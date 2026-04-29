// TurboQuant KV cache quantization — fast CPU implementation
//
// Uses non-uniform scalar quantization with optimal Lloyd centroids.
// No rotation (WHT removed for CPU performance). The per-block norm
// handles scale; centroids are near-optimal for Gaussian-like KV values.
// vec_dot uses integer centroid LUT for Q4_0-competitive throughput.
//
// Based on: arXiv:2504.19874 (TurboQuant, ICLR 2026)

#define GGML_COMMON_IMPL_C
#include "ggml-common.h"

#include "ggml-turboquant.h"
#include "ggml-impl.h"

#include <math.h>
#include <string.h>
#include <assert.h>

#define UNUSED GGML_UNUSED

// ---------------------------------------------------------------------------
// Nearest centroid — branchless sum of comparisons (auto-vectorizable)
// ---------------------------------------------------------------------------
static inline int tbq_nearest(float v, const float * b, int nb) {
    int idx = 0;
    for (int i = 0; i < nb; i++)
        idx += (v > b[i]);
    return idx;
}

// ---------------------------------------------------------------------------
// Per-block scale.
//
// Original TurboQuant uses a Walsh-Hadamard rotation to gaussianize the data,
// then an L2-norm scale paired with Lloyd-Max-on-unit-sphere centroids. The
// CPU port dropped the WHT for speed, so the Gaussian assumption is violated
// by heavy-tailed K caches (e.g. Qwen 2.5's anchor-token outlier channels).
// In those blocks the L2 norm is dominated by 1-2 large values, which (a)
// clips the outliers to ~64% of their magnitude and (b) inflates the bulk
// reconstruction by 1.5-6x. The amax-based scale keeps the largest |x| at
// exactly the top centroid, preserving outliers with only a modest bulk-RMSE
// cost on Gaussian blocks. See autoresearch/tbq4_outlier_test.c.
//
// TBQ2/TBQ3 still use the L2 path; only TBQ4 is patched.
// ---------------------------------------------------------------------------
static inline float tbq_norm(const float * x, int d) {
    float s = 0.0f;
    for (int i = 0; i < d; i++) s += x[i] * x[i];
    return sqrtf(s);
}

static inline float tbq_norm_amax(const float * x, int d, float cmax) {
    float m = 0.0f;
    for (int i = 0; i < d; i++) {
        float a = fabsf(x[i]);
        if (a > m) m = a;
    }
    return m / cmax;
}

// ---------------------------------------------------------------------------
// 2-bit pack/unpack (4 values per byte)
// ---------------------------------------------------------------------------
static inline void tbq_pack2(uint8_t * qs, int idx, int val) {
    int bi = idx >> 2, bo = (idx & 3) << 1;
    qs[bi] = (qs[bi] & ~(0x3 << bo)) | ((val & 0x3) << bo);
}
static inline int tbq_unpack2(const uint8_t * qs, int idx) {
    return (qs[idx >> 2] >> ((idx & 3) << 1)) & 0x3;
}

// ---------------------------------------------------------------------------
// 3-bit pack/unpack (continuous bit stream)
// ---------------------------------------------------------------------------
static inline void tbq_pack3(uint8_t * qs, int idx, int val) {
    int bo = idx * 3, bi = bo >> 3, bs = bo & 7;
    qs[bi] = (qs[bi] & ~(0x7 << bs)) | ((val & 0x7) << bs);
    if (bs > 5) {
        int lo = 8 - bs;
        qs[bi + 1] = (qs[bi + 1] & ~(0x7 >> lo)) | ((val & 0x7) >> lo);
    }
}
static inline int tbq_unpack3(const uint8_t * qs, int idx) {
    int bo = idx * 3, bi = bo >> 3, bs = bo & 7;
    int v = qs[bi] >> bs;
    if (bs > 5) v |= qs[bi + 1] << (8 - bs);
    return v & 0x7;
}

// ---------------------------------------------------------------------------
// 4-bit pack/unpack (2 values per byte)
// ---------------------------------------------------------------------------
static inline void tbq_pack4(uint8_t * qs, int idx, int val) {
    int bi = idx >> 1, bo = (idx & 1) << 2;
    qs[bi] = (qs[bi] & ~(0xF << bo)) | ((val & 0xF) << bo);
}
static inline int tbq_unpack4(const uint8_t * qs, int idx) {
    return (qs[idx >> 1] >> ((idx & 1) << 2)) & 0xF;
}

// ===========================================================================
//  Quantize — normalize, find nearest centroid, pack
// ===========================================================================

