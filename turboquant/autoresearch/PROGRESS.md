# TurboQuant Autonomous Research — Progress Log

**Started:** 2026-04-12
**Approach:** karpathy/autoresearch-style iteration loop

## Baseline (committed)

Gilda 3.2B, tg32, d=8192:
- F16/F16:  7.53 t/s
- TBQ4/TBQ4: 10.31 t/s (+37% vs F16) ← good
- TBQ3/TBQ3:  3.69 t/s (-51% vs F16) ← BAD
- TBQ2/TBQ2:  4.55 t/s (-40% vs F16) ← BAD

## Key Insight

**TBQ3 is slower than TBQ4 not because of a bug, but because the split ql/qh
block layout requires ~3x more SIMD instructions per 32-value block:**

- TBQ4 (half-split nibble layout): load 16B → split into 2 × 16 values → vpshufb LUT → FMA
  = ~22 instructions per block
- TBQ3 (split ql/qh layout): load 8B ql + 4B qh → 4 shift/AND + 3 blend for ql → bit extract for qh → OR + vpshufb → cvt → FMA
  = ~54 instructions per block

Memory savings at 3-bit (12B/block vs 16B/block = 1.33x less) cannot overcome
the 2.5x instruction overhead at long contexts where vec_mad dominates.

## Experiments

### exp1: AVX2 `_mm256_srlv_epi32` vec_mad_tbq2/3

Replaced scalar inner loops with AVX2 variable-shift approach:
- Load full ql (8B) + qh (4B) per block
- For each of 4 chunks (8 values), broadcast the relevant ql/qh bytes
- Apply per-lane shifts with `_mm256_srlv_epi32`
- Use `_mm256_permutevar8x32_ps` for float centroid LUT
- FMA with loaded VKQ32

Result at d=8192:
- TBQ4: 10.68 (+0.4% vs baseline 10.31)
- TBQ3: 3.71 (no change vs 3.69)
- TBQ2: 4.53 (no change vs 4.55)

**Interpretation:** AVX2 srlv reduces TBQ3 instruction count but doesn't help
throughput. The bottleneck is elsewhere:
- Register pressure (many live __m256 values)
- Data dependency chains (each chunk depends on ql/qh loads)
- Possibly memory access pattern (small 14-byte blocks don't align well with cache lines)

Status: **discard** (no improvement, keep the code for reference)

### exp2: Pre-dequantize V tile once per KV_TILE

Hypothesized: TBQ types re-dequantize V blocks 128 times per tile (once per query).
Pre-dequantize once to F32, then use fast ggml_vec_mad_f32.

Result: No change. Because use_tiled=false for TBQ types in tg (one_chunk path
is used), so this optimization doesn't apply to token generation.

Status: **discard**, reverted.

## Conclusion

**TBQ3/TBQ2 cannot be made faster than TBQ4 without fundamentally changing
their block layout.** The split bit format requires inherently more compute.

This is actually a valuable paper finding:
- TBQ4 (4-bit, nibble-packed) is the Pareto-optimal bit-width on CPU
- Lower bit-widths like TBQ3, TBQ2 save memory but not bandwidth-per-second
- The compute-bandwidth crossover is at 4-bit on modern x86

## Comprehensive Benchmark

Currently running: 3 models × 6 KV types × 4 depths × tg128
- Models: Gilda 3.2B (Llama), Qwen2.5 7B, Gemma 2 9B
- KV: F16, Q8_0, Q4_0, TBQ4, TBQ3, TBQ2
- Depths: 0, 2048, 4096, 8192
- Output: `turboquant/results/comprehensive_20260412_042410/`

Started: 2026-04-12 04:24
Expected runtime: ~2 hours (tg-only is faster than pp+tg).

## Quality Evaluation (next step)

After the comprehensive bench, run eval_quality.sh which:
- 3 models × 6 KV × 5 prompts = 90 outputs
- Uses llama-cli with --single-turn --simple-io --no-display-prompt
- Compare outputs to F16 baseline for quality degradation
- Estimated: 30-60 min
