#pragma once

#define GGML_COMMON_DECL_C
#include "ggml-common.h"

#include "ggml.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Block size for all TBQ types
#define QK_TBQ 32

// ---------------------------------------------------------------------------
// Block structures
// ---------------------------------------------------------------------------

typedef struct {
    ggml_half d;              // block L2 norm
    uint8_t   qs[QK_TBQ / 4]; // 32 x 2 bits = 8 bytes
} block_tbq2;
static_assert(sizeof(block_tbq2) == sizeof(ggml_half) + QK_TBQ / 4, "wrong tbq2 block size");

typedef struct {
    ggml_half d;              // block L2 norm
    uint8_t   ql[QK_TBQ / 4]; // low 2 bits: 32 × 2 bits = 8 bytes (4 values/byte)
    uint8_t   qh[QK_TBQ / 8]; // high bit:   32 × 1 bit  = 4 bytes (8 values/byte)
} block_tbq3;
// Split layout enables AVX2 SIMD unpack (same technique as Q3_K)
static_assert(sizeof(block_tbq3) == sizeof(ggml_half) + QK_TBQ/4 + QK_TBQ/8, "wrong tbq3 block size");

typedef struct {
    ggml_half d;              // block L2 norm
    uint8_t   qs[QK_TBQ / 2]; // 32 x 4 bits = 16 bytes
} block_tbq4;
static_assert(sizeof(block_tbq4) == sizeof(ggml_half) + QK_TBQ / 2, "wrong tbq4 block size");

// ---------------------------------------------------------------------------
// Precomputed centroids and decision boundaries from Lloyd's algorithm
// ---------------------------------------------------------------------------

static const float tbq_centroids_2bit[4] = {
    -0.2633194111f, -0.0798019294f,  0.0798019294f,  0.2633194111f
};
static const float tbq_boundaries_2bit[3] = {
    -0.1715606703f, -0.0000000000f,  0.1715606703f
};

static const float tbq_centroids_3bit[8] = {
    -0.3662683345f, -0.2324606889f, -0.1317562372f, -0.0428516655f,
     0.0428513652f,  0.1317559552f,  0.2324604435f,  0.3662681484f
};
static const float tbq_boundaries_3bit[7] = {
    -0.2993645117f, -0.1821084631f, -0.0873039514f, -0.0000001501f,
     0.0873036602f,  0.1821081994f,  0.2993642960f
};

static const float tbq_centroids_4bit[16] = {
    -0.4533823690f, -0.3498689875f, -0.2765066024f, -0.2161363211f,
    -0.1628755531f, -0.1138667127f, -0.0674132126f, -0.0223388465f,
     0.0222986460f,  0.0673736555f,  0.1138284429f,  0.1628392198f,
     0.2161025935f,  0.2764762106f,  0.3498428421f,  0.4533620310f
};
static const float tbq_boundaries_4bit[15] = {
    -0.4016256783f, -0.3131877950f, -0.2463214617f, -0.1895059371f,
    -0.1383711329f, -0.0906399627f, -0.0448760296f, -0.0000201002f,
     0.0448361508f,  0.0906010492f,  0.1383338314f,  0.1894709066f,
     0.2462894021f,  0.3131595263f,  0.4016024366f
};

// ---------------------------------------------------------------------------
// Integer centroid LUT for fast vec_dot (scaled to [-127, 127] range)
//   centroid_i8[k] = round(centroid[k] / max_abs_centroid * 127)
//   d_scale = max_abs_centroid / 127  (multiply into final result)
// ---------------------------------------------------------------------------

// 2-bit: max_abs = 0.2633194111, d_scale = 0.2633194111/127 = 0.00207338
static const int8_t tbq_centroids_i8_2bit[4] = { -127, -38, 38, 127 };
static const float  tbq_dscale_2bit = 0.00207338f;

// 3-bit: max_abs = 0.3662683345, d_scale = 0.3662683345/127 = 0.00288400
static const int8_t tbq_centroids_i8_3bit[8] = { -127, -80, -46, -15, 15, 46, 80, 127 };
static const float  tbq_dscale_3bit = 0.00288400f;

// 4-bit: max_abs = 0.4533823690, d_scale = 0.4533823690/127 = 0.00356994
static const int8_t tbq_centroids_i8_4bit[16] = {
    -127, -98, -77, -61, -46, -32, -19, -6,
       6,  19,  32,  46,  61,  77,  98, 127
};
static const float  tbq_dscale_4bit = 0.00356994f;

// ---------------------------------------------------------------------------
// Function declarations
// ---------------------------------------------------------------------------

// Reference quantization (used as from_float_ref in ggml.c type_traits)
GGML_API void quantize_row_tbq2_ref(const float * GGML_RESTRICT x, block_tbq2 * GGML_RESTRICT y, int64_t k);
GGML_API void quantize_row_tbq3_ref(const float * GGML_RESTRICT x, block_tbq3 * GGML_RESTRICT y, int64_t k);
GGML_API void quantize_row_tbq4_ref(const float * GGML_RESTRICT x, block_tbq4 * GGML_RESTRICT y, int64_t k);

// Dequantization (used as to_float in ggml.c type_traits)
GGML_API void dequantize_row_tbq2(const block_tbq2 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k);
GGML_API void dequantize_row_tbq3(const block_tbq3 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k);
GGML_API void dequantize_row_tbq4(const block_tbq4 * GGML_RESTRICT x, float * GGML_RESTRICT y, int64_t k);

// CPU quantization (used as from_float in ggml-cpu.c type_traits_cpu)
void quantize_row_tbq2(const float * GGML_RESTRICT x, void * GGML_RESTRICT y, int64_t k);
void quantize_row_tbq3(const float * GGML_RESTRICT x, void * GGML_RESTRICT y, int64_t k);
void quantize_row_tbq4(const float * GGML_RESTRICT x, void * GGML_RESTRICT y, int64_t k);

// CPU vec_dot (used as vec_dot in ggml-cpu.c type_traits_cpu)
void ggml_vec_dot_tbq2_q8_0(int n, float * GGML_RESTRICT s, size_t bs, const void * GGML_RESTRICT vx, size_t bx, const void * GGML_RESTRICT vy, size_t by, int nrc);
void ggml_vec_dot_tbq3_q8_0(int n, float * GGML_RESTRICT s, size_t bs, const void * GGML_RESTRICT vx, size_t bx, const void * GGML_RESTRICT vy, size_t by, int nrc);
void ggml_vec_dot_tbq4_q8_0(int n, float * GGML_RESTRICT s, size_t bs, const void * GGML_RESTRICT vx, size_t bx, const void * GGML_RESTRICT vy, size_t by, int nrc);

// Fused dequant-mad for flash attention V accumulation:
//   VKQ32[d] += dequant(v_data)[d] * scale,  for d = 0..n-1
// Single-pass: reads quantized V, accumulates directly into VKQ32.
// Avoids the intermediate F32 dequant buffer that the default path uses.
void ggml_vec_mad_tbq2(int n, float * GGML_RESTRICT VKQ32, const void * GGML_RESTRICT vx, float scale);
void ggml_vec_mad_tbq3(int n, float * GGML_RESTRICT VKQ32, const void * GGML_RESTRICT vx, float scale);
void ggml_vec_mad_tbq4(int n, float * GGML_RESTRICT VKQ32, const void * GGML_RESTRICT vx, float scale);

#ifdef __cplusplus
}
#endif
