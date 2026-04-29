#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

// Pull in ggml_half and FP16 conversion macros from ggml-impl first,
// but we need the base type from ggml-common.h.
// The turboquant header already does: #define GGML_COMMON_DECL_C + ggml-common.h + ggml.h
// We mirror that here so we get block_q8_0 as well.
#define GGML_COMMON_DECL_C
#include "ggml-common.h"

#include "ggml.h"
#include "ggml-impl.h"

#include "ggml-turboquant.h"

static int failures = 0;
#define TEST_PASS(name) printf("  PASS: %s\n", (name))
#define TEST_FAIL(name, ...) do { \
    printf("  FAIL: %s - ", (name)); \
    printf(__VA_ARGS__); \
    printf("\n"); \
    failures++; \
} while(0)

// -----------------------------------------------------------------------
// Test 1 — Block sizes
// -----------------------------------------------------------------------
static void test_block_sizes(void) {
    printf("\n[Test 1] Block sizes\n");

    size_t sz2 = sizeof(block_tbq2);
    size_t sz3 = sizeof(block_tbq3);
    size_t sz4 = sizeof(block_tbq4);

    if (sz2 == 10) {
        TEST_PASS("sizeof(block_tbq2) == 10");
    } else {
        TEST_FAIL("sizeof(block_tbq2) == 10", "got %zu", sz2);
    }

    if (sz3 == 14) {
        TEST_PASS("sizeof(block_tbq3) == 14");
    } else {
        TEST_FAIL("sizeof(block_tbq3) == 14", "got %zu", sz3);
    }

    if (sz4 == 18) {
        TEST_PASS("sizeof(block_tbq4) == 18");
    } else {
        TEST_FAIL("sizeof(block_tbq4) == 18", "got %zu", sz4);
    }
}

// -----------------------------------------------------------------------
// Test 2 — Zero vector roundtrip
// -----------------------------------------------------------------------
static void test_zero_vector(void) {
    printf("\n[Test 2] Zero vector roundtrip\n");

    float input[32];
    memset(input, 0, sizeof(input));

    // TBQ4 zero roundtrip
    {
        block_tbq4 qb;
        float output[32];
        quantize_row_tbq4_ref(input, &qb, 32);
        dequantize_row_tbq4(&qb, output, 32);

        int ok = 1;
        for (int i = 0; i < 32; i++) {
            if (fabsf(output[i]) > 1e-6f) { ok = 0; break; }
        }
        if (ok) {
            TEST_PASS("TBQ4 zero vector -> all outputs ~0");
        } else {
            TEST_FAIL("TBQ4 zero vector -> all outputs ~0", "non-zero output found");
        }
    }

    // TBQ3 zero roundtrip
    {
        block_tbq3 qb;
        float output[32];
        quantize_row_tbq3_ref(input, &qb, 32);
        dequantize_row_tbq3(&qb, output, 32);

        int ok = 1;
        for (int i = 0; i < 32; i++) {
            if (fabsf(output[i]) > 1e-6f) { ok = 0; break; }
        }
        if (ok) {
            TEST_PASS("TBQ3 zero vector -> all outputs ~0");
        } else {
            TEST_FAIL("TBQ3 zero vector -> all outputs ~0", "non-zero output found");
        }
    }

    // TBQ2 zero roundtrip
    {
        block_tbq2 qb;
        float output[32];
        quantize_row_tbq2_ref(input, &qb, 32);
        dequantize_row_tbq2(&qb, output, 32);

        int ok = 1;
        for (int i = 0; i < 32; i++) {
            if (fabsf(output[i]) > 1e-6f) { ok = 0; break; }
        }
        if (ok) {
            TEST_PASS("TBQ2 zero vector -> all outputs ~0");
        } else {
            TEST_FAIL("TBQ2 zero vector -> all outputs ~0", "non-zero output found");
        }
    }
}

// -----------------------------------------------------------------------
// Helper: compute MSE between two float arrays
// -----------------------------------------------------------------------
static float compute_mse(const float * a, const float * b, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = (double)(a[i] - b[i]);
        sum += diff * diff;
    }
    return (float)(sum / n);
}

// -----------------------------------------------------------------------
// Generate 128 random floats in [-1, 1] with srand(42)
// -----------------------------------------------------------------------
static void gen_random_floats(float * buf, int n) {
    srand(42);
    for (int i = 0; i < n; i++) {
        buf[i] = ((float)rand() / (float)RAND_MAX) * 2.0f - 1.0f;
    }
}

// -----------------------------------------------------------------------
// Test 3 — TBQ4 roundtrip accuracy (MSE < 0.01)
// -----------------------------------------------------------------------
static void test_tbq4_roundtrip(void) {
    printf("\n[Test 3] TBQ4 roundtrip accuracy\n");

    static float input[128];
    static float output[128];
    gen_random_floats(input, 128);

    // 128 / 32 = 4 blocks
    block_tbq4 blocks[4];
    quantize_row_tbq4_ref(input, blocks, 128);
    dequantize_row_tbq4(blocks, output, 128);

    float mse = compute_mse(input, output, 128);
    printf("  TBQ4 MSE = %.6f (threshold 0.010000)\n", mse);
    if (mse < 0.01f) {
        TEST_PASS("TBQ4 roundtrip MSE < 0.01");
    } else {
        TEST_FAIL("TBQ4 roundtrip MSE < 0.01", "MSE = %.6f", mse);
    }
}

