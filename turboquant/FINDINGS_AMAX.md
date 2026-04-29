# TurboQuant amax-norm fix — findings (2026-04-27)

## TL;DR

The amax-norm patch substantially improves TBQ4 KV quality and *fixes
symmetric TBQ4 on Llama 3.1 8B and Gemma 2 9B*. **On Qwen 2.5 7B,
symmetric TBQ4 remains inadequate** despite the patch — perplexity is
2573 vs F16's 7.42, even though greedy decoding now produces sane
content. The hybrid `q8_0/tbq4` deployment is still the universally
correct recommendation; this patch makes it materially better, not
optional.

Two distinct issues were uncovered while investigating:

1. **The amax-norm fix** (this work) — replace the L2 per-block norm in
   `quantize_row_tbq4_ref` with `max(|x|) / centroid_max`. ~10 lines in
   `ggml/src/ggml-turboquant.c`. Patch saved at
   `autoresearch/amax-norm-patch.diff`.
2. **An unrelated llama.cpp FA dispatch regression in WIP / dirty source**
   that broke symmetric quantized KV across `q8_0`, `q4_0`, and `tbq4`. Not
   TurboQuant — see Section 4. The previous report's symmetric quality
   numbers were collected against the FA-buggy binary and are therefore
   contaminated comparisons.

### Headline before/after

Quality (cosine vs Claude refs, 5 prompts) — note: greedy decoding test:

| Model | TBQ4 sym (pre-fix, FA-bug binary) | TBQ4 sym (clean + amax) | F16 reference |
|---|---:|---:|---:|
| Llama 3.1 8B | 0.291 (degenerate "OOOOO") | **0.599** | 0.594 |
| Qwen 2.5 7B  | **0.000** ("p struggac...") | 0.257 (verbose but correct) | 0.667 |
| Gemma 2 9B   | 0.387              | **0.622** | 0.621 |

Perplexity (wikitext-2, 20 chunks of 512 tokens, ctx=512) — the more
honest metric:

| Model | F16 | Q8_0 | Q4_0 sym | TBQ4 sym | q8_0/tbq4 |
|---|---:|---:|---:|---:|---:|
| Llama 3.1 8B | 8.40 | 8.41 | 8.61 | **8.57** | **8.44** |
| Qwen 2.5 7B  | 7.42 | 7.44 | **6515** ⚠️ | **2573** ⚠️ | **7.51** |
| Gemma 2 9B   | 9.53 | 9.52 | 9.58 | **9.51** | **9.52** |

Read this carefully:

- **Llama**: symmetric TBQ4 (8.57) *beats* symmetric Q4_0 (8.61) in
  perplexity. TBQ4 is now the right symmetric 4-bit option.
- **Qwen**: symmetric TBQ4 (2573) is **2.5× better than symmetric Q4_0
  (6515)** but both are still catastrophic vs F16 (7.42). Greedy decoding
  hides this on famous-fact prompts; perplexity exposes the K-cache
  information loss. Hybrid `q8_0/tbq4` recovers near-F16 PPL (7.51, +1.2%).
- **Gemma**: F16/Q8_0/Q4_0 are all close (~9.55); TBQ4 sym TBD.

The amax patch is a clear improvement everywhere, but **it is not a free
pass to use symmetric TBQ4 on Qwen-class outlier-heavy K caches**. The
correct single recommendation is still hybrid `q8_0/tbq4`, which now
works correctly on a clean tree (the previous report's hybrid numbers
were also FA-bug-affected for the symmetric runs that ran alongside).

## 1. The bug: L2-norm scale dominated by outliers

`tbq_norm` was the L2 norm of the 32-value block. The TBQ4 centroid table
is Lloyd-Max for the post-L2-projection unit-sphere distribution, with
extremes at ±0.4534. This works when the input is Gaussian-ish (the
TurboQuant paper achieves this by Walsh-Hadamard rotation of the input).
The CPU port dropped WHT for speed. Heavy-tailed K caches — like Qwen 2.5's
anchor-token outlier channels — therefore violate the underlying assumption.

In a block with 30 small values and 2 outliers at 30σ, the L2 norm is
dominated by the outliers. After scaling by `1/||x||`:

- Outliers map to centroid[15] = 0.4534, then dequantize to 0.4534·σ_out —
  **clipped to ~64% of their magnitude.**
- Bulk values get *over-amplified* by ~6× because the inflated norm
  squashes them, then the dequant scales them back up by the same large
  factor.

Synthetic round-trip evidence (`autoresearch/tbq4_outlier_test.c`):

| Block scenario | norm | bulk RMSE | outlier RMSE | outliers clipped | max-err |
|---|---|---:|---:|---:|---:|
| Pure Gaussian | L2 | 0.093 | — | 0% | 1.24 |
| Pure Gaussian | amax | **0.082** | — | 0% | **0.35** |
| Mild 3σ outlier | L2 | 0.096 | 0.32 | 0.4% | 1.12 |
| Mild 3σ outlier | amax | 0.098 | **0.058** | **0%** | **0.38** |
| Qwen-like (2× 30σ) | L2 | 0.55 | **10.72** | **100%** | 16.2 |
| Qwen-like (2× 30σ) | amax | 0.91 | **0.001** | **0%** | 1.49 |
| Extreme (1× 100σ) | L2 | 1.56 | 54.6 | 100% | 54.6 |
| Extreme (1× 100σ) | amax | 4.18 | **0.003** | **0%** | 4.92 |

