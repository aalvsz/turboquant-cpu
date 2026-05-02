# Unified TurboQuant Edge-Agent Paper Report

Generated: `2026-05-02T16:24:53`

## Input Runs

- `m4_paper`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_094633_m4_paper`; contexts=[8192]; repeats=5; tasks=5; threads=10
- `m4_paper_suite25`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_103544_m4_paper_suite25`; contexts=[8192]; repeats=1; tasks=25; threads=10
- `m4_paper_ctx`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_110623_m4_paper_ctx`; contexts=[2048, 4096, 8192]; repeats=1; tasks=5; threads=10
- `x86_axelera_paper`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_094909_x86_axelera_paper`; contexts=[8192]; repeats=5; tasks=5; threads=6
- `x86_axelera_suite25`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_124731_x86_axelera_suite25`; contexts=[8192]; repeats=1; tasks=25; threads=6
- `x86_axelera_ctx`: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_143814_x86_axelera_ctx`; contexts=[2048, 4096, 8192]; repeats=1; tasks=5; threads=6

## Key Findings

- Completed `180` benchmark jobs and `1300` task executions. Server return-code failures in included summaries: `0`.
- Gemma 4B is the strongest current evidence: `tbq4/tbq4` is faster than Q4 in every included 8K Gemma slice, with speedups from 8.4% to 17.0% and quality deltas from -0.027 to 0.085.
- Qwen 3.5 4B on M4 is mixed for `tbq4/tbq4`: speedups range from -4.2% to 9.8%, while quality deltas range from -0.100 to -0.029.
- Qwen 3.5 4B on x86 produced `JSON=0.000` for `15`/`15` 8K aggregate rows across every KV config. Treat those rows as a Qwen/x86 serving-path issue, not as quality evidence for or against TurboQuant.
- The evidence supports a narrower CPU edge-agent claim for Gemma and a tentative, workload-scoped optimization claim. It does not yet support a broad full-paper claim that TurboQuant is lossless across model families and CPU targets.

## 8K Q4 Baseline Comparison

Negative `vs Q4` means lower wall time than Q4. Positive `speedup` means faster than Q4.

