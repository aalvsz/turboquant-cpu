# Gemma 4 E4B CPU Decode Findings

**Date:** 2026-04-30

**CPU:** Intel Core i5-12500 class x86 CPU, AVX2/AVX-VNNI capable

**Model:** Gemma 4 E4B IT, Q4_0 GGUF

**Benchmark:** `llama-bench`, CPU only, 6 threads, flash attention enabled,
`n_prompt=0`, `n_gen=16`, `repetitions=2`

This note records the local Gemma 4 E4B CPU investigation after adding scoped
Gemma 4 support to the bundled `llama.cpp` tree and optimizing the TurboQuant
decode path. Raw benchmark CSV files are intentionally not checked in because
they include local absolute model paths. The sanitized summary is stored in
`results/gemma4_e4b_cpu_summary.csv`.

## Summary

The useful TurboQuant speedup appears at longer KV depths. At shallow depth,
TBQ4 is neutral to slightly slower than F16/Q8. Once the KV cache is large
enough for attention bandwidth and cache traversal to matter, TBQ4 becomes the
fastest tested symmetric KV cache type.

At 8192 KV depth:

- `f16/f16`: 7.071 tok/s
- `q8_0/q8_0`: 8.575 tok/s
- `q4_0/q4_0`: 7.880 tok/s
- `tbq4/tbq4`: 9.193 tok/s

That makes `tbq4/tbq4`:

- 30.0% faster than F16
- 7.2% faster than Q8
- 16.7% faster than Q4_0

## Results

Throughput is decode tokens per second.

| KV depth | F16/F16 | Q8_0/Q8_0 | Q4_0/Q4_0 | TBQ4/TBQ4 | TBQ4 vs F16 | TBQ4 vs Q8 | TBQ4 vs Q4 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 10.041 | 10.026 | n/a | 9.908 | -1.3% | -1.2% | n/a |
| 512 | 9.785 | 9.756 | n/a | 9.783 | -0.0% | +0.3% | n/a |
| 2048 | 9.248 | 9.512 | 8.961 | 9.668 | +4.5% | +1.6% | +7.9% |
| 4096 | 8.681 | 9.161 | 8.552 | 9.536 | +9.8% | +4.1% | +11.5% |
| 8192 | 7.071 | 8.575 | 7.880 | 9.193 | +30.0% | +7.2% | +16.7% |

## What Changed

The speedup was not obtained by only trying different K/V quantization schemes.
Two implementation changes mattered:

1. Quantized KV cache types were allowed into the split-KV decode path when the
   type has a CPU vector-dot implementation and a query conversion path. Before
   this, quantized KV decode was under-parallelized at long depth.

2. TBQ4 V-cache accumulation gained an AVX2 fused path that avoids building an
   intermediate F32 dequantization buffer in the hot flash-attention loop.

The final TBQ4 AVX2 V path uses the existing int8 centroid approximation also
used by the TBQ4 K-dot path. Exact float-centroid gather and higher-precision
int16-centroid shuffle variants were tested, but both were slower and did not
preserve the long-depth advantage over Q8.

## Negative Results

- `q4_0/q4_0` was measured after the first summary because it had already been
  trailing in earlier runs. The final measurement confirmed it is not
  competitive on this Gemma 4 E4B CPU setup.
- 12 threads were slower than 6 threads on this CPU for the tested decode setup.
- TBQ4 does not help at depth 0 and is effectively neutral at depth 512.
- Exact float-centroid V accumulation is cleaner semantically, but too slow on
  this AVX2 path because gathers dominate the small per-block workload.

## Caveats

These are speed findings, not a full quality/perplexity endorsement. The
optimized TBQ4 V path is approximate in the same style as the existing TBQ4
K-dot path, so quality should be validated before treating symmetric
`tbq4/tbq4` as a general default. For quality-sensitive usage, the earlier
hybrid recommendation `q8_0/tbq4` remains worth testing per model.

## Reproduction Template

Use a local Gemma 4 E4B IT GGUF path in place of `/path/to/model.gguf`:

```bash
./llama.cpp/build/bin/llama-bench \
  -m /path/to/model.gguf \
  -t 6 \
  -p 0 \
  -n 16 \
  -d 2048,4096,8192 \
  -r 2 \
  -ctk tbq4 \
  -ctv tbq4 \
  -fa 1
```
