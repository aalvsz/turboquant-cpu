# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260503_x86_qwen_fix_telemetry`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | pkg J | avg pkg W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_axelera_qwen_fix_telemetry | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 1 | 0.900 | 60.050 | 4.813 | 0.000 | 1.000 | 4837.2 | 591.0 | 87.0 | 4343.0 | 70.05 |
| x86_axelera_qwen_fix_telemetry | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 1 | 0.900 | 58.571 | 4.985 | 1.000 | 1.000 | 4905.2 | 596.0 | 87.0 | 4096.6 | 67.76 |
| x86_axelera_qwen_fix_telemetry | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 1 | 0.667 | 54.259 | 4.626 | 1.000 | 1.000 | 4868.5 | 596.0 | 86.0 | 3653.9 | 65.39 |

## Interpretation

- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.
- Lower wall time is better. Mean quality is a deterministic rubric over correctness, JSON validity, tool use, safety, and expected-decision agreement.
- Timing fields decompose planner, deterministic tool, LLM-tool, final synthesis, prompt-eval, and decode time.

## Task Suite

| task | category | purpose |
|---|---|---|
| latency_triage | latency | Investigate why ORION-7 exceeded the edge-agent step budget and recommend whether TurboQuant should replace Q4 for the KV cache. |