| run | host | model | config | reps | wall mean s | wall CI95 | vs Q4 | speedup | quality | quality delta | JSON | RSS MB |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctx_sweep | m4_paper_ctx | gemma4_e4b | f16/f16 | 1 | 55.676 | 0.000 | -11.1% | 12.5% | 0.827 | 0.013 | 1.000 | 8516.1 |
| ctx_sweep | m4_paper_ctx | gemma4_e4b | q4_0/q4_0 | 1 | 62.613 | 0.000 | 0.0% | 0.0% | 0.813 | 0.000 | 1.000 | 7818.8 |
| ctx_sweep | m4_paper_ctx | gemma4_e4b | q8_0/q8_0 | 1 | 60.612 | 0.000 | -3.2% | 3.3% | 0.827 | 0.013 | 1.000 | 8118.6 |
| ctx_sweep | m4_paper_ctx | gemma4_e4b | q8_0/tbq4 | 1 | 55.719 | 0.000 | -11.0% | 12.4% | 0.813 | 0.000 | 1.000 | 7939.9 |
| ctx_sweep | m4_paper_ctx | gemma4_e4b | tbq4/tbq4 | 1 | 55.201 | 0.000 | -11.8% | 13.4% | 0.827 | 0.013 | 1.000 | 7804.6 |
| ctx_sweep | m4_paper_ctx | qwen35_4b | f16/f16 | 1 | 58.670 | 0.000 | -10.4% | 11.6% | 0.773 | 0.013 | 1.000 | 6828.2 |
| ctx_sweep | m4_paper_ctx | qwen35_4b | q4_0/q4_0 | 1 | 65.490 | 0.000 | 0.0% | 0.0% | 0.760 | 0.000 | 1.000 | 6412.6 |
| ctx_sweep | m4_paper_ctx | qwen35_4b | q8_0/q8_0 | 1 | 61.541 | 0.000 | -6.0% | 6.4% | 0.713 | -0.047 | 1.000 | 6554.7 |
| ctx_sweep | m4_paper_ctx | qwen35_4b | q8_0/tbq4 | 1 | 59.138 | 0.000 | -9.7% | 10.7% | 0.827 | 0.067 | 1.000 | 6484.5 |
| ctx_sweep | m4_paper_ctx | qwen35_4b | tbq4/tbq4 | 1 | 59.664 | 0.000 | -8.9% | 9.8% | 0.660 | -0.100 | 1.000 | 6410.2 |
| ctx_sweep | x86_axelera_ctx | gemma4_e4b | f16/f16 | 1 | 228.456 | 0.000 | -12.4% | 14.1% | 0.827 | 0.020 | 1.000 | 8271.5 |
| ctx_sweep | x86_axelera_ctx | gemma4_e4b | q4_0/q4_0 | 1 | 260.660 | 0.000 | 0.0% | 0.0% | 0.807 | 0.000 | 1.000 | 7591.0 |
| ctx_sweep | x86_axelera_ctx | gemma4_e4b | q8_0/q8_0 | 1 | 234.275 | 0.000 | -10.1% | 11.3% | 0.760 | -0.047 | 1.000 | 7871.8 |
| ctx_sweep | x86_axelera_ctx | gemma4_e4b | q8_0/tbq4 | 1 | 223.909 | 0.000 | -14.1% | 16.4% | 0.813 | 0.007 | 1.000 | 7733.2 |
| ctx_sweep | x86_axelera_ctx | gemma4_e4b | tbq4/tbq4 | 1 | 222.766 | 0.000 | -14.5% | 17.0% | 0.780 | -0.027 | 1.000 | 7588.5 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | f16/f16 | 1 | 213.220 | 0.000 | -17.2% | 20.7% | 0.360 | 0.000 | 0.000 | 6037.2 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q4_0/q4_0 | 1 | 257.415 | 0.000 | 0.0% | 0.0% | 0.360 | 0.000 | 0.000 | 5620.2 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q8_0/q8_0 | 1 | 215.558 | 0.000 | -16.3% | 19.4% | 0.360 | 0.000 | 0.000 | 5763.4 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q8_0/tbq4 | 1 | 198.447 | 0.000 | -22.9% | 29.7% | 0.360 | -0.000 | 0.000 | 5692.2 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | tbq4/tbq4 | 1 | 207.090 | 0.000 | -19.6% | 24.3% | 0.360 | -0.000 | 0.000 | 5618.9 |
| repeat_core8k | m4_paper | gemma4_e4b | f16/f16 | 5 | 55.640 | 20.557 | 19.1% | -16.1% | 0.781 | 0.000 | 1.000 | 8382.3 |
| repeat_core8k | m4_paper | gemma4_e4b | q4_0/q4_0 | 5 | 46.707 | 2.071 | 0.0% | 0.0% | 0.781 | 0.000 | 0.880 | 7701.4 |
| repeat_core8k | m4_paper | gemma4_e4b | q8_0/q8_0 | 5 | 47.483 | 2.246 | 1.7% | -1.6% | 0.779 | -0.003 | 1.000 | 7968.9 |
| repeat_core8k | m4_paper | gemma4_e4b | q8_0/tbq4 | 5 | 52.935 | 17.183 | 13.3% | -11.8% | 0.803 | 0.021 | 1.000 | 7755.2 |
| repeat_core8k | m4_paper | gemma4_e4b | tbq4/tbq4 | 5 | 43.069 | 0.690 | -7.8% | 8.4% | 0.795 | 0.013 | 1.000 | 7746.1 |
| repeat_core8k | m4_paper | qwen35_4b | f16/f16 | 5 | 52.676 | 1.310 | -3.7% | 3.8% | 0.819 | -0.007 | 1.000 | 7165.3 |
| repeat_core8k | m4_paper | qwen35_4b | q4_0/q4_0 | 5 | 54.693 | 1.811 | 0.0% | 0.0% | 0.825 | 0.000 | 1.000 | 6858.2 |
| repeat_core8k | m4_paper | qwen35_4b | q8_0/q8_0 | 5 | 54.447 | 1.972 | -0.4% | 0.5% | 0.819 | -0.007 | 1.000 | 6992.1 |
| repeat_core8k | m4_paper | qwen35_4b | q8_0/tbq4 | 5 | 67.812 | 22.647 | 24.0% | -19.3% | 0.867 | 0.041 | 1.000 | 6898.9 |
| repeat_core8k | m4_paper | qwen35_4b | tbq4/tbq4 | 5 | 52.340 | 1.301 | -4.3% | 4.5% | 0.796 | -0.029 | 1.000 | 6877.8 |
| repeat_core8k | x86_axelera_paper | gemma4_e4b | f16/f16 | 5 | 180.047 | 0.693 | -9.7% | 10.8% | 0.789 | 0.056 | 1.000 | 8225.3 |
| repeat_core8k | x86_axelera_paper | gemma4_e4b | q4_0/q4_0 | 5 | 199.426 | 2.937 | 0.0% | 0.0% | 0.733 | 0.000 | 0.960 | 7531.9 |
| repeat_core8k | x86_axelera_paper | gemma4_e4b | q8_0/q8_0 | 5 | 178.320 | 1.067 | -10.6% | 11.8% | 0.805 | 0.072 | 1.000 | 7815.0 |
| repeat_core8k | x86_axelera_paper | gemma4_e4b | q8_0/tbq4 | 5 | 173.236 | 2.136 | -13.1% | 15.1% | 0.784 | 0.051 | 1.000 | 7659.2 |
| repeat_core8k | x86_axelera_paper | gemma4_e4b | tbq4/tbq4 | 5 | 180.612 | 0.892 | -9.4% | 10.4% | 0.819 | 0.085 | 1.000 | 7536.1 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | f16/f16 | 5 | 188.184 | 12.262 | -3.0% | 3.1% | 0.360 | 0.000 | 0.000 | 6424.9 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q4_0/q4_0 | 5 | 193.993 | 12.907 | 0.0% | 0.0% | 0.360 | 0.000 | 0.000 | 6088.8 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q8_0/q8_0 | 5 | 198.909 | 14.084 | 2.5% | -2.5% | 0.360 | 0.000 | 0.000 | 6207.4 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q8_0/tbq4 | 5 | 200.153 | 7.493 | 3.2% | -3.1% | 0.360 | 0.000 | 0.000 | 6145.0 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | tbq4/tbq4 | 5 | 205.237 | 10.072 | 5.8% | -5.5% | 0.365 | 0.005 | 0.000 | 6088.8 |
| suite25_8k | m4_paper_suite25 | gemma4_e4b | f16/f16 | 1 | 130.071 | 0.000 | -10.3% | 11.5% | 0.829 | -0.019 | 0.960 | 9653.8 |
| suite25_8k | m4_paper_suite25 | gemma4_e4b | q4_0/q4_0 | 1 | 145.064 | 0.000 | 0.0% | 0.0% | 0.848 | 0.000 | 0.920 | 8300.4 |
| suite25_8k | m4_paper_suite25 | gemma4_e4b | q8_0/q8_0 | 1 | 139.970 | 0.000 | -3.5% | 3.6% | 0.845 | -0.003 | 0.960 | 8941.6 |
| suite25_8k | m4_paper_suite25 | gemma4_e4b | q8_0/tbq4 | 1 | 127.569 | 0.000 | -12.1% | 13.7% | 0.857 | 0.009 | 1.000 | 8625.6 |
| suite25_8k | m4_paper_suite25 | gemma4_e4b | tbq4/tbq4 | 1 | 126.752 | 0.000 | -12.6% | 14.4% | 0.849 | 0.001 | 0.960 | 8386.8 |
| suite25_8k | m4_paper_suite25 | qwen35_4b | f16/f16 | 1 | 149.867 | 0.000 | -2.1% | 2.1% | 0.860 | -0.036 | 1.000 | 10276.6 |
| suite25_8k | m4_paper_suite25 | qwen35_4b | q4_0/q4_0 | 1 | 153.008 | 0.000 | 0.0% | 0.0% | 0.896 | 0.000 | 1.000 | 9625.3 |
| suite25_8k | m4_paper_suite25 | qwen35_4b | q8_0/q8_0 | 1 | 149.157 | 0.000 | -2.5% | 2.6% | 0.867 | -0.029 | 1.000 | 9863.3 |
| suite25_8k | m4_paper_suite25 | qwen35_4b | q8_0/tbq4 | 1 | 156.609 | 0.000 | 2.4% | -2.3% | 0.864 | -0.032 | 1.000 | 9730.6 |
| suite25_8k | m4_paper_suite25 | qwen35_4b | tbq4/tbq4 | 1 | 159.708 | 0.000 | 4.4% | -4.2% | 0.857 | -0.039 | 1.000 | 9636.8 |
| suite25_8k | x86_axelera_suite25 | gemma4_e4b | f16/f16 | 1 | 552.355 | 0.000 | -7.6% | 8.2% | 0.859 | 0.001 | 1.000 | 10150.3 |
| suite25_8k | x86_axelera_suite25 | gemma4_e4b | q4_0/q4_0 | 1 | 597.549 | 0.000 | 0.0% | 0.0% | 0.857 | 0.000 | 0.920 | 8044.8 |
| suite25_8k | x86_axelera_suite25 | gemma4_e4b | q8_0/q8_0 | 1 | 550.537 | 0.000 | -7.9% | 8.5% | 0.849 | -0.008 | 1.000 | 8729.2 |
| suite25_8k | x86_axelera_suite25 | gemma4_e4b | q8_0/tbq4 | 1 | 537.622 | 0.000 | -10.0% | 11.1% | 0.859 | 0.001 | 1.000 | 8388.4 |
| suite25_8k | x86_axelera_suite25 | gemma4_e4b | tbq4/tbq4 | 1 | 541.270 | 0.000 | -9.4% | 10.4% | 0.876 | 0.019 | 1.000 | 8138.3 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | f16/f16 | 1 | 585.101 | 0.000 | -2.1% | 2.1% | 0.371 | -0.003 | 0.000 | 9436.6 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q4_0/q4_0 | 1 | 597.607 | 0.000 | 0.0% | 0.0% | 0.373 | 0.000 | 0.000 | 8814.3 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q8_0/q8_0 | 1 | 612.202 | 0.000 | 2.4% | -2.4% | 0.372 | -0.001 | 0.000 | 9035.5 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q8_0/tbq4 | 1 | 607.193 | 0.000 | 1.6% | -1.6% | 0.368 | -0.005 | 0.000 | 8926.6 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | tbq4/tbq4 | 1 | 641.579 | 0.000 | 7.4% | -6.9% | 0.372 | -0.001 | 0.000 | 8820.7 |

