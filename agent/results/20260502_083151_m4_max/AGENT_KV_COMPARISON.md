# Agent KV Comparison

Run folder: `agent/results/20260502_083151_m4_max`

## Wall Time vs Q4

Lower is better.

| model | config | total wall s | vs Q4 | mean score | completion tok/s | max RSS MB |
|---|---|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 81.464 | +0.1% | 0.667 | 23.139 | 8350.6 |
| gemma4_e4b | q8_0/q8_0 | 85.792 | +5.4% | 0.733 | 22.496 | 7941.3 |
| gemma4_e4b | q4_0/q4_0 | 81.410 | +0.0% | 0.733 | 21.705 | 7766.0 |
| gemma4_e4b | tbq4/tbq4 | 70.850 | -13.0% | 0.733 | 23.176 | 7752.6 |
| gemma4_e4b | q8_0/tbq4 | 72.193 | -11.3% | 0.533 | 23.673 | 7837.7 |
| qwen35_4b | f16/f16 | 120.191 | +5.1% | 0.867 | 18.487 | 6754.0 |
| qwen35_4b | q8_0/q8_0 | 107.469 | -6.0% | 0.800 | 17.633 | 6383.2 |
| qwen35_4b | q4_0/q4_0 | 114.374 | +0.0% | 0.600 | 16.612 | 6339.4 |
| qwen35_4b | tbq4/tbq4 | 97.610 | -14.7% | 0.800 | 19.957 | 6278.6 |
| qwen35_4b | q8_0/tbq4 | 112.340 | -1.8% | 0.867 | 19.414 | 6569.2 |

## Decision Scaffold

- Prefer `q8_0/tbq4` if it beats Q4 wall time while preserving mean score and JSON/tool discipline.
- Prefer `tbq4/tbq4` if maximum speed is needed and task score does not drop.
- Do not treat these agent scores as human-quality proof; they are a fast end-to-end regression signal.
