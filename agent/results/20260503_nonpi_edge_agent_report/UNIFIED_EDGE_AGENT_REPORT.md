# Unified TurboQuant Edge-Agent Paper Report

Generated: `2026-05-03T18:32:29`

## Input Runs

- `m4_fixed_core8k_battery`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260503_m4_fixed_core8k`; contexts=[8192]; repeats=1; tasks=5; threads=10
- `x86_axelera_fixed_core8k`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260503_x86_fixed_core8k`; contexts=[8192]; repeats=1; tasks=5; threads=6

## Key Findings

- Completed `20` benchmark jobs and `100` task executions. Server return-code failures in included summaries: `0`.
- Gemma 4B is the strongest current evidence: `tbq4/tbq4` is faster than Q4 in every included 8K Gemma slice, with speedups from 24.5% to 29.6% and quality deltas from 0.000 to 0.013.
- Qwen 3.5 4B on M4 is mixed for `tbq4/tbq4`: speedups range from 17.7% to 17.7%, while quality deltas range from 0.007 to 0.007.
- Qwen 3.5 4B on x86 no longer shows zero-valid-JSON 8K aggregate rows; `tbq4/tbq4` speedups range from 15.7% to 15.7% with quality deltas from -0.053 to -0.053.
- The evidence supports a narrower CPU edge-agent claim for Gemma and a tentative, workload-scoped optimization claim. It does not yet support a broad full-paper claim that TurboQuant is lossless across model families and CPU targets.

## 8K Q4 Baseline Comparison

Negative `vs Q4` means lower wall time than Q4. Positive `speedup` means faster than Q4.

| run | host | model | config | reps | wall mean s | wall CI95 | vs Q4 | speedup | quality | quality delta | JSON | RSS MB |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_core8k | m4_fixed_core8k_battery | gemma4_e4b | f16/f16 | 1 | 145.235 | 0.000 | -17.4% | 21.1% | 0.813 | 0.093 | 1.000 | 8400.9 |
| fixed_core8k | m4_fixed_core8k_battery | gemma4_e4b | q4_0/q4_0 | 1 | 175.877 | 0.000 | 0.0% | 0.0% | 0.720 | 0.000 | 1.000 | 7885.3 |
| fixed_core8k | m4_fixed_core8k_battery | gemma4_e4b | q8_0/q8_0 | 1 | 163.046 | 0.000 | -7.3% | 7.9% | 0.787 | 0.067 | 1.000 | 7995.9 |
| fixed_core8k | m4_fixed_core8k_battery | gemma4_e4b | q8_0/tbq4 | 1 | 142.921 | 0.000 | -18.7% | 23.1% | 0.787 | 0.067 | 1.000 | 8108.3 |
| fixed_core8k | m4_fixed_core8k_battery | gemma4_e4b | tbq4/tbq4 | 1 | 141.279 | 0.000 | -19.7% | 24.5% | 0.733 | 0.013 | 1.000 | 7896.2 |
| fixed_core8k | m4_fixed_core8k_battery | qwen35_4b | f16/f16 | 1 | 160.836 | 0.000 | -12.6% | 14.4% | 0.680 | -0.127 | 1.000 | 7783.0 |
| fixed_core8k | m4_fixed_core8k_battery | qwen35_4b | q4_0/q4_0 | 1 | 184.007 | 0.000 | 0.0% | 0.0% | 0.807 | 0.000 | 1.000 | 7072.3 |
| fixed_core8k | m4_fixed_core8k_battery | qwen35_4b | q8_0/q8_0 | 1 | 182.910 | 0.000 | -0.6% | 0.6% | 0.687 | -0.120 | 1.000 | 7323.2 |
| fixed_core8k | m4_fixed_core8k_battery | qwen35_4b | q8_0/tbq4 | 1 | 144.411 | 0.000 | -21.5% | 27.4% | 0.727 | -0.080 | 1.000 | 6889.9 |
| fixed_core8k | m4_fixed_core8k_battery | qwen35_4b | tbq4/tbq4 | 1 | 156.398 | 0.000 | -15.0% | 17.7% | 0.813 | 0.007 | 1.000 | 7070.2 |
| fixed_core8k | x86_axelera_fixed_core8k | gemma4_e4b | f16/f16 | 1 | 521.615 | 0.000 | -23.2% | 30.3% | 0.813 | 0.027 | 1.000 | 8715.4 |
| fixed_core8k | x86_axelera_fixed_core8k | gemma4_e4b | q4_0/q4_0 | 1 | 679.445 | 0.000 | 0.0% | 0.0% | 0.787 | 0.000 | 1.000 | 7702.8 |
| fixed_core8k | x86_axelera_fixed_core8k | gemma4_e4b | q8_0/q8_0 | 1 | 548.812 | 0.000 | -19.2% | 23.8% | 0.787 | 0.000 | 1.000 | 8055.9 |
| fixed_core8k | x86_axelera_fixed_core8k | gemma4_e4b | q8_0/tbq4 | 1 | 518.591 | 0.000 | -23.7% | 31.0% | 0.733 | -0.053 | 1.000 | 7883.9 |
| fixed_core8k | x86_axelera_fixed_core8k | gemma4_e4b | tbq4/tbq4 | 1 | 524.071 | 0.000 | -22.9% | 29.6% | 0.787 | 0.000 | 1.000 | 7693.0 |
| fixed_core8k | x86_axelera_fixed_core8k | qwen35_4b | f16/f16 | 1 | 496.801 | 0.000 | -23.1% | 30.0% | 0.700 | -0.073 | 1.000 | 6863.2 |
| fixed_core8k | x86_axelera_fixed_core8k | qwen35_4b | q4_0/q4_0 | 1 | 645.774 | 0.000 | 0.0% | 0.0% | 0.773 | 0.000 | 1.000 | 6313.0 |
| fixed_core8k | x86_axelera_fixed_core8k | qwen35_4b | q8_0/q8_0 | 1 | 583.972 | 0.000 | -9.6% | 10.6% | 0.693 | -0.080 | 1.000 | 6554.3 |
| fixed_core8k | x86_axelera_fixed_core8k | qwen35_4b | q8_0/tbq4 | 1 | 490.703 | 0.000 | -24.0% | 31.6% | 0.787 | 0.013 | 1.000 | 6334.2 |
| fixed_core8k | x86_axelera_fixed_core8k | qwen35_4b | tbq4/tbq4 | 1 | 558.373 | 0.000 | -13.5% | 15.7% | 0.720 | -0.053 | 1.000 | 6304.6 |

