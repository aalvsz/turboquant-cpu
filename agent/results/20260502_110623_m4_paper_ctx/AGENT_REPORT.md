# TurboQuant Edge-Agent Benchmark Report

Run folder: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_110623_m4_paper_ctx`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_paper_ctx | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.813 | 62.613 | 9.263 | 1.000 | 1.000 | 7818.8 | 188.7 |
| m4_paper_ctx | 4096 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.753 | 41.089 | 13.021 | 1.000 | 1.000 | 6381.3 | 278.4 |
| m4_paper_ctx | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.813 | 55.719 | 9.979 | 1.000 | 1.000 | 7939.9 | 186.8 |
| m4_paper_ctx | 4096 | 1 | gemma4_e4b | f16/f16 | 5 | 0.760 | 39.599 | 14.521 | 1.000 | 1.000 | 8207.5 | 132.8 |
| m4_paper_ctx | 4096 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.747 | 42.958 | 11.825 | 1.000 | 1.000 | 6409.5 | 261.5 |
| m4_paper_ctx | 2048 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.840 | 32.017 | 15.148 | 1.000 | 1.000 | 6340.2 | 158.0 |
| m4_paper_ctx | 2048 | 1 | qwen35_4b | f16/f16 | 5 | 0.840 | 32.239 | 16.378 | 1.000 | 1.000 | 6440.2 | 150.8 |
| m4_paper_ctx | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.827 | 55.201 | 10.127 | 1.000 | 1.000 | 7804.6 | 197.2 |
| m4_paper_ctx | 2048 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.773 | 30.453 | 20.557 | 1.000 | 0.800 | 7664.2 | 157.8 |
| m4_paper_ctx | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.827 | 55.676 | 10.220 | 1.000 | 1.000 | 8516.1 | 215.6 |
| m4_paper_ctx | 2048 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.860 | 33.948 | 17.203 | 1.000 | 1.000 | 6335.0 | 251.7 |
| m4_paper_ctx | 2048 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.747 | 28.619 | 21.524 | 1.000 | 0.800 | 7667.2 | 180.9 |
| m4_paper_ctx | 2048 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.813 | 31.962 | 15.425 | 1.000 | 1.000 | 6297.0 | 194.5 |
| m4_paper_ctx | 2048 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.767 | 32.456 | 16.145 | 1.000 | 1.000 | 6303.4 | 168.9 |
| m4_paper_ctx | 2048 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 27.194 | 20.740 | 1.000 | 1.000 | 7719.3 | 132.5 |
| m4_paper_ctx | 4096 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 35.867 | 15.111 | 1.000 | 1.000 | 7727.2 | 133.6 |
| m4_paper_ctx | 4096 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.733 | 38.428 | 14.859 | 1.000 | 1.000 | 7913.8 | 140.1 |
| m4_paper_ctx | 4096 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.720 | 40.408 | 11.532 | 1.000 | 1.000 | 6337.2 | 257.8 |
| m4_paper_ctx | 4096 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.773 | 40.337 | 12.842 | 1.000 | 1.000 | 6335.4 | 209.3 |
| m4_paper_ctx | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.660 | 59.664 | 8.866 | 1.000 | 1.000 | 6410.2 | 232.8 |
| m4_paper_ctx | 2048 | 1 | gemma4_e4b | f16/f16 | 5 | 0.827 | 28.565 | 19.849 | 1.000 | 1.000 | 8102.4 | 159.0 |
| m4_paper_ctx | 2048 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.813 | 29.319 | 19.475 | 1.000 | 1.000 | 7834.5 | 152.9 |
| m4_paper_ctx | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.827 | 60.612 | 9.421 | 1.000 | 1.000 | 8118.6 | 321.6 |
| m4_paper_ctx | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.713 | 61.541 | 8.011 | 1.000 | 1.000 | 6554.7 | 327.0 |
| m4_paper_ctx | 4096 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 36.038 | 15.262 | 1.000 | 1.000 | 7814.8 | 178.6 |
| m4_paper_ctx | 4096 | 1 | qwen35_4b | f16/f16 | 5 | 0.707 | 39.336 | 12.330 | 1.000 | 1.000 | 6565.6 | 170.6 |
| m4_paper_ctx | 4096 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.773 | 41.054 | 13.860 | 1.000 | 1.000 | 7713.2 | 218.6 |
| m4_paper_ctx | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.760 | 65.490 | 7.360 | 1.000 | 1.000 | 6412.6 | 397.4 |
| m4_paper_ctx | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.827 | 59.138 | 8.573 | 1.000 | 1.000 | 6484.5 | 284.1 |
| m4_paper_ctx | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.773 | 58.670 | 9.000 | 1.000 | 1.000 | 6828.2 | 312.5 |

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