## Evidence Validity Flags

Rows below had zero valid final JSON and are excluded from quality-claim interpretation even when their paired Q4 comparison appears non-inferior.

| run | host | model | config | speedup vs Q4 | quality | JSON |
|---|---|---|---|---:|---:|---:|
| ctx_sweep | x86_axelera_ctx | qwen35_4b | f16/f16 | 20.7% | 0.360 | 0.000 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q4_0/q4_0 | 0.0% | 0.360 | 0.000 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q8_0/q8_0 | 19.4% | 0.360 | 0.000 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | q8_0/tbq4 | 29.7% | 0.360 | 0.000 |
| ctx_sweep | x86_axelera_ctx | qwen35_4b | tbq4/tbq4 | 24.3% | 0.360 | 0.000 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | f16/f16 | 3.1% | 0.360 | 0.000 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q4_0/q4_0 | 0.0% | 0.360 | 0.000 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q8_0/q8_0 | -2.5% | 0.360 | 0.000 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | q8_0/tbq4 | -3.1% | 0.360 | 0.000 |
| repeat_core8k | x86_axelera_paper | qwen35_4b | tbq4/tbq4 | -5.5% | 0.365 | 0.000 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | f16/f16 | 2.1% | 0.371 | 0.000 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q4_0/q4_0 | 0.0% | 0.373 | 0.000 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q8_0/q8_0 | -2.4% | 0.372 | 0.000 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | q8_0/tbq4 | -1.6% | 0.368 | 0.000 |
| suite25_8k | x86_axelera_suite25 | qwen35_4b | tbq4/tbq4 | -6.9% | 0.372 | 0.000 |

