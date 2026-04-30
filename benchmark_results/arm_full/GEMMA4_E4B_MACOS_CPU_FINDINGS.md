# Gemma 4 E4B macOS CPU Follow-Up

**Date:** 2026-04-30

**Host:** Apple M4 Max, `arm64`, 14 CPU cores reported by macOS
(`hw.perflevel0.physicalcpu=10`, `hw.perflevel1.physicalcpu=4`), 36 GB RAM

**Build:** CPU only, `GGML_METAL=OFF`, `GGML_ACCELERATE=ON`,
`GGML_NATIVE=ON`

**Model:** Gemma 4 E4B IT, Q4_0 GGUF

**Benchmark:** `llama-bench`, 6 threads, flash attention enabled,
`n_prompt=0`, `n_gen=16`, `repetitions=2`, depths
`0,512,2048,4096,8192`

This is the Apple Silicon replication of the x86 Gemma 4 E4B CPU investigation.
The Mac CPU is ARM, not x86. The build needed one portability fix before
running: non-x86 builds now export scalar wrappers for
`ggml_vec_dot_tbq{2,3,4}_q8_0`, because the optimized implementations were only
present in the x86 arch file.

## Main Result

Apple Silicon is much faster in absolute throughput than the earlier local x86
CPU, but the **relative TBQ4 speedup does not reproduce on this ARM build**.
At 8K KV depth, `tbq4/tbq4` is slower than F16, Q8_0, and Q4_0 on the M4 Max.

| KV config | x86 8K tok/s | macOS 8K tok/s | macOS vs x86 | macOS vs macOS F16 |
|---|---:|---:|---:|---:|
| `f16/f16` | 7.071 | 33.232 | 4.70x | baseline |
| `q8_0/q8_0` | 8.575 | 30.049 | 3.50x | -9.6% |
| `q4_0/q4_0` | 7.880 | 29.471 | 3.74x | -11.3% |
| `tbq4/tbq4` | 9.193 | 23.715 | 2.58x | -28.6% |
| `q8_0/tbq4` | n/a | 25.398 | n/a | -23.6% |

Mac-only decode throughput by depth:

| KV depth | F16/F16 | Q8_0/Q8_0 | Q4_0/Q4_0 | TBQ4/TBQ4 | Q8_0/TBQ4 |
|---:|---:|---:|---:|---:|---:|
| 0 | 48.634 | 13.917 | 44.729 | 39.182 | 49.278 |
| 512 | 46.782 | 32.944 | 41.982 | 31.945 | 42.308 |
| 2048 | 40.701 | 35.698 | 38.831 | 30.835 | 36.966 |
| 4096 | 37.633 | 36.008 | 35.502 | 28.075 | 32.209 |
| 8192 | 33.232 | 30.049 | 29.471 | 23.715 | 25.398 |

The likely explanation is implementation parity, not model quality:

- x86 has AVX2 TurboQuant vec-dot and fused V-cache accumulation paths.
- this ARM run uses scalar TurboQuant vec-dot wrappers and the generic
  non-AVX2 `ggml_vec_mad_tbq4` fallback.
- Q8_0/Q4_0 already have mature ARM NEON/i8mm paths in `llama.cpp`; TBQ does
  not yet.

So the current ARM result says: **TurboQuant needs NEON/SVE kernels before the
x86 speed claim can be compared fairly on Apple Silicon.**

## ARM-Optimized Follow-Up Build

A second, separate build was added at `llama.cpp/build-arm-turboquant`; the
existing `llama.cpp/build-macos-cpu` build was not deleted. This build uses the
same CPU-only CMake configuration, but the source now has ARM NEON/i8mm TBQ4
hot paths:

- `ggml_vec_dot_tbq4_q8_0` in `ggml/src/ggml-cpu/arch/arm/quants.c`
- `ggml_vec_mad_tbq4` NEON path in `ggml/src/ggml-cpu/quants.c`

The new build restores the x86 direction in a memory-conscious 8K smoke run
using one repetition:

| KV config | ARM baseline 8K tok/s | ARM TBQ4-opt 8K tok/s | Opt-build vs F16 |
|---|---:|---:|---:|
| `f16/f16` | 33.232 | 20.923 | baseline |
| `q8_0/q8_0` | 30.049 | 18.726 | -10.5% |
| `q4_0/q4_0` | 29.471 | 18.272 | -12.7% |
| `tbq4/tbq4` | 23.715 | 22.787 | +8.9% |
| `q8_0/tbq4` | 25.398 | 24.762 | +18.3% |

