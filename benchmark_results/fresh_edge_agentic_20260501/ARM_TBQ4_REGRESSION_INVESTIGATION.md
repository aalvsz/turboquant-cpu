# ARM TBQ4 Regression Investigation

Date: 2026-05-01

## Trigger

The latest ARM follow-up showed Gemma `tbq4/tbq4` slower than `f16/f16`.
That result conflicts with the earlier optimized ARM run, so it should not be
accepted without isolating build and measurement effects.

## New Artifacts

- `arm_m4_old_build_gemma_short`: old optimized ARM binary, Gemma, 6 threads,
  8K depth, `n_gen=16`, `r=3`, full KV matrix.
- `arm_m4_opt_build_gemma_short`: rebuilt ARM binary from the fresh source,
  same command shape.
- `arm_m4_idle_gated_probe`: attempted idle-gated run. It refused to start
  because CPU load was too high.
- `arm_m4_old_build_gemma_short_prio3_noisy`: attempted high-priority probe.
  It failed because macOS denied `llama-bench --prio 3`.

## A/B Results

Same device, same Gemma model, same 6-thread / 8K / `n_gen=16` / `r=3`
benchmark shape:

| Run | `f16/f16` tok/s | `tbq4/tbq4` tok/s | TBQ4 vs F16 | `q8_0/tbq4` tok/s | q8/TBQ4 vs F16 |
|---|---:|---:|---:|---:|---:|
| old optimized binary now | 16.672 | 18.609 | +11.62% | 16.947 | +1.65% |
| rebuilt binary now | 18.010 | 17.422 | -3.26% | 17.019 | -5.50% |
| historical old optimized run | 20.052 | 20.445 | +1.96% | 24.597 | +22.67% |

## Build Inspection

The two ARM build caches use the same relevant CPU build shape:

- `CMAKE_BUILD_TYPE=Release`
- `GGML_NATIVE=ON`
- `GGML_METAL=OFF`
- `GGML_ACCELERATE=ON`
- compile flags include `-O3`, `-arch arm64`, and
  `-mcpu=native+dotprod+i8mm+nosve+sme`

The old binary reports commit `ef7047a-dirty`; the fresh rebuilt source reports
`90b03b6`. The compiled TBQ4 symbols exist in both builds:

- `_ggml_vec_dot_tbq4_q8_0`
- `_ggml_vec_dot_tbq4_q8_0_generic`
- `_ggml_vec_mad_tbq4`

Disassembly showed the `ggml_vec_dot_tbq4_q8_0` hot function is effectively the
same in both binaries. `ggml_vec_mad_tbq4` is also the same NEON kernel shape,
with minor instruction scheduling differences. So the current evidence does
not support a simple "NEON TBQ4 symbol missing from the rebuild" explanation.

## Measurement Problem Found

The current ARM host is not idle enough for publishable CPU speed numbers.
Before any model process was active:

- RAM was safe: about 54-55% free.
- CPU load was not safe: load averages around 5-6.
- Top CPU users included Cursor renderer processes, WindowServer, WebKit, and
  endpoint/security background services.

The new idle gate refused to start at `loadavg_1m=6.20` with a threshold of
`2.00`. That is the correct behavior for future publication-grade runs.

The failed `--prio 3` probe is also informative: macOS returned permission
denied, so we cannot rely on `llama-bench --prio 3` from this user session.

## Interpretation

You were right to challenge the negative ARM TBQ4 result. It is not clean
enough to support "TBQ4 is slower than F16" on this ARM device.

The old optimized binary still puts `tbq4/tbq4` ahead of F16 in the same short
A/B run. However, the same old binary did not reproduce the historical
`q8_0/tbq4` speedup under today's noisy host conditions, which points to
measurement contamination rather than a single build regression.

At the same time, "TBQ4 cannot be slower than F16" is too strong as a universal
engineering statement. TBQ4 trades KV bandwidth for extra dequant/LUT work; it
wins when KV-cache bandwidth is the bottleneck and the kernel/dispatch path is
good, but it can lose under CPU contention, thermal/power variability, or when
the workload is not KV-bandwidth-bound enough.

## Runner Fix

`scripts/fresh_eval.py` now records CPU load and top CPU processes in every
command metadata file. It also supports:

- `--max-load-1m`
- `--max-load-1m-per-core`
- `--kv-configs`
- `--bench-prio`
- `--cpu-mask`
- `--cpu-strict`
- `--bench-delay`

For future ARM speed claims, use an idle gate, for example:

```bash
python3 benchmark_results/fresh_edge_agentic_20260501/scripts/fresh_eval.py \
  --root benchmark_results/fresh_edge_agentic_20260501/arm_m4_idle_confirm \
  --host-label arm_m4_idle_confirm \
  --bench-bin benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-opt/bin/llama-bench \
  --cli-bin benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-opt/bin/llama-cli \
  --ppl-bin benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-opt/bin/llama-perplexity \
  --dataset benchmark_results/fresh_edge_agentic_20260501/shared/wikitext-2-raw/wiki.test.raw \
  --model gemma4_e4b=/Users/ander.alvarez/Downloads/gemma-4-E4B-it-Q4_0.gguf \
  --stage speed \
  --threads-speed 6 \
  --depths 8192 \
  --speed-n-gen 128 \
  --speed-repetitions 5 \
  --min-memory-free-pct 20 \
  --max-load-1m 2.0 \
  --kv-configs f16/f16,tbq4/tbq4,q8_0/tbq4
```

## Claim Status

The optimized TurboQuant edge-agentic-AI claim is not publication-ready yet.
The strongest current evidence remains x86 speedup plus Gemma quality
preservation, with a useful ARM/Qwen speed signal. The ARM/Gemma speed signal
must be rerun under the new CPU-load gate before being cited.

Do not call the technique lossless. The defensible wording is
quality-preserving under the tested Gemma conditions, pending broader model,
task, and hardware validation.