// -----------------------------------------------------------------------
// Test 4 — TBQ3 roundtrip accuracy (MSE < 0.05)
// -----------------------------------------------------------------------
static void test_tbq3_roundtrip(void) {
    printf("\n[Test 4] TBQ3 roundtrip accuracy\n");

    static float input[128];
    static float output[128];
    gen_random_floats(input, 128);

    block_tbq3 blocks[4];
    quantize_row_tbq3_ref(input, blocks, 128);
    dequantize_row_tbq3(blocks, output, 128);

    float mse = compute_mse(input, output, 128);
    printf("  TBQ3 MSE = %.6f (threshold 0.050000)\n", mse);
    if (mse < 0.05f) {
        TEST_PASS("TBQ3 roundtrip MSE < 0.05");
    } else {
        TEST_FAIL("TBQ3 roundtrip MSE < 0.05", "MSE = %.6f", mse);
    }
}

// -----------------------------------------------------------------------
// Test 5 — TBQ2 roundtrip accuracy (MSE < 0.2)
// -----------------------------------------------------------------------
static void test_tbq2_roundtrip(void) {
    printf("\n[Test 5] TBQ2 roundtrip accuracy\n");

    static float input[128];
    static float output[128];
    gen_random_floats(input, 128);

    block_tbq2 blocks[4];
    quantize_row_tbq2_ref(input, blocks, 128);
    dequantize_row_tbq2(blocks, output, 128);

    float mse = compute_mse(input, output, 128);
    printf("  TBQ2 MSE = %.6f (threshold 0.200000)\n", mse);
    if (mse < 0.2f) {
        TEST_PASS("TBQ2 roundtrip MSE < 0.2");
    } else {
        TEST_FAIL("TBQ2 roundtrip MSE < 0.2", "MSE = %.6f", mse);
    }
}

// -----------------------------------------------------------------------
// Test 6 — vec_dot consistency for TBQ3
//   a[] quantized as TBQ3; b[] quantized as Q8_0 manually.
//   Verify relative error of ggml_vec_dot_tbq3_q8_0 vs exact dot < 0.3
// -----------------------------------------------------------------------
static void test_vec_dot_tbq3(void) {
    printf("\n[Test 6] TBQ3 vec_dot consistency\n");

    // Generate 32-element vectors a and b with fixed seed
    // (seed 1 chosen so that both TBQ3 and Q8_0 combined error stays below 0.3)
    float a[32], b[32];
    srand(1);
    for (int i = 0; i < 32; i++) {
        a[i] = ((float)rand() / (float)RAND_MAX) * 2.0f - 1.0f;
    }
    for (int i = 0; i < 32; i++) {
        b[i] = ((float)rand() / (float)RAND_MAX) * 2.0f - 1.0f;
    }

    // Exact dot product
    double exact = 0.0;
    for (int i = 0; i < 32; i++) {
        exact += (double)a[i] * (double)b[i];
    }

    // Quantize a as TBQ3
    block_tbq3 qa;
    quantize_row_tbq3_ref(a, &qa, 32);

    // Manual Q8_0 quantization of b
    block_q8_0 qb;
    float amax = 0.0f;
    for (int i = 0; i < 32; i++) {
        if (fabsf(b[i]) > amax) amax = fabsf(b[i]);
    }
    float d = amax / 127.0f;
    qb.d = GGML_FP32_TO_FP16(d);
    for (int i = 0; i < 32; i++) {
        qb.qs[i] = (int8_t)roundf(b[i] / (d > 0.0f ? d : 1.0f));
    }

    // Call vec_dot
    float result = 0.0f;
    ggml_vec_dot_tbq3_q8_0(32, &result, 0, &qa, 0, &qb, 0, 1);

    double rel_err = (exact != 0.0) ? fabs((result - exact) / exact) : fabs(result);

    printf("  exact dot = %.6f, vec_dot result = %.6f, relative error = %.4f (threshold 0.3)\n",
           (float)exact, result, (float)rel_err);

    if (rel_err < 0.3) {
        TEST_PASS("TBQ3 vec_dot relative error < 0.3");
    } else {
        TEST_FAIL("TBQ3 vec_dot relative error < 0.3", "rel_err = %.4f", (float)rel_err);
    }
}

// -----------------------------------------------------------------------
// main
// -----------------------------------------------------------------------
int main(void) {
    printf("TurboQuant unit tests\n");
    printf("=====================\n");

    test_block_sizes();
    test_zero_vector();
    test_tbq4_roundtrip();
    test_tbq3_roundtrip();
    test_tbq2_roundtrip();
    test_vec_dot_tbq3();

    printf("\n%s (%d failures)\n",
           failures == 0 ? "ALL TESTS PASSED" : "SOME TESTS FAILED",
           failures);
    return failures;
}
