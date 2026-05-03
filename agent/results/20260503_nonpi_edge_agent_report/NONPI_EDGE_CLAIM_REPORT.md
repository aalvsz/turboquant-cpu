# Non-Pi Edge Agent TurboQuant Claim Report

Generated: 2026-05-03

## Scope

- Devices: Apple M4 Max ARM64 and Axelera x86 CPU host. Raspberry Pi is intentionally excluded from this run and remains the next hardware target.
- Models: `gemma4_e4b` and `qwen35_4b` GGUF models.
- Agent workload: Google ADK-compatible local agent harness, CPU-only `llama-server`, 8K context, 5 tool-heavy tasks per row, LLM orchestrator plus LLM-powered helper tools.
- KV configs: `f16/f16`, `q8_0/q8_0`, `q4_0/q4_0`, `tbq4/tbq4`, `q8_0/tbq4`.
- Validity: 20/20 rows completed, 100/100 tasks executed, 100% final JSON validity, 0 server return-code failures.

## Bottom Line

We are not ready to publish a strict `lossless optimization` paper claim. The evidence is strong enough for a narrower claim: TurboQuant KV-cache formats, especially mixed `q8_0/tbq4`, can reduce CPU edge-agent wall time and energy versus Q4 on both tested CPU targets while preserving tool/JSON discipline in this task suite. Full `tbq4/tbq4` is promising for Gemma and M4 Qwen, but it is not uniformly quality-preserving and is not always faster than F16.

The best current paper wording is: `TurboQuant is a CPU-side KV-cache optimization that can preserve agent tool discipline and reduce high-context local-agent latency/energy under tested workloads.` Avoid `lossless` until repeat statistics and broader quality evaluation support it.

## Agent Matrix vs Q4 and F16

| host | model | config | wall s | vs Q4 wall | vs F16 wall | quality | quality vs Q4 | JSON | energy J | energy vs Q4 | energy vs F16 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_fixed_core8k_battery | gemma4_e4b | f16/f16 | 145.2 | -17.4% | +0.0% | 0.813 | +0.093 | 1.0 | 12829.0 | -15.9% | +0.0% |
| m4_fixed_core8k_battery | gemma4_e4b | q4_0/q4_0 | 175.9 | +0.0% | +21.1% | 0.720 | +0.000 | 1.0 | 15258.4 | +0.0% | +18.9% |
| m4_fixed_core8k_battery | gemma4_e4b | q8_0/q8_0 | 163.0 | -7.3% | +12.3% | 0.787 | +0.067 | 1.0 | 13925.2 | -8.7% | +8.5% |
| m4_fixed_core8k_battery | gemma4_e4b | q8_0/tbq4 | 142.9 | -18.7% | -1.6% | 0.787 | +0.067 | 1.0 | 12336.8 | -19.1% | -3.8% |
| m4_fixed_core8k_battery | gemma4_e4b | tbq4/tbq4 | 141.3 | -19.7% | -2.7% | 0.733 | +0.013 | 1.0 | 12477.2 | -18.2% | -2.7% |

| m4_fixed_core8k_battery | qwen35_4b | f16/f16 | 160.8 | -12.6% | +0.0% | 0.680 | -0.127 | 1.0 | 13550.9 | +5.2% | +0.0% |
| m4_fixed_core8k_battery | qwen35_4b | q4_0/q4_0 | 184.0 | +0.0% | +14.4% | 0.807 | +0.000 | 1.0 | 12878.7 | +0.0% | -5.0% |
| m4_fixed_core8k_battery | qwen35_4b | q8_0/q8_0 | 182.9 | -0.6% | +13.7% | 0.687 | -0.120 | 1.0 | 13682.1 | +6.2% | +1.0% |
| m4_fixed_core8k_battery | qwen35_4b | q8_0/tbq4 | 144.4 | -21.5% | -10.2% | 0.727 | -0.080 | 1.0 | 9487.8 | -26.3% | -30.0% |
| m4_fixed_core8k_battery | qwen35_4b | tbq4/tbq4 | 156.4 | -15.0% | -2.8% | 0.813 | +0.007 | 1.0 | 13201.7 | +2.5% | -2.6% |

