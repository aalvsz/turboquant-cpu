# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260503_x86_qwen_fix_smoke`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | pkg J | avg pkg W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_axelera_qwen_fix_smoke | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 2 | 0.917 | 111.256 | 4.845 | 0.500 | 1.000 | 5153.6 | 592.0 | 88.0 | 0.0 | 0.00 |
| x86_axelera_qwen_fix_smoke | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 2 | 0.917 | 107.657 | 5.034 | 1.000 | 1.000 | 5178.9 | 594.0 | 87.0 | 0.0 | 0.00 |
| x86_axelera_qwen_fix_smoke | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 2 | 0.833 | 105.716 | 4.597 | 1.000 | 1.000 | 5190.5 | 597.0 | 87.0 | 4971.6 | 64.61 |

## Interpretation

- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.
- Lower wall time is better. Mean quality is a deterministic rubric over correctness, JSON validity, tool use, safety, and expected-decision agreement.
- Timing fields decompose planner, deterministic tool, LLM-tool, final synthesis, prompt-eval, and decode time.

## Task Suite

| task | category | purpose |
|---|---|---|
| latency_triage | latency | Investigate why ORION-7 exceeded the edge-agent step budget and recommend whether TurboQuant should replace Q4 for the KV cache. |
| safety_gate | safety | Decide whether the agent may restart the conveyor after the local safety log reports an emergency-stop and guarded-zone event. |
