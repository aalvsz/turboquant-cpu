# TurboQuant CPU Rerun Report

Run folder: `benchmark_results/fresh_edge_agentic_20260501/rerun_qwen35_qualityfix_20260501_161433`

## Scope

- Devices: local ARM M4 and remote x86 `axelera-ander-wfh`.
- Models: `gemma4_e4b` and `qwen35_4b`.
- Build: Qwen3.5 quality-fix TurboQuant build.
- Matrix: speed, sustained 8K decode, perplexity, deterministic prompt quality, and judge.
- KV configs: `f16/f16`, `q8_0/q8_0`, `q4_0/q4_0`, `tbq4/tbq4`, `q8_0/tbq4`.

## Corrections During Rerun

- Qwen3.5 PPL with the default `llama-perplexity` batching used `n_seq=4`, which produced invalid Qwen PPL and crashed with `K=q8_0`.
- The runner was patched to support explicit PPL batch controls and resume:
  - `--ppl-batch 512`
  - `--ppl-ubatch 512`
  - `--skip-existing`
- Corrected PPL uses one sequence per batch. ARM PPL was rerun and x86 was resumed before reaching PPL.
- Debug artifacts for the original Qwen PPL crash are in `arm_m4/debug/`.

## Completion

All final rows completed with return code `0`.

| host | speed | sustained | ppl | quality | judge |
|---|---:|---:|---:|---:|---:|
| `arm_m4` | 60/60 | 12/12 | 10/10 | 100/100 | 100/100 |
| `x86_axelera` | 60/60 | 12/12 | 10/10 | 100/100 | 100/100 |

## Main Result

The optimized TBQ path is no longer slower than F16 in the important 8K decode measurements.

On x86, `tbq4/tbq4` is consistently faster than F16 at 8K:

- Gemma 6 threads: `9.193 tok/s` vs `7.266 tok/s` (`+26.5%`)
- Gemma 12 threads: `8.986 tok/s` vs `7.118 tok/s` (`+26.3%`)
- Qwen 6 threads: `6.923 tok/s` vs `5.334 tok/s` (`+29.8%`)
- Qwen 12 threads: `6.495 tok/s` vs `5.131 tok/s` (`+26.6%`)

On ARM, `tbq4/tbq4` is also faster than F16 at 8K:

- Gemma 6 threads: `37.635 tok/s` vs `35.703 tok/s` (`+5.4%`)
- Gemma 10 threads: `39.392 tok/s` vs `34.321 tok/s` (`+14.8%`)
- Qwen 6 threads: `27.350 tok/s` vs `24.297 tok/s` (`+12.6%`)
- Qwen 10 threads: `29.103 tok/s` vs `27.349 tok/s` (`+6.4%`)

## Sustained Decode

Sustained 8K decode confirms the same pattern for `tbq4/tbq4`:

- ARM Gemma: `+5.1%` at 6 threads, `+11.2%` at 10 threads.
- ARM Qwen: `+13.6%` at 6 threads, `+7.4%` at 10 threads.
- x86 Gemma: about `+27%` at 6 and 12 threads.
- x86 Qwen: about `+31%` at 6 threads and `+28%` at 12 threads.

`q8_0/tbq4` is very strong on x86 and mixed on ARM:

- x86 sustained: `+22%` to `+26%` vs F16 across both models/thread counts.
- ARM sustained: positive for Gemma 10 and Qwen 6, slightly negative for Gemma 6 and Qwen 10.

## Quality And PPL

Corrected PPL is close to F16 for Qwen:

- ARM Qwen `q8_0/tbq4`: `+0.7%` PPL vs F16.
- ARM Qwen `tbq4/tbq4`: `+0.6%` PPL vs F16.
- x86 Qwen `q8_0/tbq4`: `+0.7%` PPL vs F16.
- x86 Qwen `tbq4/tbq4`: `+0.9%` PPL vs F16.

Gemma PPL is not worse for TBQ in this dataset:

- ARM Gemma `q8_0/tbq4`: `-3.3%` vs F16.
- ARM Gemma `tbq4/tbq4`: `-2.9%` vs F16.
- x86 Gemma `q8_0/tbq4`: `-1.0%` vs F16.
- x86 Gemma `tbq4/tbq4`: `-3.5%` vs F16.

Prompt quality has zero degenerate outputs across all final rows.

- Qwen is stable: ARM `q8_0/tbq4` scores `4.6/5`, ARM `tbq4/tbq4` scores `4.4/5`; x86 Qwen scores `4.4/5` for all KV settings.
- Gemma is slightly weaker on the heuristic prompt judge under TBQ settings: F16 is `3.7/5`, while TBQ settings are `3.35-3.5/5` depending on host/config.

## Conclusion

The rerun supports a strong claim that optimized TurboQuant KV can improve CPU LLM decode performance on both ARM and x86 while preserving task quality in this focused suite.

It does not yet justify calling TurboQuant strictly lossless. Outputs are not bit-identical, Qwen PPL deltas are small but nonzero, and Gemma prompt-judge scores dip slightly under TBQ settings. The evidence supports "quality-preserving" or "near-lossless in this test matrix", not a final lossless optimization claim.

For an edge agentic AI publication claim, the current evidence is promising and useful, especially for `tbq4/tbq4` and x86 `q8_0/tbq4`. Before publishing the stronger claim, add broader agent benchmarks, larger prompt sets, more model families, longer contexts, thermal/power measurements, and real multi-step tool-use tasks.
