# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260505_m4_agentic_impact_qwen8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_agentic_impact_qwen8k | 8192 | 1 | qwen35_4b | f16/f16 | 8 | 0.871 | 101.578 | 20.615 | 1.000 | 1.000 | 7944.9 | 229.0 | 0.0 | 0x0 | 0.0 | 0.00 | 3401.7 | 33.37 |
| m4_agentic_impact_qwen8k | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 8 | 0.848 | 98.984 | 20.367 | 0.875 | 1.000 | 7826.3 | 246.9 | 0.0 | 0x0 | 0.0 | 0.00 | 1236.8 | 12.29 |
| m4_agentic_impact_qwen8k | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 8 | 0.792 | 99.676 | 20.195 | 1.000 | 1.000 | 7919.6 | 284.8 | 0.0 | 0x0 | 0.0 | 0.00 | 1210.8 | 12.02 |
| m4_agentic_impact_qwen8k | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 8 | 0.752 | 98.845 | 20.598 | 1.000 | 1.000 | 7890.3 | 233.8 | 0.0 | 0x0 | 0.0 | 0.00 | 1296.1 | 13.00 |
| m4_agentic_impact_qwen8k | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 8 | 0.831 | 98.350 | 20.539 | 0.875 | 1.000 | 7639.5 | 181.2 | 0.0 | 0x0 | 0.0 | 0.00 | 1206.8 | 12.12 |

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