The absolute optimized-build smoke numbers are lower because this was a
single-repetition run taken after prior heavy memory pressure, so they should
not replace the full scalar matrix. The relative result is the important
follow-up: with ARM TBQ4 kernels enabled, TBQ4 is again faster than F16/Q8/Q4 at
8K, and the hybrid `q8_0/tbq4` is fastest in this smoke run.

Smoke artifacts are in `results/macos_cpu_arm_turboquant/smoke_8k/`.

`test-quantize-fns` builds under `build-arm-turboquant`. It still exits nonzero
because the existing TBQ2/TBQ3 threshold checks fail; TBQ4 did not report a
failure in that test run.

## ARM Tuning Follow-Up

A stable speed-only follow-up was run at 8K depth, 6 threads, `n_gen=16`, and
3 repetitions to reduce the noise in the one-repetition smoke run. This uses
the final ARM build with the one-row NEON TBQ4 dot path enabled.

| KV config | 8K tok/s | vs F16 |
|---|---:|---:|
| `f16/f16` | 20.052 | baseline |
| `q8_0/q8_0` | 17.794 | -11.3% |
| `q4_0/q4_0` | 17.605 | -12.2% |
| `tbq4/tbq4` | 20.445 | +2.0% |
| `q8_0/tbq4` | 24.597 | +22.7% |

The practical M4 Max recommendation from this pass is therefore
`q8_0/tbq4`: keep K cache on the mature ARM Q8_0 path and use TBQ4 for V
cache, where the ARM `ggml_vec_mad_tbq4` path pays off clearly.

An experimental TBQ4 `.nrows = 2` dispatch using Apple I8MM
(`vmmlaq_s32`) was implemented and checked for numerical correctness against
four independent one-row TBQ4 dot products. It matched within `~1e-6`, but it
was slower in `llama-bench` and was reverted:

| KV config | before I8MM dispatch | I8MM 2-row dispatch |
|---|---:|---:|
| `f16/f16` | 20.052 | 19.319 |
| `tbq4/tbq4` | 20.445 | 18.719 |
| `q8_0/tbq4` | 24.597 | 23.561 |

The M4 Max path is not "done", but this experiment rules out the obvious
reuse of llama.cpp's two-row int8 matmul dispatch for TBQ4. The next useful
kernel work is a profile-guided K-cache TBQ4 path rather than forcing TBQ4
into the Q4_0/Q8_0 `.nrows = 2` schedule.

## Quality Checks

The quality side does replicate. The 20-chunk WikiText-2 PPL values are nearly
identical across hosts, and TBQ4 remains the lowest-PPL setting in this small
run.

| KV config | x86 PPL | macOS PPL | macOS - x86 |
|---|---:|---:|---:|
| `f16/f16` | 117.9486 | 117.6615 | -0.2871 |
| `q8_0/q8_0` | 117.4703 | 117.7613 | +0.2910 |
| `q4_0/q4_0` | 133.7736 | 134.7332 | +0.9596 |
| `tbq4/tbq4` | 113.8643 | 113.8434 | -0.0209 |
| `q8_0/tbq4` | 116.7188 | 116.8874 | +0.1686 |

Hard-prompt heuristic task scores are also close for TBQ4 and hybrid:

| KV config | x86 mean task score | macOS mean task score | macOS - x86 |
|---|---:|---:|---:|
| `f16/f16` | 0.8375 | 0.8375 | +0.0000 |
| `q8_0/q8_0` | 0.8375 | 0.8375 | +0.0000 |
| `q4_0/q4_0` | 0.8875 | 0.7250 | -0.1625 |
| `tbq4/tbq4` | 0.7688 | 0.7688 | +0.0000 |
| `q8_0/tbq4` | 0.8375 | 0.8125 | -0.0250 |

## Artifacts

- Raw macOS run: `results/macos_cpu/`
- Host comparison: `results/macos_cpu/comparison/summary.md`
- Speed comparison CSV:
  `results/macos_cpu/comparison/speed_x86_vs_macos.csv`
- PPL comparison CSV:
  `results/macos_cpu/comparison/ppl_x86_vs_macos.csv`
- Hard-prompt task comparison CSV:
  `results/macos_cpu/comparison/quality_task_x86_vs_macos.csv`

## Next Work

1. Profile the K-cache TBQ4 attention path on ARM. The V-cache path is already
   strong enough that `q8_0/tbq4` is the best measured M4 Max configuration.
2. Tighten or split the existing TBQ2/TBQ3 `test-quantize-fns` thresholds so
   the ARM build can use that test as a clean regression gate for TBQ4 changes.
3. Add x86 `q8_0/tbq4` speed rows to the sanitized x86 summary so hybrid can be
   compared directly across hosts.
