# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260504_pi_qwen_core8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raspberry_pi5_8gb_qwen_core8k | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.713 | 1822.601 | 0.707 | 0.800 | 1.000 | 6797.8 | 370.0 | 77.1 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_qwen_core8k | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.713 | 2079.364 | 0.584 | 0.600 | 1.000 | 6299.5 | 373.0 | 76.5 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_qwen_core8k | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.673 | 2078.110 | 0.606 | 0.800 | 1.000 | 6551.9 | 374.0 | 77.1 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_qwen_core8k | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.760 | 1745.904 | 0.773 | 0.800 | 1.000 | 6332.5 | 372.0 | 76.5 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_qwen_core8k | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.747 | 1650.372 | 0.731 | 0.800 | 1.000 | 6219.3 | 372.0 | 76.5 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |

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
