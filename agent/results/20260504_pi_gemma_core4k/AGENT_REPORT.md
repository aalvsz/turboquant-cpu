# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260504_pi_gemma_core4k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raspberry_pi5_8gb_gemma_core4k | 4096 | 1 | gemma4_e4b | f16/f16 | 5 | 0.727 | 1091.764 | 0.951 | 1.000 | 1.000 | 7386.9 | 386.0 | 77.7 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_gemma_core4k | 4096 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.787 | 1313.520 | 0.824 | 1.000 | 1.000 | 7309.9 | 381.0 | 76.5 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_gemma_core4k | 4096 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.787 | 1140.370 | 0.921 | 1.000 | 1.000 | 7377.1 | 389.0 | 77.7 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_gemma_core4k | 4096 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 1127.017 | 0.948 | 1.000 | 1.000 | 7410.2 | 387.0 | 77.1 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_gemma_core4k | 4096 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 1136.283 | 0.923 | 1.000 | 1.000 | 7429.5 | 388.0 | 77.1 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |

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