void quantize_row_tbq2_ref(const float * GGML_RESTRICT x, block_tbq2 * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        const float * src = x + i * QK_TBQ;
        float norm = tbq_norm(src, QK_TBQ);
        y[i].d = GGML_FP32_TO_FP16(norm);
        memset(y[i].qs, 0, sizeof(y[i].qs));
        if (norm < 1e-10f) continue;
        float inv = 1.0f / norm;
        for (int j = 0; j < QK_TBQ; j++)
            tbq_pack2(y[i].qs, j, tbq_nearest(src[j] * inv, tbq_boundaries_2bit, 3));
    }
}

void quantize_row_tbq3_ref(const float * GGML_RESTRICT x, block_tbq3 * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        const float * src = x + i * QK_TBQ;
        float norm = tbq_norm(src, QK_TBQ);
        y[i].d = GGML_FP32_TO_FP16(norm);
        memset(y[i].ql, 0, sizeof(y[i].ql));
        memset(y[i].qh, 0, sizeof(y[i].qh));
        if (norm < 1e-10f) continue;
        float inv = 1.0f / norm;
        for (int j = 0; j < QK_TBQ; j++) {
            int idx = tbq_nearest(src[j] * inv, tbq_boundaries_3bit, 7);
            // Store low 2 bits in ql (4 values per byte)
            int bi = j >> 2, bo = (j & 3) << 1;
            y[i].ql[bi] |= (idx & 0x3) << bo;
            // Store high bit in qh (8 values per byte)
            y[i].qh[j >> 3] |= ((idx >> 2) & 1) << (j & 7);
        }
    }
}

void quantize_row_tbq4_ref(const float * GGML_RESTRICT x, block_tbq4 * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        const float * src = x + i * QK_TBQ;
        float norm = tbq_norm_amax(src, QK_TBQ, tbq_centroids_4bit[15]);
        y[i].d = GGML_FP32_TO_FP16(norm);
        memset(y[i].qs, 0, sizeof(y[i].qs));
        if (norm < 1e-10f) continue;
        float inv = 1.0f / norm;
        // Q4_0-style half-split packing: first half in low nibbles, second half in high nibbles
        // This matches the AVX2 vpshufb unpack order used in vec_dot
        for (int j = 0; j < QK_TBQ / 2; j++) {
            int idx0 = tbq_nearest(src[j]              * inv, tbq_boundaries_4bit, 15);
            int idx1 = tbq_nearest(src[j + QK_TBQ / 2] * inv, tbq_boundaries_4bit, 15);
            y[i].qs[j] = (uint8_t)((idx0 & 0xF) | ((idx1 & 0xF) << 4));
        }
    }
}

// ===========================================================================
//  Dequantize — unpack centroid, scale by norm
// ===========================================================================

void dequantize_row_tbq2(const block_tbq2 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        float norm = GGML_FP16_TO_FP32(x[i].d);
        float * out = y + i * QK_TBQ;
        for (int j = 0; j < QK_TBQ; j++)
            out[j] = tbq_centroids_2bit[tbq_unpack2(x[i].qs, j)] * norm;
    }
}

void dequantize_row_tbq3(const block_tbq3 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        float norm = GGML_FP16_TO_FP32(x[i].d);
        float * out = y + i * QK_TBQ;
        for (int j = 0; j < QK_TBQ; j++) {
            int lo = (x[i].ql[j >> 2] >> ((j & 3) << 1)) & 0x3;
            int hi = (x[i].qh[j >> 3] >> (j & 7)) & 1;
            out[j] = tbq_centroids_3bit[lo | (hi << 2)] * norm;
        }
    }
}

void dequantize_row_tbq4(const block_tbq4 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k) {
    assert(k % QK_TBQ == 0);
    const int nb = k / QK_TBQ;
    for (int i = 0; i < nb; i++) {
        float norm = GGML_FP16_TO_FP32(x[i].d);
        float * out = y + i * QK_TBQ;
        // Q4_0-style half-split: low nibble = first half, high nibble = second half
        for (int j = 0; j < QK_TBQ / 2; j++) {
            out[j]              = tbq_centroids_4bit[x[i].qs[j] & 0xF] * norm;
            out[j + QK_TBQ / 2] = tbq_centroids_4bit[x[i].qs[j] >> 4]  * norm;
        }
    }
}

// CPU quantize_row wrappers and vec_dot are in ggml-cpu/quants.c (scalar)
// and ggml-cpu/arch/x86/quants.c (AVX2 SIMD). They are NOT in ggml-base
// because ggml-base is compiled without -march=native (no SIMD flags).
