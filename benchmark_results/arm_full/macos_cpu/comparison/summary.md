# Gemma 4 CPU Comparison: x86 vs macOS

macOS result root: `turboquant/results/macos_cpu`
macOS platform: `macOS-26.3.1-arm64-arm-64bit-Mach-O`
macOS machine: `arm64`

## 8K Decode Throughput

| setting_label | x86_tok_s | macos_tok_s | macos_vs_x86 | macos_delta_pct |
| --- | --- | --- | --- | --- |
| F16/F16 | 7.070834 | 33.232162 | 4.6999 | +369.99 |
| Q8/Q8 | 8.575463 | 30.048617 | 3.5040 | +250.40 |
| Q4/Q4 | 7.879723 | 29.471472 | 3.7402 | +274.02 |
| TBQ4/TBQ4 | 9.192574 | 23.714667 | 2.5798 | +157.98 |
| Q8/TBQ4 |  | 25.398234 |  |  |

## Perplexity

| setting_label | x86_ppl | macos_ppl | macos_minus_x86 | macos_delta_pct |
| --- | --- | --- | --- | --- |
| F16/F16 | 117.948600 | 117.661500 | -0.287100 | -0.24 |
| Q8/Q8 | 117.470300 | 117.761300 | +0.291000 | +0.25 |
| Q4/Q4 | 133.773600 | 134.733200 | +0.959600 | +0.72 |
| TBQ4/TBQ4 | 113.864300 | 113.843400 | -0.020900 | -0.02 |
| Q8/TBQ4 | 116.718800 | 116.887400 | +0.168600 | +0.14 |

## Hard-Prompt Task Score

| setting_label | x86_mean_task_score | macos_mean_task_score | macos_minus_x86 |
| --- | --- | --- | --- |
| F16/F16 | 0.837500 | 0.837500 | +0.000000 |
| Q8/Q8 | 0.837500 | 0.837500 | +0.000000 |
| Q4/Q4 | 0.887500 | 0.725000 | -0.162500 |
| TBQ4/TBQ4 | 0.768750 | 0.768750 | +0.000000 |
| Q8/TBQ4 | 0.837500 | 0.812500 | -0.025000 |