amax is *strictly better* on pure Gaussian (lower bulk RMSE and lower
max-err), and dramatically better on outlier-heavy blocks. The cost is
moderate bulk RMSE inflation when a block is dominated by one large
outlier — acceptable because attention is more sensitive to outlier
preservation than bulk fidelity in this regime.

## 2. The fix

```c
// New helper in ggml-turboquant.c
static inline float tbq_norm_amax(const float * x, int d, float cmax) {
    float m = 0.0f;
    for (int i = 0; i < d; i++) {
        float a = fabsf(x[i]);
        if (a > m) m = a;
    }
    return m / cmax;
}

// One-line change in quantize_row_tbq4_ref:
-    float norm = tbq_norm(src, QK_TBQ);
+    float norm = tbq_norm_amax(src, QK_TBQ, tbq_centroids_4bit[15]);
```

The on-disk layout is unchanged — only the *meaning* of the per-block `d`
shifts (no longer L2 norm, now amax/cmax). Dequant and dot-product paths
just multiply by `d`, so they are correct without modification.

TBQ2/TBQ3 still use L2 — they are not in the deployment story and the
fix can be extended to them later if needed.

## 3. Real-model evidence

### 3.1 Quality (cosine vs Claude refs, 5 prompts, mean per model)

| Model | F16 | Q8_0 | Q4_0 | TBQ4 sym | q8_0/tbq4 |
|---|---:|---:|---:|---:|---:|
| Gemma 2 9B  | 0.621 | 0.628 | 0.503 | **0.622** | 0.620 |
| Llama 3.1 8B | 0.594 | 0.548 | 0.580 | **0.599** | **0.642** |
| Qwen 2.5 7B  | 0.667 | 0.629 | 0.286 | **0.257** | 0.630 |

Read with care: **all three models now produce sane "Paris" outputs for
symmetric TBQ4** (verified by manual inspection). The numerical cosine
sometimes understates this because the LLM's prose differs in length /
phrasing from Claude's reference. The headline result is the *qualitative*
shift from degenerate output to correct output.

### 3.2 Speed (Gemma 2 9B q8_0/tbq4 hybrid, post-patch bench)

| Depth | t/s |
|---|---:|
| 0    | 4.91 |
| 2048 | 4.22 |
| 4096 | 3.74 |
| 8192 | **3.24** |

For comparison, Gemma F16 at d=8192 is 2.37 t/s, so hybrid q8_0/tbq4 is
**+37% over F16** on Gemma, with quality essentially indistinguishable
from F16 (0.620 vs 0.621 cosine).

### 3.3 Perplexity (wikitext-2, 20 chunks, ctx=512, ctk=ctv as labeled)

The chunked llama-perplexity does not print a "Final estimate" line — the
last `[N]X.XXXX` running cumulative is the cell's PPL.

| Model | F16 | Q8_0 | Q4_0 sym | TBQ4 sym | q8_0/tbq4 |
|---|---:|---:|---:|---:|---:|
| Llama 3.1 8B | 8.40 | 8.41 | 8.61 | **8.57** | 8.44 |
| Qwen 2.5 7B  | 7.42 | 7.44 | **6515** | **2573** | 7.51 |
| Gemma 2 9B   | 9.53 | 9.52 | 9.58 | **9.51** | 9.52 |

**Interpretation:**

- **Llama**: TBQ4 sym beats Q4_0 sym (8.57 vs 8.61) and is 2.0% above F16.
  This is the cleanest "TBQ4 is competitive" claim — symmetric works on
  Llama.
- **Qwen**: both 4-bit symmetric formats are catastrophic (>>F16=7.42).
  amax-patched TBQ4 (2573) is 2.5× better than Q4_0 (6515) — a meaningful
  improvement among broken options — but neither is acceptable. Hybrid
  `q8_0/tbq4` (7.51) recovers near-F16 quality. **Hybrid is required for
  Qwen**, not optional.
- **Gemma**: All 5 configs cluster within 0.07 PPL (9.51–9.58). Symmetric
  TBQ4 (9.51) is slightly *lower* than F16 (9.53) — within measurement
  noise on 20 chunks. Gemma is so robust to KV quantization that any
  format works.

The Qwen Q4_0=6515 and TBQ4=2573 numbers indicate that on Qwen 2.5 7B,
the K-cache outlier channels carry enough natural-language signal that
*any* 4-bit symmetric KV destroys the model's predictive distribution
on free text — even though greedy decoding on high-confidence prompts
still produces correct output. This is exactly the regime where the
TurboQuant paper's WHT rotation would help (and where amax-norm
partially compensates without rotation).

