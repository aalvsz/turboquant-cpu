# KV-Cache Capacity Curve Report

Run folder: `agent/results/20260505_pi_qwen_context_curve_c1`

| model | config | ctx/agent | concurrency | total ctx | ok | errors | JSON | wall s | mean req s | RSS MB | temp C | throttle | killed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen35_4b | f16/f16 | 8192 | 1 | 8192 | 1 | 0 | 1.000 | 173.911 | 173.910 | 4917.9 | 77.1 | 0x0 | 0 |
| qwen35_4b | q4_0/q4_0 | 8192 | 1 | 8192 | 1 | 0 | 1.000 | 213.305 | 213.304 | 4729.9 | 76.0 | 0x0 | 0 |
| qwen35_4b | tbq4/tbq4 | 8192 | 1 | 8192 | 1 | 0 | 1.000 | 188.301 | 188.300 | 4729.9 | 76.0 | 0x0 | 0 |
| qwen35_4b | q8_0/tbq4 | 8192 | 1 | 8192 | 1 | 0 | 1.000 | 190.717 | 190.717 | 4762.9 | 76.0 | 0x0 | 0 |
| qwen35_4b | f16/f16 | 12288 | 1 | 12288 | 1 | 0 | 1.000 | 264.951 | 264.950 | 5051.4 | 76.0 | 0x0 | 0 |
| qwen35_4b | q4_0/q4_0 | 12288 | 1 | 12288 | 1 | 0 | 1.000 | 352.077 | 352.076 | 4771.1 | 76.0 | 0x0 | 0 |
| qwen35_4b | tbq4/tbq4 | 12288 | 1 | 12288 | 1 | 0 | 1.000 | 291.804 | 291.803 | 4771.5 | 76.5 | 0x0 | 0 |
| qwen35_4b | q8_0/tbq4 | 12288 | 1 | 12288 | 1 | 0 | 1.000 | 311.187 | 311.187 | 4820.4 | 76.5 | 0x0 | 0 |
| qwen35_4b | f16/f16 | 16384 | 1 | 16384 | 1 | 0 | 1.000 | 364.657 | 364.656 | 5182.9 | 77.1 | 0x0 | 0 |
| qwen35_4b | q4_0/q4_0 | 16384 | 1 | 16384 | 1 | 0 | 1.000 | 522.098 | 522.097 | 4809.9 | 76.5 | 0x0 | 0 |
| qwen35_4b | tbq4/tbq4 | 16384 | 1 | 16384 | 1 | 0 | 1.000 | 424.748 | 424.748 | 4811.4 | 77.1 | 0x0 | 0 |
| qwen35_4b | q8_0/tbq4 | 16384 | 1 | 16384 | 1 | 0 | 1.000 | 446.427 | 446.427 | 4875.4 | 77.7 | 0x0 | 0 |

Lower wall time is better within a fixed context/concurrency cell. Rows killed by the RSS guard are capacity failures, not latency wins.
The server context is `ctx/agent * concurrency` so each parallel slot has the target per-agent context budget.