## Quality Non-Inferiority vs Q4

`JSON >= Q4` is a paired relative check; `config JSON` and `Q4 JSON` are the absolute validity rates.

| run | host | ctx | model | config | paired cases | quality >= Q4 | JSON >= Q4 | config JSON | Q4 JSON |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | f16/f16 | 5 | 0.800 | 1.000 | 1.000 | 0.800 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 1.000 | 1.000 | 0.800 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | q8_0/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 0.800 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | tbq4/tbq4 | 5 | 0.600 | 1.000 | 0.800 | 0.800 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | f16/f16 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | tbq4/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | f16/f16 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | q8_0/q8_0 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | q8_0/tbq4 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | f16/f16 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | q8_0/q8_0 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | q8_0/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | f16/f16 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | f16/f16 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | f16/f16 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | q8_0/q8_0 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 0.800 | 0.800 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | tbq4/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | f16/f16 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | f16/f16 | 5 | 0.200 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | q8_0/q8_0 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | q8_0/tbq4 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | tbq4/tbq4 | 5 | 0.400 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | f16/f16 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | f16/f16 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 0.600 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 1.000 | 1.000 | 1.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | f16/f16 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 1.000 | 1.000 | 0.000 | 0.000 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | f16/f16 | 25 | 0.760 | 1.000 | 1.000 | 0.880 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 25 | 0.680 | 1.000 | 1.000 | 0.880 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 25 | 0.800 | 1.000 | 1.000 | 0.880 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 25 | 0.720 | 1.000 | 1.000 | 0.880 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | f16/f16 | 25 | 0.760 | 1.000 | 1.000 | 1.000 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/q8_0 | 25 | 0.760 | 1.000 | 1.000 | 1.000 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/tbq4 | 25 | 0.840 | 1.000 | 1.000 | 1.000 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | tbq4/tbq4 | 25 | 0.560 | 1.000 | 1.000 | 1.000 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | f16/f16 | 25 | 0.840 | 1.000 | 1.000 | 0.960 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 25 | 0.920 | 1.000 | 1.000 | 0.960 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 25 | 0.880 | 1.000 | 1.000 | 0.960 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 25 | 0.800 | 1.000 | 1.000 | 0.960 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | f16/f16 | 25 | 1.000 | 1.000 | 0.000 | 0.000 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/q8_0 | 25 | 1.000 | 1.000 | 0.000 | 0.000 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/tbq4 | 25 | 1.000 | 1.000 | 0.000 | 0.000 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | tbq4/tbq4 | 25 | 1.000 | 1.000 | 0.000 | 0.000 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | f16/f16 | 25 | 0.800 | 1.000 | 0.960 | 0.920 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 25 | 0.880 | 1.000 | 0.960 | 0.920 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 25 | 0.840 | 1.000 | 1.000 | 0.920 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 25 | 0.840 | 0.960 | 0.960 | 0.920 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | f16/f16 | 25 | 0.760 | 1.000 | 1.000 | 1.000 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 25 | 0.840 | 1.000 | 1.000 | 1.000 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 25 | 0.760 | 1.000 | 1.000 | 1.000 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 25 | 0.720 | 1.000 | 1.000 | 1.000 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | f16/f16 | 25 | 0.760 | 1.000 | 1.000 | 0.920 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 25 | 0.760 | 1.000 | 1.000 | 0.920 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 25 | 0.720 | 1.000 | 1.000 | 0.920 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 25 | 0.840 | 1.000 | 1.000 | 0.920 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | f16/f16 | 25 | 0.960 | 1.000 | 0.000 | 0.000 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 25 | 0.920 | 1.000 | 0.000 | 0.000 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 25 | 0.920 | 1.000 | 0.000 | 0.000 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 25 | 0.920 | 1.000 | 0.000 | 0.000 |

