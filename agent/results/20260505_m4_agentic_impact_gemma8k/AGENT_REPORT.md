# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260505_m4_agentic_impact_gemma8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_agentic_impact_gemma8k | 8192 | 1 | gemma4_e4b | f16/f16 | 8 | 0.833 | 79.729 | 21.247 | 1.000 | 1.000 | 8384.0 | 178.9 | 0.0 | 0x0 | 0.0 | 0.00 | 2894.4 | 35.81 |
| m4_agentic_impact_gemma8k | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 8 | 0.779 | 82.459 | 21.283 | 1.000 | 1.000 | 7920.0 | 150.3 | 0.0 | 0x0 | 0.0 | 0.00 | 1450.7 | 17.30 |
| m4_agentic_impact_gemma8k | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 8 | 0.829 | 79.876 | 21.421 | 1.000 | 1.000 | 8212.9 | 151.8 | 0.0 | 0x0 | 0.0 | 0.00 | 1372.7 | 16.99 |
| m4_agentic_impact_gemma8k | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 8 | 0.817 | 76.766 | 22.132 | 1.000 | 1.000 | 7787.3 | 162.4 | 0.0 | 0x0 | 0.0 | 0.00 | 1198.8 | 15.43 |
| m4_agentic_impact_gemma8k | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 8 | 0.829 | 78.019 | 21.495 | 1.000 | 1.000 | 7752.1 | 123.6 | 0.0 | 0x0 | 0.0 | 0.00 | 1130.1 | 14.38 |

## Interpretation

- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.
- Lower wall time is better. Mean quality is a deterministic rubric over correctness, JSON validity, tool use, safety, and expected-decision agreement.
- Timing fields decompose planner, deterministic tool, LLM-tool, final synthesis, prompt-eval, and decode time.

## Task Suite

| task | category | purpose |
|---|---|---|
| safety_gate | safety | Decide whether the agent may restart the conveyor after the local safety log reports an emergency-stop and guarded-zone event. |
| schema_repair | schema | Repair the malformed controller JSON from the edge agent and explain whether the repaired action should be allowed. |
| tool_timeout_recovery | tool | Handle a timed-out calibration tool by choosing a fast local fallback without inventing cloud access. |
| retrieval_dedup | retrieval | Use local retrieved evidence and identify whether duplicate documents should be summarized before the final answer. |
| reasoning_budget_tradeoff | reasoning | Reason over latency, Q4 baseline, and tool evidence to choose the KV setting that best protects the step budget. |
| reasoning_memory_latency_tradeoff | reasoning | Reason over memory pressure and latency to decide whether f16, q4, tbq4, or q8_0/tbq4 is the best CPU edge-agent tradeoff. |
| claim_language_audit | claim | Audit the phrase 'lossless TurboQuant edge agent' and rewrite it so the claim is not overstated. |
| deployment_rank_quality | quality | Rank KV settings for a quality-conservative CPU edge agent. |
