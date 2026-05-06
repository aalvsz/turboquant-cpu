# TurboQuant Edge-Agent Benchmark Report

Run folder: `agent/results/20260506_x86_agentic_impact_8k`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % | max temp C | throttle | pkg J | avg pkg W | batt J | avg batt W |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_i5_12500_agentic_8k | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 8 | 0.773 | 424.230 | 4.679 | 1.000 | 1.000 | 6946.6 | 995.0 | 90.0 | 0x0 | 27700.3 | 65.09 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 8 | 0.800 | 345.110 | 4.877 | 1.000 | 1.000 | 7662.8 | 994.0 | 90.0 | 0x0 | 22626.2 | 65.05 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 8 | 0.812 | 327.213 | 5.217 | 1.000 | 1.000 | 7995.6 | 994.0 | 90.0 | 0x0 | 21418.0 | 64.97 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 8 | 0.808 | 342.629 | 5.140 | 1.000 | 1.000 | 7818.6 | 988.0 | 90.0 | 0x0 | 22339.7 | 64.74 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | gemma4_e4b | f16/f16 | 8 | 0.812 | 327.813 | 5.204 | 1.000 | 1.000 | 8610.6 | 990.0 | 90.0 | 0x0 | 21436.7 | 64.96 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | qwen35_4b | f16/f16 | 8 | 0.840 | 450.027 | 4.624 | 1.000 | 1.000 | 7480.6 | 992.0 | 90.0 | 0x0 | 29316.6 | 64.84 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 8 | 0.840 | 331.968 | 5.284 | 1.000 | 1.000 | 7647.1 | 994.0 | 88.0 | 0x0 | 21666.6 | 64.85 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 8 | 0.802 | 439.833 | 4.447 | 1.000 | 1.000 | 6978.8 | 992.0 | 91.0 | 0x0 | 28689.6 | 64.90 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 8 | 0.819 | 458.793 | 4.525 | 1.000 | 1.000 | 7029.6 | 994.0 | 91.0 | 0x0 | 29849.1 | 64.86 | 0.0 | 0.00 |
| x86_i5_12500_agentic_8k | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 8 | 0.800 | 451.671 | 4.539 | 1.000 | 1.000 | 7200.4 | 992.0 | 91.0 | 0x0 | 29419.1 | 64.90 | 0.0 | 0.00 |

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