## Quality Non-Inferiority vs Q4

`JSON >= Q4` is a paired relative check; `config JSON` and `Q4 JSON` are the absolute validity rates.

| run | host | ctx | model | config | paired cases | quality >= Q4 | JSON >= Q4 | config JSON | Q4 JSON |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | f16/f16 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | f16/f16 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | f16/f16 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | f16/f16 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |

## Latency Decomposition

| run | host | ctx | model | config | planner s | deterministic tools s | LLM tools s | final s | prompt eval ms | decode ms |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | f16/f16 | 3.368 | 0.003 | 22.741 | 2.935 | 23999.8 | 5009.5 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q4_0/q4_0 | 3.725 | 0.003 | 28.120 | 3.328 | 29759.6 | 5397.6 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/q8_0 | 3.502 | 0.003 | 26.162 | 2.942 | 27535.1 | 5051.9 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/tbq4 | 3.121 | 0.003 | 22.566 | 2.894 | 23903.9 | 4663.0 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | tbq4/tbq4 | 3.422 | 0.002 | 22.048 | 2.783 | 23331.9 | 4906.1 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | f16/f16 | 5.567 | 0.003 | 23.049 | 3.547 | 24183.3 | 7924.1 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q4_0/q4_0 | 5.634 | 0.005 | 27.495 | 3.667 | 28805.0 | 7954.0 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/q8_0 | 5.640 | 0.003 | 27.086 | 3.853 | 28143.3 | 8397.5 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/tbq4 | 5.382 | 0.003 | 19.493 | 4.004 | 20774.2 | 8050.6 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | tbq4/tbq4 | 4.950 | 0.005 | 22.317 | 4.007 | 23592.3 | 7639.7 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | f16/f16 | 13.059 | 0.000 | 79.916 | 11.347 | 81620.4 | 22600.9 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q4_0/q4_0 | 14.787 | 0.000 | 107.853 | 13.248 | 111846.7 | 24006.6 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/q8_0 | 13.230 | 0.000 | 84.797 | 11.734 | 87326.0 | 22377.2 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/tbq4 | 13.121 | 0.000 | 78.960 | 11.637 | 81583.2 | 22085.9 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | tbq4/tbq4 | 13.441 | 0.000 | 79.568 | 11.805 | 82910.2 | 21866.6 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | f16/f16 | 21.271 | 0.000 | 64.329 | 13.760 | 64941.4 | 34254.8 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q4_0/q4_0 | 22.200 | 0.000 | 93.361 | 13.593 | 95660.5 | 33359.5 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/q8_0 | 21.272 | 0.000 | 81.307 | 14.215 | 82194.3 | 34455.3 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/tbq4 | 20.314 | 0.000 | 62.408 | 15.419 | 64303.2 | 33702.7 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | tbq4/tbq4 | 21.997 | 0.000 | 76.508 | 13.169 | 78319.4 | 33219.7 |

