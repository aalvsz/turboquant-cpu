# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260505_pi_agentic_impact_gemma4k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | 1 | gemma4_e4b | f16/f16 | 8 | 0.812 | 1008.648 | 1.699 | 1.000 | 1.000 | 6818.8 | 369.0 | 78.2 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | 1 | gemma4_e4b | q4_0/q4_0 | 8 | 0.775 | 1036.571 | 1.562 | 1.000 | 1.000 | 7343.8 | 375.0 | 77.1 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | 1 | gemma4_e4b | q8_0/q8_0 | 8 | 0.812 | 977.822 | 1.756 | 1.000 | 1.000 | 7367.8 | 387.0 | 77.7 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | 1 | gemma4_e4b | q8_0/tbq4 | 8 | 0.829 | 951.917 | 1.780 | 1.000 | 1.000 | 7441.3 | 385.0 | 77.7 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | 1 | gemma4_e4b | tbq4/tbq4 | 8 | 0.829 | 976.312 | 1.740 | 1.000 | 1.000 | 7456.9 | 386.0 | 77.7 | 0x0 | 0.0 | 0.00 | 0.0 | 0.00 |

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
