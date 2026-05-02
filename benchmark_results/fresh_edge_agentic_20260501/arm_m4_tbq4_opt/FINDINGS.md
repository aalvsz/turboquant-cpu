# Fresh Findings: arm_m4_tbq4_opt

## 8K Decode Speed

| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |
|---|---:|---|---:|---:|---:|---:|
| gemma4_e4b | 6 | f16/f16 | 16.166 | +0.0% | +10.4% | +25.5% |
| gemma4_e4b | 6 | q8_0/q8_0 | 14.638 | -9.5% | +0.0% | +13.6% |
| gemma4_e4b | 6 | q4_0/q4_0 | 12.885 | -20.3% | -12.0% | +0.0% |
| gemma4_e4b | 6 | tbq4/tbq4 | 15.521 | -4.0% | +6.0% | +20.5% |
| gemma4_e4b | 6 | q8_0/tbq4 | 14.319 | -11.4% | -2.2% | +11.1% |
| qwen35_4b | 6 | f16/f16 | 9.523 | +0.0% | +1.9% | +7.7% |
| qwen35_4b | 6 | q8_0/q8_0 | 9.346 | -1.9% | +0.0% | +5.7% |
| qwen35_4b | 6 | q4_0/q4_0 | 8.840 | -7.2% | -5.4% | +0.0% |
| qwen35_4b | 6 | tbq4/tbq4 | 10.081 | +5.9% | +7.9% | +14.0% |
| qwen35_4b | 6 | q8_0/tbq4 | 9.986 | +4.9% | +6.9% | +13.0% |

## Perplexity

| model | config | ppl | delta vs f16 | returncode |
|---|---|---:|---:|---:|

## Deterministic Prompt Judge

| model | setting | n | mean score | degenerate rate |
|---|---|---:|---:|---:|

## Sustained 8K Decode

| model | threads | config | tok/s | max RSS MB | energy J |
|---|---:|---|---:|---:|---:|
