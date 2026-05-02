# TurboQuant Edge-Agent Benchmark Report

Run folder: `/Users/ander.alvarez/dev/perso/turboquant-cpu/agent/results/20260502_094633_m4_paper`

## Summary

| host | ctx | repeat | model | config | tasks | mean quality | total wall s | tok/s | plan valid | JSON valid | max RSS MB | max CPU % |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_paper | 8192 | 2 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 87.709 | 9.383 | 0.600 | 1.000 | 7828.2 | 277.4 |
| m4_paper | 8192 | 5 | qwen35_4b | q8_0/tbq4 | 5 | 0.873 | 113.884 | 7.736 | 0.000 | 1.000 | 6944.5 | 447.7 |
| m4_paper | 8192 | 2 | gemma4_e4b | f16/f16 | 5 | 0.800 | 97.564 | 8.845 | 0.600 | 1.000 | 8351.7 | 261.9 |
| m4_paper | 8192 | 5 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 48.622 | 16.947 | 0.600 | 1.000 | 7516.9 | 177.7 |
| m4_paper | 8192 | 1 | qwen35_4b | q8_0/tbq4 | 5 | 0.873 | 58.603 | 14.846 | 0.000 | 1.000 | 6719.1 | 496.0 |
| m4_paper | 8192 | 2 | qwen35_4b | q8_0/tbq4 | 5 | 0.873 | 57.986 | 15.142 | 0.000 | 1.000 | 6946.0 | 302.6 |
| m4_paper | 8192 | 1 | qwen35_4b | f16/f16 | 5 | 0.813 | 55.046 | 14.987 | 0.000 | 1.000 | 6966.4 | 222.2 |
| m4_paper | 8192 | 1 | gemma4_e4b | f16/f16 | 5 | 0.747 | 46.629 | 18.658 | 0.600 | 1.000 | 8237.7 | 202.8 |
| m4_paper | 8192 | 5 | gemma4_e4b | q8_0/q8_0 | 5 | 0.747 | 52.059 | 16.769 | 0.600 | 1.000 | 7730.7 | 172.2 |
| m4_paper | 8192 | 2 | qwen35_4b | q8_0/q8_0 | 5 | 0.827 | 57.873 | 13.979 | 0.000 | 1.000 | 6976.1 | 209.3 |
| m4_paper | 8192 | 1 | qwen35_4b | tbq4/tbq4 | 5 | 0.780 | 52.592 | 14.356 | 0.000 | 1.000 | 6882.5 | 208.0 |
| m4_paper | 8192 | 1 | qwen35_4b | q8_0/q8_0 | 5 | 0.800 | 54.913 | 14.441 | 0.000 | 1.000 | 6995.4 | 247.8 |
| m4_paper | 8192 | 2 | gemma4_e4b | q4_0/q4_0 | 5 | 0.747 | 47.459 | 18.100 | 0.800 | 0.800 | 7667.8 | 135.1 |
| m4_paper | 8192 | 3 | qwen35_4b | q8_0/q8_0 | 5 | 0.827 | 54.488 | 14.425 | 0.000 | 1.000 | 6990.1 | 189.8 |
| m4_paper | 8192 | 1 | qwen35_4b | q4_0/q4_0 | 5 | 0.853 | 57.104 | 15.358 | 0.000 | 1.000 | 6874.1 | 212.6 |
| m4_paper | 8192 | 2 | qwen35_4b | q4_0/q4_0 | 5 | 0.807 | 52.622 | 14.842 | 0.000 | 1.000 | 6883.0 | 277.1 |
| m4_paper | 8192 | 2 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 46.342 | 18.817 | 0.600 | 1.000 | 8041.7 | 137.1 |
| m4_paper | 8192 | 4 | qwen35_4b | q8_0/tbq4 | 5 | 0.873 | 54.937 | 16.546 | 0.000 | 1.000 | 6939.7 | 176.9 |
| m4_paper | 8192 | 4 | gemma4_e4b | q8_0/q8_0 | 5 | 0.787 | 46.469 | 18.550 | 0.600 | 1.000 | 7983.2 | 140.0 |
| m4_paper | 8192 | 5 | qwen35_4b | f16/f16 | 5 | 0.827 | 51.613 | 15.500 | 0.000 | 1.000 | 7219.9 | 226.5 |
| m4_paper | 8192 | 4 | gemma4_e4b | q4_0/q4_0 | 5 | 0.827 | 44.687 | 17.768 | 0.800 | 1.000 | 7707.7 | 136.5 |
| m4_paper | 8192 | 3 | qwen35_4b | tbq4/tbq4 | 5 | 0.780 | 50.418 | 15.074 | 0.000 | 1.000 | 6878.5 | 212.8 |
| m4_paper | 8192 | 3 | gemma4_e4b | q8_0/q8_0 | 5 | 0.800 | 46.104 | 18.849 | 0.600 | 1.000 | 8043.5 | 165.4 |
| m4_paper | 8192 | 3 | gemma4_e4b | f16/f16 | 5 | 0.760 | 44.692 | 19.467 | 0.600 | 1.000 | 8499.5 | 164.9 |
| m4_paper | 8192 | 4 | gemma4_e4b | q8_0/tbq4 | 5 | 0.813 | 42.742 | 19.208 | 0.600 | 1.000 | 7800.2 | 177.9 |
| m4_paper | 8192 | 2 | qwen35_4b | f16/f16 | 5 | 0.827 | 51.842 | 15.431 | 0.000 | 1.000 | 7210.5 | 260.1 |
| m4_paper | 8192 | 5 | qwen35_4b | q8_0/q8_0 | 5 | 0.827 | 51.948 | 15.130 | 0.000 | 1.000 | 7002.3 | 224.0 |
| m4_paper | 8192 | 1 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 42.888 | 19.423 | 0.600 | 1.000 | 7802.7 | 133.8 |
| m4_paper | 8192 | 5 | qwen35_4b | q4_0/q4_0 | 5 | 0.827 | 52.430 | 15.278 | 0.000 | 1.000 | 6868.2 | 173.1 |
| m4_paper | 8192 | 3 | gemma4_e4b | q4_0/q4_0 | 5 | 0.760 | 50.394 | 17.442 | 0.800 | 0.800 | 7713.8 | 155.6 |
| m4_paper | 8192 | 4 | qwen35_4b | q4_0/q4_0 | 5 | 0.827 | 55.707 | 14.756 | 0.000 | 1.000 | 6787.6 | 244.3 |
| m4_paper | 8192 | 1 | gemma4_e4b | tbq4/tbq4 | 5 | 0.787 | 42.789 | 19.187 | 0.800 | 1.000 | 7720.6 | 142.9 |
| m4_paper | 8192 | 2 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 42.445 | 18.989 | 0.800 | 1.000 | 7773.6 | 134.0 |
| m4_paper | 8192 | 5 | gemma4_e4b | q4_0/q4_0 | 5 | 0.813 | 44.737 | 18.106 | 0.800 | 1.000 | 7706.6 | 173.9 |
| m4_paper | 8192 | 4 | gemma4_e4b | tbq4/tbq4 | 5 | 0.787 | 42.740 | 19.303 | 0.800 | 1.000 | 7762.6 | 120.1 |
| m4_paper | 8192 | 2 | qwen35_4b | tbq4/tbq4 | 5 | 0.840 | 52.796 | 15.740 | 0.000 | 1.000 | 6858.6 | 208.3 |
| m4_paper | 8192 | 3 | qwen35_4b | q4_0/q4_0 | 5 | 0.813 | 55.600 | 14.604 | 0.000 | 1.000 | 6878.0 | 149.1 |
| m4_paper | 8192 | 3 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 44.440 | 18.654 | 0.800 | 1.000 | 7693.4 | 146.0 |
| m4_paper | 8192 | 4 | qwen35_4b | f16/f16 | 5 | 0.800 | 53.270 | 15.431 | 0.000 | 1.000 | 7215.9 | 255.9 |
| m4_paper | 8192 | 4 | qwen35_4b | q8_0/q8_0 | 5 | 0.813 | 53.014 | 15.392 | 0.000 | 1.000 | 6996.4 | 235.6 |
| m4_paper | 8192 | 5 | gemma4_e4b | f16/f16 | 5 | 0.800 | 44.721 | 19.409 | 0.600 | 1.000 | 8313.1 | 135.4 |
| m4_paper | 8192 | 4 | qwen35_4b | tbq4/tbq4 | 5 | 0.793 | 51.513 | 15.181 | 0.000 | 1.000 | 6884.7 | 283.1 |
| m4_paper | 8192 | 5 | qwen35_4b | tbq4/tbq4 | 5 | 0.787 | 54.379 | 16.422 | 0.000 | 1.000 | 6884.8 | 192.0 |
| m4_paper | 8192 | 1 | gemma4_e4b | q8_0/q8_0 | 5 | 0.760 | 46.441 | 18.798 | 0.600 | 1.000 | 8045.5 | 152.6 |
| m4_paper | 8192 | 1 | gemma4_e4b | q4_0/q4_0 | 5 | 0.760 | 46.256 | 18.722 | 0.800 | 0.800 | 7711.3 | 208.2 |
| m4_paper | 8192 | 5 | gemma4_e4b | tbq4/tbq4 | 5 | 0.800 | 42.928 | 19.055 | 0.800 | 1.000 | 7780.4 | 182.1 |
| m4_paper | 8192 | 3 | gemma4_e4b | q8_0/tbq4 | 5 | 0.800 | 42.712 | 19.479 | 0.600 | 1.000 | 7828.2 | 195.2 |
| m4_paper | 8192 | 3 | qwen35_4b | q8_0/tbq4 | 5 | 0.840 | 53.653 | 15.861 | 0.000 | 1.000 | 6945.0 | 222.9 |
| m4_paper | 8192 | 4 | gemma4_e4b | f16/f16 | 5 | 0.800 | 44.592 | 19.443 | 0.600 | 1.000 | 8509.4 | 113.6 |
| m4_paper | 8192 | 3 | qwen35_4b | f16/f16 | 5 | 0.827 | 51.608 | 15.502 | 0.000 | 1.000 | 7213.5 | 142.6 |

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
