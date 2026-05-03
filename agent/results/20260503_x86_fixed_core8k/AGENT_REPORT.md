# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260503_x86_fixed_core8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_axelera_fixed_core8k | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.787 | 490.703 | 2.570 | 1.000 | 1.000 | 6334.2 | 597.0 | 87.0 | 33081.5 | 67.25 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.787 | 679.445 | 1.600 | 1.000 | 1.000 | 7702.8 | 595.0 | 87.0 | 44364.1 | 65.03 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.787 | 548.812 | 1.953 | 1.000 | 1.000 | 8055.9 | 597.0 | 88.0 | 0.0 | 0.00 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.733 | 518.591 | 2.061 | 1.000 | 1.000 | 7883.9 | 597.0 | 88.0 | 33830.6 | 64.99 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.813 | 521.615 | 2.036 | 1.000 | 1.000 | 8715.4 | 596.0 | 86.0 | 34041.3 | 65.02 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.700 | 496.801 | 2.540 | 0.800 | 1.000 | 6863.2 | 596.0 | 87.0 | 32335.2 | 64.78 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.787 | 524.071 | 2.040 | 1.000 | 1.000 | 7693.0 | 598.0 | 88.0 | 34276.4 | 65.09 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.720 | 558.373 | 2.237 | 0.800 | 1.000 | 6304.6 | 597.0 | 87.0 | 36345.3 | 64.93 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.773 | 645.774 | 1.909 | 0.600 | 1.000 | 6313.0 | 597.0 | 86.0 | 42034.0 | 64.89 | 0.0 | 0.00 |
| x86_axelera_fixed_core8k | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.693 | 583.972 | 2.185 | 0.800 | 1.000 | 6554.3 | 598.0 | 88.0 | 0.0 | 0.00 | 0.0 | 0.00 |

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