| x86_axelera_fixed_core8k | gemma4_e4b | f16/f16 | 521.6 | -23.2% | +0.0% | 0.813 | +0.027 | 1.0 | 34041.3 | -23.3% | +0.0% |
| x86_axelera_fixed_core8k | gemma4_e4b | q4_0/q4_0 | 679.4 | +0.0% | +30.3% | 0.787 | +0.000 | 1.0 | 44364.1 | +0.0% | +30.3% |
| x86_axelera_fixed_core8k | gemma4_e4b | q8_0/q8_0 | 548.8 | -19.2% | +5.2% | 0.787 | +0.000 | 1.0 | 35845.5 | -19.2% | +5.3% |
| x86_axelera_fixed_core8k | gemma4_e4b | q8_0/tbq4 | 518.6 | -23.7% | -0.6% | 0.733 | -0.053 | 1.0 | 33830.6 | -23.7% | -0.6% |
| x86_axelera_fixed_core8k | gemma4_e4b | tbq4/tbq4 | 524.1 | -22.9% | +0.5% | 0.787 | +0.000 | 1.0 | 34276.4 | -22.7% | +0.7% |

| x86_axelera_fixed_core8k | qwen35_4b | f16/f16 | 496.8 | -23.1% | +0.0% | 0.700 | -0.073 | 1.0 | 32335.2 | -23.1% | +0.0% |
| x86_axelera_fixed_core8k | qwen35_4b | q4_0/q4_0 | 645.8 | +0.0% | +30.0% | 0.773 | +0.000 | 1.0 | 42034.0 | +0.0% | +30.0% |
| x86_axelera_fixed_core8k | qwen35_4b | q8_0/q8_0 | 584.0 | -9.6% | +17.5% | 0.693 | -0.080 | 1.0 | 38003.8 | -9.6% | +17.5% |
| x86_axelera_fixed_core8k | qwen35_4b | q8_0/tbq4 | 490.7 | -24.0% | -1.2% | 0.787 | +0.013 | 1.0 | 33081.5 | -21.3% | +2.3% |
| x86_axelera_fixed_core8k | qwen35_4b | tbq4/tbq4 | 558.4 | -13.5% | +12.4% | 0.720 | -0.053 | 1.0 | 36345.3 | -13.5% | +12.4% |

Energy notes: M4 energy is whole-system battery discharge estimated from `ioreg` because passwordless `powermetrics` was unavailable. x86 energy is Intel RAPL package energy; two rows were repaired from raw samples to handle counter wrap.

## Best Configs Observed

- `m4_fixed_core8k_battery` / `gemma4_e4b` fastest: `tbq4/tbq4` at 141.3s, quality 0.733. Best quality: `f16/f16` at 0.813. Lowest measured energy: `q8_0/tbq4` at 12336.8 J.
- `m4_fixed_core8k_battery` / `qwen35_4b` fastest: `q8_0/tbq4` at 144.4s, quality 0.727. Best quality: `tbq4/tbq4` at 0.813. Lowest measured energy: `q8_0/tbq4` at 9487.8 J.
- `x86_axelera_fixed_core8k` / `gemma4_e4b` fastest: `q8_0/tbq4` at 518.6s, quality 0.733. Best quality: `f16/f16` at 0.813. Lowest measured energy: `q8_0/tbq4` at 33830.6 J.
- `x86_axelera_fixed_core8k` / `qwen35_4b` fastest: `q8_0/tbq4` at 490.7s, quality 0.787. Best quality: `q8_0/tbq4` at 0.787. Lowest measured energy: `f16/f16` at 32335.2 J.

## F16/TBQ Performance Interpretation

The user concern that `tbq4` cannot be slower than F16 is not supported universally by these measurements. TurboQuant reduces KV bandwidth, but F16 can still win in prompt-heavy paths when kernel overhead, conversion cost, cache behavior, or non-KV compute dominates. The low-level profiles on both CPUs show the same broad pattern: TBQ and mixed TBQ are much faster than Q4 for prompt processing, decode is near F16 or better in several Gemma slices, but prompt throughput can remain below F16.

M4 profile: 4096-token prompt and 128-token decode, CPU-only, 10 threads, flash attention on.