## Power And Thermal Telemetry

Telemetry is comparable only within the same device and controlled power/ambient conditions.
Zero joules/watts means the energy counter was unavailable or unreadable during that run, not zero power draw.
Battery columns are whole-system battery discharge estimates on macOS, not package or SoC power.

| run | host | ctx | model | config | max temp C | pkg joules | avg pkg W | batt joules | avg batt W |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | f16/f16 | 0.0 | 0.0 | 0.00 | 12829.0 | 87.62 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q4_0/q4_0 | 0.0 | 0.0 | 0.00 | 15258.4 | 85.25 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/q8_0 | 0.0 | 0.0 | 0.00 | 13925.2 | 85.54 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/tbq4 | 0.0 | 0.0 | 0.00 | 12336.8 | 85.45 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | tbq4/tbq4 | 0.0 | 0.0 | 0.00 | 12477.2 | 86.32 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | f16/f16 | 0.0 | 0.0 | 0.00 | 13550.9 | 83.28 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q4_0/q4_0 | 0.0 | 0.0 | 0.00 | 12878.7 | 69.66 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/q8_0 | 0.0 | 0.0 | 0.00 | 13682.1 | 74.65 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/tbq4 | 0.0 | 0.0 | 0.00 | 9487.8 | 64.53 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | tbq4/tbq4 | 0.0 | 0.0 | 0.00 | 13201.7 | 84.17 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | f16/f16 | 86.0 | 34041.3 | 65.02 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q4_0/q4_0 | 87.0 | 44364.1 | 65.03 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/q8_0 | 88.0 | 35845.5 | 65.07 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/tbq4 | 88.0 | 33830.6 | 64.99 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | tbq4/tbq4 | 88.0 | 34276.4 | 65.09 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | f16/f16 | 87.0 | 32335.2 | 64.78 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q4_0/q4_0 | 86.0 | 42034.0 | 64.89 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/q8_0 | 88.0 | 38003.8 | 64.96 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/tbq4 | 87.0 | 33081.5 | 67.25 | 0.0 | 0.00 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | tbq4/tbq4 | 87.0 | 36345.3 | 64.93 | 0.0 | 0.00 |

## Context Sweep

| run | host | ctx | model | config | reps | wall mean s | speedup vs Q4 | quality | RSS MB |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | f16/f16 | 1 | 145.235 | 21.1% | 0.813 | 8400.9 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 175.877 | 0.0% | 0.720 | 7885.3 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 163.046 | 7.9% | 0.787 | 7995.9 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 142.921 | 23.1% | 0.787 | 8108.3 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 141.279 | 24.5% | 0.733 | 7896.2 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | f16/f16 | 1 | 160.836 | 14.4% | 0.680 | 7783.0 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 184.007 | 0.0% | 0.807 | 7072.3 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 182.910 | 0.6% | 0.687 | 7323.2 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 144.411 | 27.4% | 0.727 | 6889.9 |
| fixed_core8k | m4_fixed_core8k_battery | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 156.398 | 17.7% | 0.813 | 7070.2 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | f16/f16 | 1 | 521.615 | 30.3% | 0.813 | 8715.4 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 679.445 | 0.0% | 0.787 | 7702.8 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 548.812 | 23.8% | 0.787 | 8055.9 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 518.591 | 31.0% | 0.733 | 7883.9 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 524.071 | 29.6% | 0.787 | 7693.0 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | f16/f16 | 1 | 496.801 | 30.0% | 0.700 | 6863.2 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 645.774 | 0.0% | 0.773 | 6313.0 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 583.972 | 10.6% | 0.693 | 6554.3 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 490.703 | 31.6% | 0.787 | 6334.2 |
| fixed_core8k | x86_axelera_fixed_core8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 558.373 | 15.7% | 0.720 | 6304.6 |

## Claim Assessment

`tbq4/tbq4` supports the speed claim at 8K, but the deterministic quality rubric is not uniformly non-inferior to Q4.
`q8_0/tbq4` should remain exploratory until the quality deltas are consistently non-inferior.

Do not publish a strict-lossless claim from this evidence alone. The supported wording is `quality-preserving under the tested Gemma CPU edge-agent workload` or `near-lossless in this task suite`.

## Artifacts

- `aggregate_summary.csv`: repeated-run mean, stddev, CI95, Q4 speedup, quality, RSS, and CPU profile aggregates.
- `latency_breakdown.csv`: planner/tool/final/prompt/decode decomposition.
- `quality_noninferiority.csv`: paired task-level comparison against Q4.
