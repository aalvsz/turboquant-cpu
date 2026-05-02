# TurboQuant Edge-Agent Benchmark Report

Run folder: `/home/ubuntu/dev/repos/turboquant-cpu/agent/results/20260502_143814_x86_axelera_ctx`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| x86_axelera_ctx | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.807 | 260.660 | 2.175 | 1.000 | 1.000 | 7591.0 | 594.0 |
| x86_axelera_ctx | 4096 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 142.405 | 2.514 | 1.000 | 0.000 | 5587.2 | 595.0 |
| x86_axelera_ctx | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.813 | 223.909 | 2.519 | 1.000 | 1.000 | 7733.2 | 596.0 |
| x86_axelera_ctx | 4096 | 1 | gemma4_e4b | f16/f16 | 5 | 0.747 | 155.298 | 3.741 | 1.000 | 1.000 | 8041.8 | 591.0 |
| x86_axelera_ctx | 4096 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 160.814 | 3.016 | 1.000 | 0.000 | 5623.0 | 593.0 |
| x86_axelera_ctx | 2048 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 113.964 | 3.317 | 1.000 | 0.000 | 5555.4 | 591.0 |
| x86_axelera_ctx | 2048 | 1 | qwen35_4b | f16/f16 | 5 | 0.360 | 116.407 | 3.376 | 1.000 | 0.000 | 5648.7 | 595.0 |
| x86_axelera_ctx | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.780 | 222.766 | 2.478 | 1.000 | 1.000 | 7588.5 | 594.0 |
| x86_axelera_ctx | 2048 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.827 | 128.549 | 4.481 | 1.000 | 1.000 | 7416.7 | 590.0 |
| x86_axelera_ctx | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.827 | 228.456 | 2.495 | 1.000 | 1.000 | 8271.5 | 595.0 |
| x86_axelera_ctx | 2048 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 103.791 | 2.862 | 1.000 | 0.000 | 5527.5 | 596.0 |
| x86_axelera_ctx | 2048 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.813 | 118.205 | 4.915 | 1.000 | 1.000 | 7429.8 | 591.0 |
| x86_axelera_ctx | 2048 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 125.541 | 3.457 | 1.000 | 0.000 | 5508.1 | 591.0 |
| x86_axelera_ctx | 2048 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 148.890 | 4.339 | 1.000 | 0.000 | 5508.0 | 593.0 |
| x86_axelera_ctx | 2048 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.787 | 120.586 | 4.984 | 1.000 | 0.800 | 7503.5 | 592.0 |
| x86_axelera_ctx | 4096 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.787 | 150.487 | 3.681 | 1.000 | 1.000 | 7469.6 | 595.0 |
| x86_axelera_ctx | 4096 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.773 | 156.339 | 3.684 | 1.000 | 1.000 | 7667.2 | 591.0 |
| x86_axelera_ctx | 4096 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 154.464 | 2.667 | 1.000 | 0.000 | 5545.1 | 593.0 |
| x86_axelera_ctx | 4096 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 155.142 | 2.913 | 1.000 | 0.000 | 5547.4 | 594.0 |
| x86_axelera_ctx | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.360 | 207.090 | 1.492 | 1.000 | 0.000 | 5618.9 | 595.0 |
| x86_axelera_ctx | 2048 | 1 | gemma4_e4b | f16/f16 | 5 | 0.827 | 118.402 | 4.848 | 1.000 | 1.000 | 7860.6 | 586.0 |
| x86_axelera_ctx | 2048 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.760 | 118.529 | 4.775 | 1.000 | 1.000 | 7595.0 | 591.0 |
| x86_axelera_ctx | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.760 | 234.275 | 2.424 | 1.000 | 1.000 | 7871.8 | 595.0 |
| x86_axelera_ctx | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.360 | 215.558 | 1.661 | 1.000 | 0.000 | 5763.4 | 595.0 |
| x86_axelera_ctx | 4096 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.827 | 149.331 | 3.663 | 1.000 | 1.000 | 7575.9 | 591.0 |
| x86_axelera_ctx | 4096 | 1 | qwen35_4b | f16/f16 | 5 | 0.360 | 128.680 | 1.904 | 1.000 | 0.000 | 5769.6 | 592.0 |
| x86_axelera_ctx | 4096 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.853 | 174.950 | 3.510 | 1.000 | 1.000 | 7475.8 | 595.0 |
| x86_axelera_ctx | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.360 | 257.415 | 2.222 | 1.000 | 0.000 | 5620.2 | 597.0 |
| x86_axelera_ctx | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.360 | 198.447 | 1.199 | 1.000 | 0.000 | 5692.2 | 597.0 |
| x86_axelera_ctx | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.360 | 213.220 | 1.679 | 1.000 | 0.000 | 6037.2 | 594.0 |

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
