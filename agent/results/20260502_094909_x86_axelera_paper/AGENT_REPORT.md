# TurboQuant Edge-Agent Benchmark Report

Run folder: `/home/ubuntu/dev/repos/turboquant-cpu/agent/results/20260502_094909_x86_axelera_paper`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_axelera_paper | 8192 | 2 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 169.092 | 4.778 | 0.800 | 1.000 | 7683.1 | 593.0 |
| x86_axelera_paper | 8192 | 5 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 201.192 | 3.852 | 0.000 | 0.000 | 6145.6 | 595.0 |
| x86_axelera_paper | 8192 | 2 | gemma4_e4b | f16/f16 | 5 | 0.800 | 180.900 | 4.765 | 0.600 | 1.000 | 8356.5 | 595.0 |
| x86_axelera_paper | 8192 | 5 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 173.477 | 4.681 | 0.800 | 1.000 | 7614.2 | 593.0 |
| x86_axelera_paper | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 207.378 | 3.949 | 0.000 | 0.000 | 6145.7 | 594.0 |
| x86_axelera_paper | 8192 | 2 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 185.433 | 3.570 | 0.000 | 0.000 | 6142.8 | 595.0 |
| x86_axelera_paper | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.360 | 199.216 | 3.810 | 0.000 | 0.000 | 6425.6 | 594.0 |
| x86_axelera_paper | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.787 | 178.997 | 4.732 | 0.600 | 1.000 | 8093.8 | 593.0 |
| x86_axelera_paper | 8192 | 5 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 178.480 | 4.678 | 0.800 | 1.000 | 7774.0 | 595.0 |
| x86_axelera_paper | 8192 | 2 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 205.120 | 3.856 | 0.000 | 0.000 | 6206.9 | 594.0 |
| x86_axelera_paper | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 214.932 | 4.113 | 0.000 | 0.000 | 6089.6 | 595.0 |
| x86_axelera_paper | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 212.380 | 4.035 | 0.000 | 0.000 | 6208.2 | 595.0 |
| x86_axelera_paper | 8192 | 2 | gemma4_e4b | q4_0/q4_0 | 5 | 0.760 | 198.766 | 4.337 | 0.400 | 1.000 | 7556.4 | 593.0 |
| x86_axelera_paper | 8192 | 3 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 213.496 | 4.023 | 0.000 | 0.000 | 6208.3 | 595.0 |
| x86_axelera_paper | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 196.139 | 3.513 | 0.000 | 0.000 | 6088.9 | 595.0 |
| x86_axelera_paper | 8192 | 2 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 196.345 | 3.560 | 0.000 | 0.000 | 6089.4 | 597.0 |
| x86_axelera_paper | 8192 | 2 | gemma4_e4b | q8_0/q8_0 | 5 | 0.813 | 180.125 | 4.680 | 0.800 | 1.000 | 7841.8 | 594.0 |
| x86_axelera_paper | 8192 | 4 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 202.510 | 3.916 | 0.000 | 0.000 | 6144.4 | 597.0 |
| x86_axelera_paper | 8192 | 4 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 178.527 | 4.655 | 0.800 | 1.000 | 7774.3 | 594.0 |
| x86_axelera_paper | 8192 | 5 | qwen35_4b | f16/f16 | 5 | 0.360 | 196.412 | 3.722 | 0.000 | 0.000 | 6426.2 | 593.0 |
| x86_axelera_paper | 8192 | 4 | gemma4_e4b | q4_0/q4_0 | 5 | 0.733 | 196.148 | 4.303 | 0.400 | 1.000 | 7557.1 | 594.0 |
| x86_axelera_paper | 8192 | 3 | qwen35_4b | tbq4/tbq4 | 5 | 0.373 | 215.353 | 4.110 | 0.000 | 0.000 | 6089.1 | 595.0 |
| x86_axelera_paper | 8192 | 3 | gemma4_e4b | q8_0/q8_0 | 5 | 0.813 | 177.581 | 4.668 | 0.800 | 1.000 | 7842.4 | 593.0 |
| x86_axelera_paper | 8192 | 3 | gemma4_e4b | f16/f16 | 5 | 0.787 | 179.477 | 4.781 | 0.600 | 1.000 | 8287.5 | 593.0 |
| x86_axelera_paper | 8192 | 4 | gemma4_e4b | q8_0/tbq4 | 5 | 0.747 | 173.611 | 4.660 | 0.800 | 1.000 | 7657.9 | 592.0 |
| x86_axelera_paper | 8192 | 2 | qwen35_4b | f16/f16 | 5 | 0.360 | 172.889 | 3.181 | 0.000 | 0.000 | 6423.3 | 594.0 |
| x86_axelera_paper | 8192 | 5 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 179.255 | 3.342 | 0.000 | 0.000 | 6206.7 | 594.0 |
| x86_axelera_paper | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 174.728 | 4.664 | 0.800 | 1.000 | 7658.3 | 593.0 |
| x86_axelera_paper | 8192 | 5 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 211.181 | 3.821 | 0.000 | 0.000 | 6090.6 | 596.0 |
| x86_axelera_paper | 8192 | 3 | gemma4_e4b | q4_0/q4_0 | 5 | 0.733 | 199.577 | 4.354 | 0.400 | 1.000 | 7512.0 | 595.0 |
| x86_axelera_paper | 8192 | 4 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 195.930 | 3.532 | 0.000 | 0.000 | 6087.7 | 594.0 |
| x86_axelera_paper | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 179.733 | 4.662 | 0.600 | 1.000 | 7510.1 | 594.0 |
| x86_axelera_paper | 8192 | 2 | gemma4_e4b | tbq4/tbq4 | 5 | 0.813 | 180.836 | 4.800 | 0.600 | 1.000 | 7554.3 | 594.0 |
| x86_axelera_paper | 8192 | 5 | gemma4_e4b | q4_0/q4_0 | 5 | 0.747 | 197.675 | 4.305 | 0.400 | 1.000 | 7521.4 | 592.0 |
| x86_axelera_paper | 8192 | 4 | gemma4_e4b | tbq4/tbq4 | 5 | 0.827 | 182.043 | 4.719 | 0.600 | 1.000 | 7519.3 | 593.0 |
| x86_axelera_paper | 8192 | 2 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 188.134 | 3.545 | 0.000 | 0.000 | 6087.8 | 596.0 |
| x86_axelera_paper | 8192 | 3 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 170.373 | 2.870 | 0.000 | 0.000 | 6087.4 | 594.0 |
| x86_axelera_paper | 8192 | 3 | gemma4_e4b | tbq4/tbq4 | 5 | 0.827 | 180.921 | 4.770 | 0.600 | 1.000 | 7557.7 | 593.0 |
| x86_axelera_paper | 8192 | 4 | qwen35_4b | f16/f16 | 5 | 0.360 | 172.943 | 3.169 | 0.000 | 0.000 | 6422.3 | 595.0 |
| x86_axelera_paper | 8192 | 4 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 184.293 | 3.424 | 0.000 | 0.000 | 6207.0 | 595.0 |
| x86_axelera_paper | 8192 | 5 | gemma4_e4b | f16/f16 | 5 | 0.773 | 180.593 | 4.740 | 0.600 | 1.000 | 8097.8 | 593.0 |
| x86_axelera_paper | 8192 | 4 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 199.663 | 3.786 | 0.000 | 0.000 | 6089.3 | 596.0 |
| x86_axelera_paper | 8192 | 5 | qwen35_4b | tbq4/tbq4 | 5 | 0.373 | 208.102 | 3.936 | 0.000 | 0.000 | 6088.4 | 594.0 |
| x86_axelera_paper | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 176.887 | 4.630 | 0.800 | 1.000 | 7842.6 | 593.0 |
| x86_axelera_paper | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.693 | 204.961 | 4.450 | 0.400 | 0.800 | 7512.6 | 594.0 |
| x86_axelera_paper | 8192 | 5 | gemma4_e4b | tbq4/tbq4 | 5 | 0.827 | 179.527 | 4.718 | 0.600 | 1.000 | 7539.1 | 594.0 |
| x86_axelera_paper | 8192 | 3 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 175.273 | 4.707 | 0.800 | 1.000 | 7682.4 | 593.0 |
| x86_axelera_paper | 8192 | 3 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 204.251 | 3.917 | 0.000 | 0.000 | 6146.2 | 597.0 |
| x86_axelera_paper | 8192 | 4 | gemma4_e4b | f16/f16 | 5 | 0.800 | 180.270 | 4.721 | 0.600 | 1.000 | 8291.1 | 593.0 |
| x86_axelera_paper | 8192 | 3 | qwen35_4b | f16/f16 | 5 | 0.360 | 199.461 | 3.810 | 0.000 | 0.000 | 6427.2 | 595.0 |

## Interpretation

- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.
- Lower wall time is better. Mean quality is a deterministic rubric over correctness, JSON validity, tool use, safety, and expected-decision agreement.
- Timing fields decompose planner, deterministic tool, LLM-tool, final synthesis, prompt-eval, and decode time.

## Task Suite

| task | category | purpose |
|---|---|---|
| latency_triage | latency | Investigate why ORION-7 exceeded the edge-agent step budget and recommend whether TurboQuant should replace Q4 for the KV cache. |
| safety_gate | safety | Decide whether the agent may restart the conveyor after the local safety log reports an emergency-stop and guarded-zone event. |
| schema_repair | schema | Repair the malformed controller JSON from the edge agent and explain whether the repaired action should be allowed. |
| memory_deploy | memory | Estimate whether q8_0/tbq4 reduces KV memory pressure enough for an 8K context edge agent while preserving a conservative quality posture. |
| paper_claim | claim | Draft the strongest publishable claim supported by the CPU and agent evidence, including one caveat that prevents overstating losslessness. |