| model | config | prompt tok/s | prompt vs F16 | prompt vs Q4 | decode tok/s | decode vs F16 | decode vs Q4 |
|---|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 218.707 | +0.0% | +42.0% | 38.368 | +0.0% | +12.1% |
| gemma4_e4b | q4_0/q4_0 | 154.028 | -29.6% | +0.0% | 34.220 | -10.8% | +0.0% |
| gemma4_e4b | q8_0/q8_0 | 169.954 | -22.3% | +10.3% | 35.502 | -7.5% | +3.7% |
| gemma4_e4b | q8_0/tbq4 | 207.348 | -5.2% | +34.6% | 41.622 | +8.5% | +21.6% |
| gemma4_e4b | tbq4/tbq4 | 206.516 | -5.6% | +34.1% | 41.291 | +7.6% | +20.7% |
| qwen35_4b | f16/f16 | 185.409 | +0.0% | +23.5% | 31.900 | +0.0% | +1.8% |
| qwen35_4b | q4_0/q4_0 | 150.094 | -19.0% | +0.0% | 31.340 | -1.8% | +0.0% |
| qwen35_4b | q8_0/q8_0 | 147.177 | -20.6% | -1.9% | 31.839 | -0.2% | +1.6% |
| qwen35_4b | q8_0/tbq4 | 182.037 | -1.8% | +21.3% | 33.839 | +6.1% | +8.0% |
| qwen35_4b | tbq4/tbq4 | 175.166 | -5.5% | +16.7% | 31.781 | -0.4% | +1.4% |

x86 profile: 2048-token prompt and 64-token decode, CPU-only, 6 threads, flash attention on.

| model | config | prompt tok/s | prompt vs F16 | prompt vs Q4 | decode tok/s | decode vs F16 | decode vs Q4 |
|---|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 75.158 | +0.0% | +41.0% | 10.015 | +0.0% | -0.3% |
| gemma4_e4b | q8_0/q8_0 | 64.097 | -14.7% | +20.2% | 10.042 | +0.3% | -0.0% |
| gemma4_e4b | q4_0/q4_0 | 53.321 | -29.1% | +0.0% | 10.043 | +0.3% | +0.0% |
| gemma4_e4b | tbq4/tbq4 | 66.872 | -11.0% | +25.4% | 10.089 | +0.7% | +0.5% |
| gemma4_e4b | q8_0/tbq4 | 68.050 | -9.5% | +27.6% | 10.112 | +1.0% | +0.7% |
| qwen35_4b | f16/f16 | 59.611 | +0.0% | +13.3% | 7.599 | +0.0% | +1.0% |
| qwen35_4b | q8_0/q8_0 | 56.954 | -4.5% | +8.3% | 7.662 | +0.8% | +1.9% |
| qwen35_4b | q4_0/q4_0 | 52.610 | -11.7% | +0.0% | 7.521 | -1.0% | +0.0% |
| qwen35_4b | tbq4/tbq4 | 59.002 | -1.0% | +12.2% | 7.509 | -1.2% | -0.2% |
| qwen35_4b | q8_0/tbq4 | 59.371 | -0.4% | +12.9% | 7.576 | -0.3% | +0.7% |

## Claim Assessment

- Supported now: CPU-only local agents can run with TurboQuant KV formats and keep structured tool behavior intact on M4 and x86 for this task suite.
- Supported now: `q8_0/tbq4` is the best overall performance candidate. It was fastest for M4 Qwen and x86 Qwen, nearly tied or fastest for Gemma, and reduced measured energy versus Q4 on x86 and M4 Qwen.
- Supported for Gemma: full `tbq4/tbq4` is quality-noninferior to Q4 in these aggregate rows and materially faster/lower energy than Q4.
- Not supported yet: `TurboQuant is lossless` across model families. Qwen full `tbq4/tbq4` on x86 was faster than Q4 but had lower quality than Q4, and full TBQ4 was slower than F16 for x86 Qwen.
- Not supported yet: broad edge-agent deployment paper claims without Raspberry Pi, repeated runs, and controlled SoC/package power on ARM.

## Remaining Paper Gaps Before Submission

1. Add Raspberry Pi or another genuinely constrained SBC and repeat the same matrix.
2. Add at least 3-5 repeats for confidence intervals; current rows are single repeats.
3. Add a larger correctness/quality suite beyond the deterministic 5-task rubric.
4. Capture controlled ARM SoC power with `powermetrics` or an external meter; current M4 power is whole-system battery discharge.
5. Run context sweeps such as 2K/4K/8K/16K to isolate where KV-cache savings dominate.

## Artifacts

- `UNIFIED_EDGE_AGENT_REPORT.md`: generated q4-baseline report with latency, energy, and non-inferiority tables.
- `aggregate_summary.csv`, `latency_breakdown.csv`, `quality_noninferiority.csv`: paper-style tables.
- `../20260503_m4_fixed_core8k/`: full M4 raw agent run.
- `../20260503_x86_fixed_core8k/`: full copied x86 raw agent run, RAPL repaired.
- `../20260503_m4_llama_bench_f16_tbq/`: M4 low-level F16/TBQ profile.
- `../20260503_x86_llama_bench_f16_tbq/`: x86 low-level F16/TBQ profile.
