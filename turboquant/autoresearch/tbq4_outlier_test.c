// Synthetic round-trip test: how does TBQ4 representation degrade as block
// outlier mass increases? Built standalone — links nothing, replicates the
// reference quantize/dequantize math from ggml-turboquant.c.
//
// Build: cc -O2 -Wall tbq4_outlier_test.c -o tbq4_test -lm
// Run:   ./tbq4_test
//
// Reports per-scenario:
//   - bulk RMSE (error on the small "normal" coordinates)
//   - outlier reconstruction error (magnitude restoration of the outliers)
//   - max-abs error
//
// Scenarios:
//   1. Pure Gaussian (Llama-like)
//   2. Mild outliers (1 value at 3σ, rest N(0,1))
//   3. Heavy outliers (2 values at 30σ, rest N(0,1)) — Qwen-like
//   4. Extreme outlier (1 value at 100σ, rest N(0,1))
// Plus a max-norm-based fix variant for comparison.

#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define QK_TBQ 32
#define BLOCKS 1024
#define SEED 42

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

static inline int tbq_nearest(float v, const float * b, int nb) {
    int idx = 0;
    for (int i = 0; i < nb; i++) idx += (v > b[i]);
    return idx;
}

// === Production tbq_norm: L2 of the block ===
static inline float tbq_norm_l2(const float * x, int d) {
    float s = 0.0f;
    for (int i = 0; i < d; i++) s += x[i] * x[i];
    return sqrtf(s);
}

// === Proposed fix: max-abs / centroid_max ===
static inline float tbq_norm_amax(const float * x, int d) {
    float m = 0.0f;
    for (int i = 0; i < d; i++) {
        float a = fabsf(x[i]);
        if (a > m) m = a;
    }
    return m / 0.4533823690f;
}

// Quantize+dequantize one 32-block, return reconstructed values
typedef float (*norm_fn)(const float *, int);

static void tbq4_roundtrip(const float * x, float * y, norm_fn norm) {
    float n = norm(x, QK_TBQ);
    if (n < 1e-10f) { memset(y, 0, sizeof(float)*QK_TBQ); return; }
    float inv = 1.0f / n;
    for (int j = 0; j < QK_TBQ; j++) {
        int idx = tbq_nearest(x[j] * inv, tbq_boundaries_4bit, 15);
        y[j] = tbq_centroids_4bit[idx] * n;
    }
}

// Box-Muller standard normal
static double next_normal() {
    static int has_spare = 0;
    static double spare;
    if (has_spare) { has_spare = 0; return spare; }
    double u, v, s;
    do {
        u = 2.0 * rand() / RAND_MAX - 1.0;
        v = 2.0 * rand() / RAND_MAX - 1.0;
        s = u*u + v*v;
    } while (s >= 1.0 || s == 0.0);
    s = sqrt(-2.0 * log(s) / s);
    has_spare = 1;
    spare = v * s;
    return u * s;
}

typedef struct {
    const char * name;
    int n_outliers;
    float outlier_sigma;
} Scenario;

static void run_scenario(const Scenario * sc, norm_fn norm, const char * norm_name) {
    srand(SEED);
    double bulk_sse = 0.0;
    double bulk_count = 0.0;
    double outlier_sse = 0.0;
    double outlier_orig_mag2 = 0.0;
    double outlier_count = 0.0;
    double max_abs_err = 0.0;
    int outlier_clipped = 0;

    for (int b = 0; b < BLOCKS; b++) {
        float x[QK_TBQ], y[QK_TBQ];
        // bulk
        for (int j = 0; j < QK_TBQ; j++) x[j] = (float)next_normal();
        // inject outliers at random positions
        int outlier_pos[8] = {0};
        for (int k = 0; k < sc->n_outliers && k < 8; k++) {
            int p = rand() % QK_TBQ;
            outlier_pos[k] = p;
            float sgn = (rand() & 1) ? 1.0f : -1.0f;
            x[p] = sgn * sc->outlier_sigma;
        }

        tbq4_roundtrip(x, y, norm);

        // Score
        for (int j = 0; j < QK_TBQ; j++) {
            int is_outlier = 0;
            for (int k = 0; k < sc->n_outliers; k++)
                if (outlier_pos[k] == j) { is_outlier = 1; break; }
            float err = y[j] - x[j];
            float abserr = fabsf(err);
            if (abserr > max_abs_err) max_abs_err = abserr;
            if (is_outlier) {
                outlier_sse += err*err;
                outlier_orig_mag2 += x[j]*x[j];
                outlier_count += 1.0;
                if (fabsf(y[j]) < fabsf(x[j]) * 0.7f) outlier_clipped++;
            } else {
                bulk_sse += err*err;
                bulk_count += 1.0;
            }
        }
    }

    double bulk_rmse = sqrt(bulk_sse / bulk_count);
    double outlier_rmse = (outlier_count > 0) ? sqrt(outlier_sse / outlier_count) : 0.0;
    double outlier_orig_rms = (outlier_count > 0) ? sqrt(outlier_orig_mag2 / outlier_count) : 0.0;
    double outlier_clip_pct = (outlier_count > 0) ? 100.0 * outlier_clipped / outlier_count : 0.0;

    printf("[%-12s | %-10s] bulk_rmse=%.4f  out_rmse=%.4f  out_orig_rms=%.4f  clip%%=%5.1f  maxerr=%.4f\n",
           sc->name, norm_name,
           bulk_rmse, outlier_rmse, outlier_orig_rms, outlier_clip_pct, max_abs_err);
}

int main(void) {
    Scenario scenarios[] = {
        {"pure_gauss",   0,  0.0f},
        {"mild_3sig",    1,  3.0f},
        {"qwen_like_30", 2, 30.0f},   // Qwen anchor-token-ish
        {"extreme_100",  1, 100.0f},
    };

    printf("\n=== TBQ4 round-trip: production L2-norm vs amax-norm fix ===\n");
    printf("Block size = %d, %d blocks per scenario\n\n", QK_TBQ, BLOCKS);

    for (size_t i = 0; i < sizeof(scenarios)/sizeof(scenarios[0]); i++) {
        run_scenario(&scenarios[i], tbq_norm_l2,   "L2");
        run_scenario(&scenarios[i], tbq_norm_amax, "amax");
        printf("\n");
    }
    return 0;
}