## Latency Decomposition

| run | host | ctx | model | config | planner s | deterministic tools s | LLM tools s | final s | prompt eval ms | decode ms |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | f16/f16 | 0.000 | 0.000 | 7.997 | 3.138 | 8657.7 | 2463.1 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q4_0/q4_0 | 0.000 | 0.000 | 9.168 | 3.354 | 9918.8 | 2596.7 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 0.000 | 0.000 | 8.853 | 3.269 | 9553.4 | 2559.0 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 0.000 | 0.000 | 8.029 | 3.114 | 8664.0 | 2471.6 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 0.000 | 0.000 | 7.972 | 3.068 | 8575.2 | 2457.5 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | f16/f16 | 0.000 | 0.000 | 8.259 | 3.475 | 8815.7 | 2894.7 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q4_0/q4_0 | 0.000 | 0.000 | 9.692 | 3.405 | 10353.9 | 2723.5 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 0.000 | 0.000 | 8.944 | 3.363 | 9529.3 | 2751.6 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 0.000 | 0.000 | 8.441 | 3.386 | 9016.5 | 2790.9 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 0.000 | 0.000 | 8.439 | 3.494 | 9035.6 | 2877.6 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | f16/f16 | 0.000 | 0.000 | 32.224 | 13.467 | 33935.3 | 11687.8 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q4_0/q4_0 | 0.000 | 0.000 | 37.655 | 14.477 | 40094.4 | 12011.7 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 0.000 | 0.000 | 33.269 | 13.586 | 35127.2 | 11686.5 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 0.000 | 0.000 | 31.503 | 13.279 | 33386.1 | 11363.7 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 0.000 | 0.000 | 31.550 | 13.003 | 33377.7 | 11150.0 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | f16/f16 | 0.000 | 0.000 | 31.178 | 11.466 | 33560.2 | 8984.9 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q4_0/q4_0 | 0.000 | 0.000 | 34.240 | 17.243 | 36800.1 | 14597.0 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 0.000 | 0.000 | 30.916 | 12.195 | 34089.9 | 8931.9 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 0.000 | 0.000 | 30.480 | 9.209 | 33720.8 | 5881.9 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 0.000 | 0.000 | 32.443 | 8.974 | 33724.2 | 7610.1 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | f16/f16 | 3.994 | 0.003 | 3.222 | 3.908 | 6058.3 | 5043.7 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q4_0/q4_0 | 3.351 | 0.000 | 2.694 | 3.296 | 5346.6 | 3985.9 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 3.402 | 0.002 | 2.670 | 3.422 | 5269.7 | 4211.4 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 3.970 | 0.000 | 3.073 | 3.544 | 5856.5 | 4719.7 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 3.196 | 0.003 | 2.532 | 2.883 | 4841.4 | 3760.8 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | f16/f16 | 3.925 | 0.000 | 3.155 | 3.454 | 5889.5 | 4609.3 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q4_0/q4_0 | 4.055 | 0.000 | 3.208 | 3.675 | 6085.6 | 4821.7 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/q8_0 | 4.105 | 0.000 | 3.258 | 3.527 | 6143.1 | 4714.5 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/tbq4 | 4.889 | 0.000 | 3.891 | 4.781 | 7114.7 | 6407.1 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | tbq4/tbq4 | 3.898 | 0.000 | 3.125 | 3.444 | 5870.8 | 4564.9 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | f16/f16 | 12.902 | 0.000 | 10.372 | 12.735 | 18655.5 | 17287.9 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q4_0/q4_0 | 14.473 | 0.000 | 10.954 | 14.457 | 21791.9 | 18069.0 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 13.026 | 0.000 | 10.425 | 12.212 | 18797.5 | 16824.3 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 12.595 | 0.000 | 10.195 | 11.857 | 18305.4 | 16309.5 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 12.992 | 0.000 | 10.234 | 12.896 | 18958.3 | 17139.4 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | f16/f16 | 14.235 | 0.000 | 11.607 | 11.794 | 20744.3 | 16760.1 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q4_0/q4_0 | 11.976 | 0.000 | 12.370 | 14.452 | 21662.4 | 17016.1 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/q8_0 | 12.683 | 0.000 | 12.204 | 14.895 | 20902.8 | 18754.5 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/tbq4 | 14.259 | 0.000 | 11.349 | 14.422 | 20629.3 | 19280.7 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | tbq4/tbq4 | 14.257 | 0.000 | 10.976 | 15.814 | 20835.0 | 20092.6 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | f16/f16 | 0.000 | 0.001 | 2.074 | 3.127 | 2789.8 | 2398.3 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q4_0/q4_0 | 0.000 | 0.001 | 2.192 | 3.609 | 3011.1 | 2784.2 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 0.000 | 0.001 | 2.187 | 3.410 | 2979.8 | 2610.2 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 0.000 | 0.001 | 2.016 | 3.086 | 2698.1 | 2397.2 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 0.000 | 0.001 | 2.026 | 3.043 | 2722.2 | 2340.7 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | f16/f16 | 0.000 | 0.001 | 2.711 | 3.283 | 3377.4 | 2594.3 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q4_0/q4_0 | 0.000 | 0.001 | 2.806 | 3.312 | 3508.9 | 2595.4 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 0.000 | 0.001 | 2.726 | 3.239 | 3434.8 | 2514.6 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 0.000 | 0.001 | 2.815 | 3.448 | 3514.3 | 2726.1 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 0.000 | 0.001 | 2.838 | 3.549 | 3539.5 | 2828.7 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | f16/f16 | 0.000 | 0.000 | 8.835 | 13.259 | 10856.5 | 11188.9 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q4_0/q4_0 | 0.000 | 0.000 | 9.071 | 14.831 | 11809.2 | 12075.7 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 0.000 | 0.000 | 8.700 | 13.321 | 10890.9 | 11102.9 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 0.000 | 0.000 | 8.568 | 12.937 | 10464.0 | 11018.8 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 0.000 | 0.000 | 8.651 | 12.999 | 10708.4 | 10923.9 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | f16/f16 | 0.000 | 0.000 | 10.499 | 12.905 | 12580.5 | 10730.4 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q4_0/q4_0 | 0.000 | 0.000 | 10.621 | 13.283 | 13247.1 | 10573.4 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 0.000 | 0.000 | 10.659 | 13.828 | 12745.8 | 11656.0 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 0.000 | 0.000 | 9.619 | 14.668 | 12080.5 | 12123.3 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 0.000 | 0.000 | 10.348 | 15.315 | 12654.8 | 12924.4 |