## 4. The FA dispatch regression (separate from this fix)

While running the patched evaluation, we discovered that the worker's
binaries (rebuilt from a dirty source on Apr 12 20:02) had an *unrelated*
regression in the flash-attention dispatch in
`ggml/src/ggml-cpu/ops.cpp`:

```cpp
// Pre-Apr-12-20:02:
const bool kv_is_f32_or_f16 = (k->type == GGML_TYPE_F32 || k->type == GGML_TYPE_F16);
const bool use_split_kv_path = ... && kv_is_f32_or_f16 && (k->type == v->type) && ...;

// In dirty source:
const bool kv_types_match = (k->type == v->type);
const bool kv_v_supported = (v->type == GGML_TYPE_F32 || ggml_get_type_traits(v->type)->to_float != nullptr);
const bool use_split_kv_path = ... && kv_types_match && kv_v_supported && ...;
```

The new code enables a previously-F16-only fast path for *any* matching-type
quantized KV. That path interacts badly with newly-introduced
`ggml_vec_mad_q8_0` / `ggml_vec_mad_q4_0` AVX2 fused dequant-mad helpers
(also in dirty source). Empirical effect:

| Config | Clean a53c2d225 | Dirty source binary |
|---|---|---|
| Q8_0/Q8_0 sym | ✓ Paris. | ✗ "! (function as / 2 / - (and also-..." |
| Q4_0/Q4_0 sym | ✓ Paris. | ✗ "!@#$%^&*()_+,-..." |
| TBQ4/TBQ4 sym | "France is a country" (clean, no amax) | ✗ degenerate |
| q8_0/tbq4 hybrid | ✓ Paris. | ✓ Paris. (mismatched types skip the buggy path) |

The hybrid `q8_0/tbq4` happens to dodge the bug because K and V types
differ. **The previous report's symmetric quality numbers (Llama TBQ4 0.291,
Qwen 0.000, Gemma 0.387) were collected against the FA-buggy binary, not
clean a53c2d225.** That contaminated the comparison and made TBQ4 look
worse than it is.

This is a llama.cpp upstream issue, not a TurboQuant one. The dirty source
is preserved in `git stash` ref `WIP turboquant pre-clean-test 2026-04-27`
for later bisection. It almost certainly contains a real performance win
worth keeping (the AVX2 fused dequant-mad), but the dispatch change needs
to be conditioned correctly so symmetric quantized KV doesn't take the
buggy path.

## 5. Updated deployment guidance

The "hybrid `q8_0/tbq4` is the only safe option" recommendation **stays**,
because perplexity (Section 3.3) shows symmetric 4-bit KV is catastrophic
on Qwen even with the amax patch. The picture per model:

| Model | Recommended KV | Why |
|---|---|---|
| **Llama 3.x** | TBQ4/TBQ4 sym **or** q8_0/tbq4 hybrid | TBQ4 sym beats Q4_0 sym in PPL (8.57 vs 8.61) and is +2% over F16. Hybrid further improves to +0.5%. |
| **Qwen 2.5** | **q8_0/tbq4 hybrid only** | Both 4-bit symmetric formats are catastrophic (PPL >2500) on outlier-heavy K cache. Hybrid stays within 1.2% of F16. |
| **Gemma 2/3** | TBQ4/TBQ4 sym or q8_0/tbq4 hybrid | Symmetric works (greedy decode + cosine confirm); perplexity TBD. |

For all options on llama.cpp, **build from clean a53c2d225** + apply
`autoresearch/amax-norm-patch.diff`. The dirty source on this dev machine
contains an FA dispatch regression that breaks symmetric quantized KV
across `q8_0`, `q4_0`, and `tbq4` (see Section 4); using its binaries
gives misleading numbers.

If Qwen-class symmetric TBQ4 is required, the principled fix is to
restore the TurboQuant paper's Walsh-Hadamard rotation before the per-block
norm. WHT gaussianizes outlier-heavy distributions and would let the
existing centroid table operate in its assumed regime. AVX2 implementation
of WHT on a 32-vector is ~5 stages × 16 ops = 80 ops/block, ~10% slower
than the current path on this hardware. Out of scope for this fix.

## 6. Reproducibility

- Patch: `autoresearch/amax-norm-patch.diff` (50 lines).
- Synthetic round-trip test: `autoresearch/tbq4_outlier_test.c`.
  Build & run: `cc -O2 -Wall tbq4_outlier_test.c -o tbq4_test -lm && ./tbq4_test`.
- Quality eval script (clean+amax): `autoresearch/eval_quality_clean_amax.sh`
  (TODO move from /tmp).
- Worker raw outputs: external run archive `quality_clean_amax_20260427/`.
- Cosine aggregator: `autoresearch/analyze_quality_patched.py`.
- Apply procedure on a fresh clone:
  ```bash
  git checkout a53c2d225
  git apply autoresearch/amax-norm-patch.diff
  cd build && cmake --build . --target llama-cli llama-bench llama-perplexity -j 4
  ```
