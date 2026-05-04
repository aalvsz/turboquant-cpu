# Raspberry Pi Compact llama-bench Report

CPU-only, 4 threads, flash attention on, 1024-token prompt and 32-token decode, 1 repetition.

## Health

- Before temp: `temp=51.6'C`; throttle: `throttled=0x0`
- After temp: `temp=65.3'C`; throttle: `throttled=0x0`

## Summary

| model | config | prompt tok/s | prompt vs F16 | prompt vs Q4 | decode tok/s | decode vs F16 | decode vs Q4 |
|---|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 20.233 | +0.0% | +22.6% | 3.402 | +0.0% | +2.8% |
| gemma4_e4b | q4_0/q4_0 | 16.497 | -18.5% | +0.0% | 3.309 | -2.7% | +0.0% |
| gemma4_e4b | q8_0/q8_0 | 18.736 | -7.4% | +13.6% | 3.362 | -1.2% | +1.6% |
| gemma4_e4b | tbq4/tbq4 | 18.867 | -6.8% | +14.4% | 3.377 | -0.7% | +2.0% |
| gemma4_e4b | q8_0/tbq4 | 19.021 | -6.0% | +15.3% | 3.286 | -3.4% | -0.7% |

| qwen35_4b | f16/f16 | 20.559 | +0.0% | +5.9% | 2.201 | +0.0% | -1.5% |
| qwen35_4b | q4_0/q4_0 | 19.416 | -5.6% | +0.0% | 2.234 | +1.5% | +0.0% |
| qwen35_4b | q8_0/q8_0 | 20.311 | -1.2% | +4.6% | 2.221 | +0.9% | -0.6% |
| qwen35_4b | tbq4/tbq4 | 20.516 | -0.2% | +5.7% | 2.228 | +1.2% | -0.3% |
| qwen35_4b | q8_0/tbq4 | 20.527 | -0.2% | +5.7% | 2.223 | +1.0% | -0.5% |
