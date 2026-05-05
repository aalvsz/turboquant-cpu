# KV-Cache Capacity Curve Report

Run folder: `agent/results/20260505_pi_qwen_capacity_curve`

| model | config | ctx/agent | concurrency | total ctx | ok | errors | JSON | wall s | mean req s | RSS MB | temp C | throttle | killed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen35_4b | f16/f16 | 4096 | 1 | 4096 | 1 | 0 | 1.000 | 91.867 | 91.866 | 4788.7 | 77.1 | 0x0 | 0 |
| qwen35_4b | q4_0/q4_0 | 4096 | 1 | 4096 | 1 | 0 | 1.000 | 99.982 | 99.981 | 4692.9 | 74.9 | 0x0 | 0 |
| qwen35_4b | tbq4/tbq4 | 4096 | 1 | 4096 | 1 | 0 | 1.000 | 93.354 | 93.353 | 4693.4 | 76.0 | 0x0 | 0 |
| qwen35_4b | q8_0/tbq4 | 4096 | 1 | 4096 | 1 | 0 | 1.000 | 92.550 | 92.550 | 4710.0 | 77.1 | 0x0 | 0 |
| qwen35_4b | f16/f16 | 4096 | 2 | 8192 | 2 | 0 | 0.000 | 270.854 | 270.559 | 5367.4 | 77.1 | 0x0 | 0 |
| qwen35_4b | q4_0/q4_0 | 4096 | 2 | 8192 | 2 | 0 | 0.500 | 258.577 | 241.771 | 4985.0 | 76.0 | 0x0 | 0 |
| qwen35_4b | tbq4/tbq4 | 4096 | 2 | 8192 | 2 | 0 | 0.000 | 275.485 | 275.207 | 4998.8 | 76.5 | 0x0 | 0 |

Lower wall time is better within a fixed context/concurrency cell. Rows killed by the RSS guard are capacity failures, not latency wins.
The server context is `ctx/agent * concurrency` so each parallel slot has the target per-agent context budget.
