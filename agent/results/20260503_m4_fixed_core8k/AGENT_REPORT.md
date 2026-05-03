# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260503_m4_fixed_core8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_fixed_core8k_battery | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.727 | 144.411 | 8.690 | 1.000 | 1.000 | 6889.9 | 384.4 | 0.0 | 0.0 | 0.00 | 9487.8 | 64.53 |
| m4_fixed_core8k_battery | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.720 | 175.877 | 6.107 | 1.000 | 1.000 | 7885.3 | 459.1 | 0.0 | 0.0 | 0.00 | 15258.4 | 85.25 |
| m4_fixed_core8k_battery | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.787 | 163.046 | 6.458 | 1.000 | 1.000 | 7995.9 | 418.5 | 0.0 | 0.0 | 0.00 | 13925.2 | 85.54 |
| m4_fixed_core8k_battery | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 142.921 | 7.074 | 1.000 | 1.000 | 8108.3 | 312.7 | 0.0 | 0.0 | 0.00 | 12336.8 | 85.45 |
| m4_fixed_core8k_battery | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.813 | 145.235 | 7.285 | 1.000 | 1.000 | 8400.9 | 428.4 | 0.0 | 0.0 | 0.00 | 12829.0 | 87.62 |
| m4_fixed_core8k_battery | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.680 | 160.836 | 7.579 | 0.800 | 1.000 | 7783.0 | 456.6 | 0.0 | 0.0 | 0.00 | 13550.9 | 83.28 |
| m4_fixed_core8k_battery | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.733 | 141.279 | 7.305 | 1.000 | 1.000 | 7896.2 | 200.8 | 0.0 | 0.0 | 0.00 | 12477.2 | 86.32 |
| m4_fixed_core8k_battery | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.813 | 156.398 | 8.108 | 1.000 | 1.000 | 7070.2 | 397.8 | 0.0 | 0.0 | 0.00 | 13201.7 | 84.17 |
| m4_fixed_core8k_battery | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.807 | 184.007 | 6.402 | 0.800 | 1.000 | 7072.3 | 611.7 | 0.0 | 0.0 | 0.00 | 12878.7 | 69.66 |
| m4_fixed_core8k_battery | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.687 | 182.910 | 6.850 | 0.800 | 1.000 | 7323.2 | 632.8 | 0.0 | 0.0 | 0.00 | 13682.1 | 74.65 |

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
