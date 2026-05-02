# TurboQuant Edge-Agent Benchmark Report

Run folder: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_083151_m4_max`

## Summary

| model | config | tasks | mean score | total wall s | completion tok/s | plan valid | final JSON valid | max RSS MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 5 | 0.667 | 81.464 | 23.139 | 0.600 | 1.000 | 8350.6 |
| gemma4_e4b | q8_0/q8_0 | 5 | 0.733 | 85.792 | 22.496 | 0.600 | 1.000 | 7941.3 |
| gemma4_e4b | q4_0/q4_0 | 5 | 0.733 | 81.410 | 21.705 | 0.800 | 1.000 | 7766.0 |
| gemma4_e4b | tbq4/tbq4 | 5 | 0.733 | 70.850 | 23.176 | 0.600 | 1.000 | 7752.6 |
| gemma4_e4b | q8_0/tbq4 | 5 | 0.533 | 72.193 | 23.673 | 0.800 | 1.000 | 7837.7 |
| qwen35_4b | f16/f16 | 5 | 0.867 | 120.191 | 18.487 | 1.000 | 1.000 | 6754.0 |
| qwen35_4b | q8_0/q8_0 | 5 | 0.800 | 107.469 | 17.633 | 0.600 | 1.000 | 6383.2 |
| qwen35_4b | q4_0/q4_0 | 5 | 0.600 | 114.374 | 16.612 | 1.000 | 1.000 | 6339.4 |
| qwen35_4b | tbq4/tbq4 | 5 | 0.800 | 97.610 | 19.957 | 0.400 | 1.000 | 6278.6 |
| qwen35_4b | q8_0/tbq4 | 5 | 0.867 | 112.340 | 19.414 | 0.600 | 1.000 | 6569.2 |

## Interpretation

- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.
- Lower wall time is better. Mean score is a lightweight task-success proxy, not a substitute for human or benchmark-grade judging.
- A config is a good edge-agent candidate only if it improves latency without reducing task score or JSON/tool discipline.

## Task Suite

| task | purpose |
|---|---|
| latency_triage | Investigate why ORION-7 exceeded the edge-agent step budget and recommend whether TurboQuant should replace Q4 for the KV cache. |
| safety_gate | Decide whether the agent may restart the conveyor after the local safety log reports an emergency-stop and guarded-zone event. |
| schema_repair | Repair the malformed controller JSON from the edge agent and explain whether the repaired action should be allowed. |
| memory_deploy | Estimate whether q8_0/tbq4 reduces KV memory pressure enough for an 8K context edge agent while preserving a conservative quality posture. |
| paper_claim | Draft the strongest publishable claim supported by the CPU and agent evidence, including one caveat that prevents overstating losslessness. |
