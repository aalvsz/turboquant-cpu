# All Bit-Width Comparison at d=8192
# Model: Gilda 3.2B (reasoning_gilda_Q4KM.gguf), tg32, r=2
# Worker 2 (10.15.1.154), 12 threads, flash-attn on

| KV Type | tg32 @ d8192 | vs F16 | Bytes/value | Ops/value (vec_mad) |
|---|---|---|---|---|
| F16/F16 | 7.53 t/s | baseline | 2.0 | 1 (FMA) |
| TBQ4/TBQ4 | 10.31 t/s | **+36.9%** | 0.5625 | ~2 (nibble split + LUT) |
| TBQ3/TBQ3 | 3.69 t/s | **-51.0%** | 0.4375 | ~6-7 (ql/qh split + blend + LUT) |
| TBQ2/TBQ2 | (pending) | ~-50% | 0.3125 | ~4-5 (shift/mask + blend + LUT) |

# Speed at short context (tg, n=16-128, d=0)
| KV Type | tg128 | Notes |
|---|---|---|
| F16 | ~16 t/s | Normal |
| TBQ4 | ~16 t/s | Normal |
| TBQ3 | ~15.3 t/s | Normal — NOT broken |
| TBQ2 | ~15 t/s | Normal — NOT broken |

# Conclusion:
# TBQ3/TBQ2 per-token speed is NORMAL at short context.
# At deep context (d=8192), TBQ3 becomes compute-bound: the vec_mad unpacking
# overhead (6-7 ops/value) exceeds the memory bandwidth savings from smaller blocks.
# TBQ4's simple nibble layout (2 ops/value) is the Pareto-optimal sweet spot.
