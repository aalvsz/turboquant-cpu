# Unified TurboQuant Edge-Agent Paper Report

Generated: `2026-05-03T12:53:43`

## Input Runs

- `x86_axelera_qwen_fix_smoke`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260503_x86_qwen_fix_smoke`; contexts=[8192]; repeats=1; tasks=2; threads=6
- `x86_axelera_qwen_fix_telemetry`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260503_x86_qwen_fix_telemetry`; contexts=[8192]; repeats=1; tasks=1; threads=6

## Key Findings

- Completed `6` benchmark jobs and `9` task executions. Server return-code failures in included summaries: `0`.
- No Gemma 4B 8K `tbq4/tbq4` rows are included in this report.
- No Qwen 3.5 4B M4 8K `tbq4/tbq4` rows are included in this report.
- Qwen 3.5 4B on x86 no longer shows zero-valid-JSON 8K aggregate rows; `tbq4/tbq4` speedups range from 5.2% to 10.7% with quality deltas from -0.233 to -0.083.
- This report resolves the Qwen/x86 serving-path question only. Use the full cross-device matrix before making broad edge-agent claims.

## 8K Q4 Baseline Comparison

Negative `vs Q4` means lower wall time than Q4. Positive `speedup` means faster than Q4.

| run | host | model | config | reps | wall mean s | wall CI95 | vs Q4 | speedup | quality | quality delta | JSON | RSS MB |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| agent | x86_axelera_qwen_fix_smoke | qwen35_4b | q4_0/q4_0 | 1 | 111.256 | 0.000 | 0.0% | 0.0% | 0.917 | 0.000 | 1.000 | 5153.6 |
| agent | x86_axelera_qwen_fix_smoke | qwen35_4b | q8_0/tbq4 | 1 | 107.657 | 0.000 | -3.2% | 3.3% | 0.917 | 0.000 | 1.000 | 5178.9 |
| agent | x86_axelera_qwen_fix_smoke | qwen35_4b | tbq4/tbq4 | 1 | 105.716 | 0.000 | -5.0% | 5.2% | 0.833 | -0.083 | 1.000 | 5190.5 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | qwen35_4b | q4_0/q4_0 | 1 | 60.050 | 0.000 | 0.0% | 0.0% | 0.900 | 0.000 | 1.000 | 4837.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | qwen35_4b | q8_0/tbq4 | 1 | 58.571 | 0.000 | -2.5% | 2.5% | 0.900 | 0.000 | 1.000 | 4905.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | qwen35_4b | tbq4/tbq4 | 1 | 54.259 | 0.000 | -9.6% | 10.7% | 0.667 | -0.233 | 1.000 | 4868.5 |

## Quality Non-Inferiority vs Q4

`JSON >= Q4` is a paired relative check; `config JSON` and `Q4 JSON` are the absolute validity rates.

| run | host | ctx | model | config | paired cases | quality >= Q4 | JSON >= Q4 | config JSON | Q4 JSON |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q8_0/tbq4 | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | tbq4/tbq4 | 2 | 0.500 | 1.000 | 1.000 | 1.000 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 0.000 | 1.000 | 1.000 | 1.000 |

## Latency Decomposition

| run | host | ctx | model | config | planner s | deterministic tools s | LLM tools s | final s | prompt eval ms | decode ms |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q4_0/q4_0 | 22.157 | 0.000 | 19.246 | 14.224 | 19952.3 | 35561.2 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q8_0/tbq4 | 21.702 | 0.000 | 16.313 | 15.813 | 18066.4 | 35653.5 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | tbq4/tbq4 | 21.659 | 0.000 | 18.753 | 12.446 | 20606.2 | 32134.8 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q4_0/q4_0 | 23.998 | 0.000 | 19.044 | 17.008 | 21537.3 | 38407.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q8_0/tbq4 | 21.576 | 0.000 | 18.711 | 18.283 | 19908.8 | 38549.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | tbq4/tbq4 | 22.453 | 0.000 | 19.389 | 12.417 | 20999.9 | 33145.8 |

## Power And Thermal Telemetry

Telemetry is comparable only within the same device and controlled power/ambient conditions.
Zero joules/watts means the energy counter was unavailable or unreadable during that run, not zero power draw.

| run | host | ctx | model | config | max temp C | pkg joules | avg pkg W |
|---|---|---:|---|---|---:|---:|---:|
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q4_0/q4_0 | 88.0 | 0.0 | 0.00 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q8_0/tbq4 | 87.0 | 0.0 | 0.00 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | tbq4/tbq4 | 87.0 | 4971.6 | 64.61 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q4_0/q4_0 | 87.0 | 4343.0 | 70.05 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q8_0/tbq4 | 87.0 | 4096.6 | 67.76 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | tbq4/tbq4 | 86.0 | 3653.9 | 65.39 |

## Context Sweep

| run | host | ctx | model | config | reps | wall mean s | speedup vs Q4 | quality | RSS MB |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 111.256 | 0.0% | 0.917 | 5153.6 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 107.657 | 3.3% | 0.917 | 5178.9 |
| agent | x86_axelera_qwen_fix_smoke | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 105.716 | 5.2% | 0.833 | 5190.5 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 60.050 | 0.0% | 0.900 | 4837.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 58.571 | 2.5% | 0.900 | 4905.2 |
| qwen_fix_telemetry | x86_axelera_qwen_fix_telemetry | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 54.259 | 10.7% | 0.667 | 4868.5 |

## Claim Assessment

`tbq4/tbq4` supports the speed claim at 8K, but the deterministic quality rubric is not uniformly non-inferior to Q4.
`q8_0/tbq4` remains the conservative quality candidate because its quality delta is non-inferior in the aggregated slices.

Do not publish a strict-lossless claim from this evidence alone. The supported wording is `quality-preserving under the tested Gemma CPU edge-agent workload` or `near-lossless in this task suite`.

## Artifacts

- `aggregate_summary.csv`: repeated-run mean, stddev, CI95, Q4 speedup, quality, RSS, and CPU profile aggregates.
- `latency_breakdown.csv`: planner/tool/final/prompt/decode decomposition.
- `quality_noninferiority.csv`: paired task-level comparison against Q4.
