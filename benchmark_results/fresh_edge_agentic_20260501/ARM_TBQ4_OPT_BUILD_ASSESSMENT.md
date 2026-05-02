# ARM TBQ4 Optimized Build Assessment

Date: 2026-05-01

## Build

New build directory:

```text
benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-opt
```

Build configuration:

- `CMAKE_BUILD_TYPE=Release`
- `GGML_NATIVE=ON`
- `GGML_METAL=OFF`
- `GGML_ACCELERATE=ON`
- `GGML_BLAS=ON`, Apple Accelerate

Implemented ARM-specific TBQ4 paths in the fresh Qwen-capable source:

- `ggml/src/ggml-cpu/arch/arm/quants.c`: NEON `ggml_vec_dot_tbq4_q8_0`
- `ggml/src/ggml-cpu/quants.c`: NEON `ggml_vec_mad_tbq4`

The previous scalar ARM wrappers for TBQ2/TBQ3 remain unchanged.

## Validation

- `llama-bench`, `llama-cli`, `llama-perplexity`, and `test-quantize-fns` built as Mach-O arm64 binaries.
- `libggml-cpu.dylib` exports `ggml_vec_dot_tbq4_q8_0` and `ggml_vec_mad_tbq4`.
- `test-quantize-fns` still reports the known TBQ2/TBQ3 failures; TBQ4 did not report a failure.
- The speed run used `scripts/fresh_eval.py` with memory preflight enabled at `--min-memory-free-pct 20`.
- Minimum recorded free-memory percentage before/after model commands was `57%`; maximum model RSS was about `5.9 GB`.
- No model benchmark processes were left running after the pass.

## Focused 8K Results

Command shape:

```text
llama-bench -t 6 -p 0 -n 128 -r 5 -d 8192 -fa 1 -ngl 0 -o csv
```

Raw and normalized outputs:

```text
benchmark_results/fresh_edge_agentic_20260501/arm_m4_tbq4_opt/speed/
```

| model | config | tok/s | delta vs F16 |
|---|---|---:|---:|
| gemma4_e4b | f16/f16 | 16.166 | +0.0% |
| gemma4_e4b | q8_0/q8_0 | 14.638 | -9.5% |
| gemma4_e4b | q4_0/q4_0 | 12.885 | -20.3% |
| gemma4_e4b | tbq4/tbq4 | 15.521 | -4.0% |
| gemma4_e4b | q8_0/tbq4 | 14.319 | -11.4% |
| qwen35_4b | f16/f16 | 9.523 | +0.0% |
| qwen35_4b | q8_0/q8_0 | 9.346 | -1.9% |
| qwen35_4b | q4_0/q4_0 | 8.840 | -7.2% |
| qwen35_4b | tbq4/tbq4 | 10.081 | +5.9% |
| qwen35_4b | q8_0/tbq4 | 9.986 | +4.9% |

## Interpretation

This build fixes the worst ARM scalar behavior only partially. TBQ4 is no longer dramatically slower for Gemma, and it beats F16 for Qwen3.5-4B, but it does not reproduce the earlier Gemma ARM win and the mixed `q8_0/tbq4` deployment candidate is negative for Gemma.

The absolute F16 numbers in this focused pass are lower than the earlier fresh ARM run, so the absolute speed values should not be mixed across runs. The within-build deltas are still useful: they show that this NEON implementation is not yet a robust ARM win.

## Claim Impact

The optimized TurboQuant for edge-agentic-AI claim is not publishable yet for ARM. Current evidence supports:

- x86 CPU speedup: yes, from the copied fresh x86 results.
- Gemma quality preservation: partially, from fresh PPL and prompt judging.
- ARM speedup: not yet; this unified Qwen-capable ARM build is mixed.
- Qwen quality preservation: not yet; the Qwen loader/output quality remains a separate blocker.
- "Lossless" wording: no. Use "quality-preserving under tested conditions" only where PPL and task outputs support it.

Next technical step: recover the exact earlier optimized ARM TBQ4 implementation or profile this NEON build. The most likely remaining issue is that the ARM V-cache fused path and/or build CPU-feature mix is still not matching the previous optimized Gemma behavior.