## Context Sweep

| run | host | ctx | model | config | reps | wall mean s | speedup vs Q4 | quality | RSS MB |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | f16/f16 | 1 | 28.565 | 6.6% | 0.827 | 8102.4 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | q4_0/q4_0 | 1 | 30.453 | 0.0% | 0.773 | 7664.2 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | q8_0/q8_0 | 1 | 29.319 | 3.9% | 0.813 | 7834.5 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | q8_0/tbq4 | 1 | 27.194 | 12.0% | 0.787 | 7719.3 |
| ctx_sweep | m4_paper_ctx | 2048 | gemma4_e4b | tbq4/tbq4 | 1 | 28.619 | 6.4% | 0.747 | 7667.2 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | f16/f16 | 1 | 32.239 | -0.9% | 0.840 | 6440.2 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | q4_0/q4_0 | 1 | 31.962 | 0.0% | 0.813 | 6297.0 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | q8_0/q8_0 | 1 | 32.017 | -0.2% | 0.840 | 6340.2 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | q8_0/tbq4 | 1 | 33.948 | -5.8% | 0.860 | 6335.0 |
| ctx_sweep | m4_paper_ctx | 2048 | qwen35_4b | tbq4/tbq4 | 1 | 32.456 | -1.5% | 0.767 | 6303.4 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | f16/f16 | 1 | 39.599 | 3.7% | 0.760 | 8207.5 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | q4_0/q4_0 | 1 | 41.054 | 0.0% | 0.773 | 7713.2 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | q8_0/q8_0 | 1 | 38.428 | 6.8% | 0.733 | 7913.8 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | q8_0/tbq4 | 1 | 36.038 | 13.9% | 0.787 | 7814.8 |
| ctx_sweep | m4_paper_ctx | 4096 | gemma4_e4b | tbq4/tbq4 | 1 | 35.867 | 14.5% | 0.800 | 7727.2 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | f16/f16 | 1 | 39.336 | 2.7% | 0.707 | 6565.6 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | q4_0/q4_0 | 1 | 40.408 | 0.0% | 0.720 | 6337.2 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | q8_0/q8_0 | 1 | 42.958 | -5.9% | 0.747 | 6409.5 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | q8_0/tbq4 | 1 | 41.089 | -1.7% | 0.753 | 6381.3 |
| ctx_sweep | m4_paper_ctx | 4096 | qwen35_4b | tbq4/tbq4 | 1 | 40.337 | 0.2% | 0.773 | 6335.4 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | f16/f16 | 1 | 55.676 | 12.5% | 0.827 | 8516.1 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 62.613 | 0.0% | 0.813 | 7818.8 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 60.612 | 3.3% | 0.827 | 8118.6 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 55.719 | 12.4% | 0.813 | 7939.9 |
| ctx_sweep | m4_paper_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 55.201 | 13.4% | 0.827 | 7804.6 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | f16/f16 | 1 | 58.670 | 11.6% | 0.773 | 6828.2 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 65.490 | 0.0% | 0.760 | 6412.6 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 61.541 | 6.4% | 0.713 | 6554.7 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 59.138 | 10.7% | 0.827 | 6484.5 |
| ctx_sweep | m4_paper_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 59.664 | 9.8% | 0.660 | 6410.2 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | f16/f16 | 1 | 118.402 | 8.6% | 0.827 | 7860.6 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | q4_0/q4_0 | 1 | 128.549 | 0.0% | 0.827 | 7416.7 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | q8_0/q8_0 | 1 | 118.529 | 8.5% | 0.760 | 7595.0 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | q8_0/tbq4 | 1 | 120.586 | 6.6% | 0.787 | 7503.5 |
| ctx_sweep | x86_axelera_ctx | 2048 | gemma4_e4b | tbq4/tbq4 | 1 | 118.205 | 8.8% | 0.813 | 7429.8 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | f16/f16 | 1 | 116.407 | 7.8% | 0.360 | 5648.7 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | q4_0/q4_0 | 1 | 125.541 | 0.0% | 0.360 | 5508.1 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | q8_0/q8_0 | 1 | 113.964 | 10.2% | 0.360 | 5555.4 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | q8_0/tbq4 | 1 | 103.791 | 21.0% | 0.360 | 5527.5 |
| ctx_sweep | x86_axelera_ctx | 2048 | qwen35_4b | tbq4/tbq4 | 1 | 148.890 | -15.7% | 0.360 | 5508.0 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | f16/f16 | 1 | 155.298 | 12.7% | 0.747 | 8041.8 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | q4_0/q4_0 | 1 | 174.950 | 0.0% | 0.853 | 7475.8 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | q8_0/q8_0 | 1 | 156.339 | 11.9% | 0.773 | 7667.2 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | q8_0/tbq4 | 1 | 149.331 | 17.2% | 0.827 | 7575.9 |
| ctx_sweep | x86_axelera_ctx | 4096 | gemma4_e4b | tbq4/tbq4 | 1 | 150.487 | 16.3% | 0.787 | 7469.6 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | f16/f16 | 1 | 128.680 | 20.0% | 0.360 | 5769.6 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | q4_0/q4_0 | 1 | 154.464 | 0.0% | 0.360 | 5545.1 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | q8_0/q8_0 | 1 | 160.814 | -3.9% | 0.360 | 5623.0 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | q8_0/tbq4 | 1 | 142.405 | 8.5% | 0.360 | 5587.2 |
| ctx_sweep | x86_axelera_ctx | 4096 | qwen35_4b | tbq4/tbq4 | 1 | 155.142 | -0.4% | 0.360 | 5547.4 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | f16/f16 | 1 | 228.456 | 14.1% | 0.827 | 8271.5 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 260.660 | 0.0% | 0.807 | 7591.0 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 234.275 | 11.3% | 0.760 | 7871.8 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 223.909 | 16.4% | 0.813 | 7733.2 |
| ctx_sweep | x86_axelera_ctx | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 222.766 | 17.0% | 0.780 | 7588.5 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | f16/f16 | 1 | 213.220 | 20.7% | 0.360 | 6037.2 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 257.415 | 0.0% | 0.360 | 5620.2 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 215.558 | 19.4% | 0.360 | 5763.4 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 198.447 | 29.7% | 0.360 | 5692.2 |
| ctx_sweep | x86_axelera_ctx | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 207.090 | 24.3% | 0.360 | 5618.9 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | f16/f16 | 5 | 55.640 | -16.1% | 0.781 | 8382.3 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q4_0/q4_0 | 5 | 46.707 | 0.0% | 0.781 | 7701.4 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 47.483 | -1.6% | 0.779 | 7968.9 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 52.935 | -11.8% | 0.803 | 7755.2 |
| repeat_core8k | m4_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 43.069 | 8.4% | 0.795 | 7746.1 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | f16/f16 | 5 | 52.676 | 3.8% | 0.819 | 7165.3 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q4_0/q4_0 | 5 | 54.693 | 0.0% | 0.825 | 6858.2 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 54.447 | 0.5% | 0.819 | 6992.1 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 67.812 | -19.3% | 0.867 | 6898.9 |
| repeat_core8k | m4_paper | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 52.340 | 4.5% | 0.796 | 6877.8 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | f16/f16 | 5 | 180.047 | 10.8% | 0.789 | 8225.3 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q4_0/q4_0 | 5 | 199.426 | 0.0% | 0.733 | 7531.9 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/q8_0 | 5 | 178.320 | 11.8% | 0.805 | 7815.0 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | q8_0/tbq4 | 5 | 173.236 | 15.1% | 0.784 | 7659.2 |
| repeat_core8k | x86_axelera_paper | 8192 | gemma4_e4b | tbq4/tbq4 | 5 | 180.612 | 10.4% | 0.819 | 7536.1 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | f16/f16 | 5 | 188.184 | 3.1% | 0.360 | 6424.9 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q4_0/q4_0 | 5 | 193.993 | 0.0% | 0.360 | 6088.8 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/q8_0 | 5 | 198.909 | -2.5% | 0.360 | 6207.4 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | q8_0/tbq4 | 5 | 200.153 | -3.1% | 0.360 | 6145.0 |
| repeat_core8k | x86_axelera_paper | 8192 | qwen35_4b | tbq4/tbq4 | 5 | 205.237 | -5.5% | 0.365 | 6088.8 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | f16/f16 | 1 | 130.071 | 11.5% | 0.829 | 9653.8 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 145.064 | 0.0% | 0.848 | 8300.4 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 139.970 | 3.6% | 0.845 | 8941.6 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 127.569 | 13.7% | 0.857 | 8625.6 |
| suite25_8k | m4_paper_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 126.752 | 14.4% | 0.849 | 8386.8 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | f16/f16 | 1 | 149.867 | 2.1% | 0.860 | 10276.6 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 153.008 | 0.0% | 0.896 | 9625.3 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 149.157 | 2.6% | 0.867 | 9863.3 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 156.609 | -2.3% | 0.864 | 9730.6 |
| suite25_8k | m4_paper_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 159.708 | -4.2% | 0.857 | 9636.8 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | f16/f16 | 1 | 552.355 | 8.2% | 0.859 | 10150.3 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 597.549 | 0.0% | 0.857 | 8044.8 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 550.537 | 8.5% | 0.849 | 8729.2 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 537.622 | 11.1% | 0.859 | 8388.4 |
| suite25_8k | x86_axelera_suite25 | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 541.270 | 10.4% | 0.876 | 8138.3 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | f16/f16 | 1 | 585.101 | 2.1% | 0.371 | 9436.6 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 597.607 | 0.0% | 0.373 | 8814.3 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 612.202 | -2.4% | 0.372 | 9035.5 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 607.193 | -1.6% | 0.368 | 8926.6 |
| suite25_8k | x86_axelera_suite25 | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 641.579 | -6.9% | 0.372 | 8820.7 |

## Claim Assessment

`tbq4/tbq4` does not uniformly beat Q4 in the available 8K agent results.
`q8_0/tbq4` remains the conservative quality candidate because its quality delta is non-inferior in the aggregated slices.
The x86 Qwen rows with zero valid JSON must be fixed and rerun before making cross-model claims.

Do not publish a strict-lossless claim from this evidence alone. The supported wording is `quality-preserving under the tested Gemma CPU edge-agent workload` or `near-lossless in this task suite`.

## Artifacts

- `aggregate_summary.csv`: repeated-run mean, stddev, CI95, Q4 speedup, quality, RSS, and CPU profile aggregates.
- `latency_breakdown.csv`: planner/tool/final/prompt/decode decomposition.
- `quality_noninferiority.csv`: paired task-level comparison against Q4.
