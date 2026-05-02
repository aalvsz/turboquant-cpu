# Cross-Host Fresh TurboQuant Findings

# Fresh Findings: arm_m4

## 8K Decode Speed

| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |
|---|---:|---|---:|---:|---:|---:|
| gemma4_e4b | 10 | f16/f16 | 34.321 | +0.0% | +1.3% | +2.0% |
| gemma4_e4b | 10 | q8_0/q8_0 | 33.864 | -1.3% | +0.0% | +0.6% |
| gemma4_e4b | 10 | q4_0/q4_0 | 33.663 | -1.9% | -0.6% | +0.0% |
| gemma4_e4b | 10 | tbq4/tbq4 | 39.392 | +14.8% | +16.3% | +17.0% |
| gemma4_e4b | 10 | q8_0/tbq4 | 37.753 | +10.0% | +11.5% | +12.2% |
| gemma4_e4b | 6 | f16/f16 | 35.703 | +0.0% | +11.1% | +13.0% |
| gemma4_e4b | 6 | q8_0/q8_0 | 32.122 | -10.0% | +0.0% | +1.7% |
| gemma4_e4b | 6 | q4_0/q4_0 | 31.582 | -11.5% | -1.7% | +0.0% |
| gemma4_e4b | 6 | tbq4/tbq4 | 37.635 | +5.4% | +17.2% | +19.2% |
| gemma4_e4b | 6 | q8_0/tbq4 | 34.552 | -3.2% | +7.6% | +9.4% |
| qwen35_4b | 10 | f16/f16 | 27.349 | +0.0% | +9.2% | +6.5% |
| qwen35_4b | 10 | q8_0/q8_0 | 25.045 | -8.4% | +0.0% | -2.5% |
| qwen35_4b | 10 | q4_0/q4_0 | 25.677 | -6.1% | +2.5% | +0.0% |
| qwen35_4b | 10 | tbq4/tbq4 | 29.103 | +6.4% | +16.2% | +13.3% |
| qwen35_4b | 10 | q8_0/tbq4 | 26.201 | -4.2% | +4.6% | +2.0% |
| qwen35_4b | 6 | f16/f16 | 24.297 | +0.0% | +9.9% | +5.8% |
| qwen35_4b | 6 | q8_0/q8_0 | 22.105 | -9.0% | +0.0% | -3.7% |
| qwen35_4b | 6 | q4_0/q4_0 | 22.965 | -5.5% | +3.9% | +0.0% |
| qwen35_4b | 6 | tbq4/tbq4 | 27.350 | +12.6% | +23.7% | +19.1% |
| qwen35_4b | 6 | q8_0/tbq4 | 24.584 | +1.2% | +11.2% | +7.0% |

## Perplexity

| model | config | ppl | delta vs f16 | returncode |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 117.662 | +0.0% | 0 |
| gemma4_e4b | q4_0/q4_0 | 134.733 | +14.5% | 0 |
| gemma4_e4b | q8_0/q8_0 | 117.761 | +0.1% | 0 |
| gemma4_e4b | q8_0/tbq4 | 113.747 | -3.3% | 0 |
| gemma4_e4b | tbq4/tbq4 | 114.261 | -2.9% | 0 |
| qwen35_4b | f16/f16 | 10.336 | +0.0% | 0 |
| qwen35_4b | q4_0/q4_0 | 10.399 | +0.6% | 0 |
| qwen35_4b | q8_0/q8_0 | 10.346 | +0.1% | 0 |
| qwen35_4b | q8_0/tbq4 | 10.411 | +0.7% | 0 |
| qwen35_4b | tbq4/tbq4 | 10.399 | +0.6% | 0 |

## Deterministic Prompt Judge

| model | setting | n | mean score | degenerate rate |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q4_0/q4_0 | 10 | 3.500 | 0.000 |
| gemma4_e4b | q8_0/q8_0 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q8_0/tbq4 | 10 | 3.500 | 0.000 |
| gemma4_e4b | tbq4/tbq4 | 10 | 3.350 | 0.000 |
| qwen35_4b | f16/f16 | 10 | 4.400 | 0.000 |
| qwen35_4b | q4_0/q4_0 | 10 | 4.600 | 0.000 |
| qwen35_4b | q8_0/q8_0 | 10 | 4.400 | 0.000 |
| qwen35_4b | q8_0/tbq4 | 10 | 4.600 | 0.000 |
| qwen35_4b | tbq4/tbq4 | 10 | 4.400 | 0.000 |

## Sustained 8K Decode

| model | threads | config | tok/s | max RSS MB | energy J |
|---|---:|---|---:|---:|---:|
| gemma4_e4b | 6 | f16/f16 | 35.401 | 6134.672 | n/a |
| gemma4_e4b | 6 | tbq4/tbq4 | 37.214 | 5893.656 | n/a |
| gemma4_e4b | 6 | q8_0/tbq4 | 34.430 | 5867.781 | n/a |
| gemma4_e4b | 10 | f16/f16 | 35.087 | 6137.438 | n/a |
| gemma4_e4b | 10 | tbq4/tbq4 | 39.020 | 5894.703 | n/a |
| gemma4_e4b | 10 | q8_0/tbq4 | 37.329 | 5866.641 | n/a |
| qwen35_4b | 6 | f16/f16 | 24.195 | 4418.641 | n/a |
| qwen35_4b | 6 | tbq4/tbq4 | 27.495 | 4041.812 | n/a |
| qwen35_4b | 6 | q8_0/tbq4 | 24.342 | 4109.188 | n/a |
| qwen35_4b | 10 | f16/f16 | 26.827 | 4417.703 | n/a |
| qwen35_4b | 10 | tbq4/tbq4 | 28.800 | 4045.844 | n/a |
| qwen35_4b | 10 | q8_0/tbq4 | 26.232 | 4111.406 | n/a |


# Fresh Findings: x86_axelera

## 8K Decode Speed

| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |
|---|---:|---|---:|---:|---:|---:|
| gemma4_e4b | 12 | f16/f16 | 7.118 | +0.0% | -15.6% | -7.6% |
| gemma4_e4b | 12 | q8_0/q8_0 | 8.435 | +18.5% | +0.0% | +9.5% |
| gemma4_e4b | 12 | q4_0/q4_0 | 7.706 | +8.3% | -8.6% | +0.0% |
| gemma4_e4b | 12 | tbq4/tbq4 | 8.986 | +26.3% | +6.5% | +16.6% |
| gemma4_e4b | 12 | q8_0/tbq4 | 8.868 | +24.6% | +5.1% | +15.1% |
| gemma4_e4b | 6 | f16/f16 | 7.266 | +0.0% | -15.1% | -8.3% |
| gemma4_e4b | 6 | q8_0/q8_0 | 8.553 | +17.7% | +0.0% | +7.9% |
| gemma4_e4b | 6 | q4_0/q4_0 | 7.924 | +9.0% | -7.4% | +0.0% |
| gemma4_e4b | 6 | tbq4/tbq4 | 9.193 | +26.5% | +7.5% | +16.0% |
| gemma4_e4b | 6 | q8_0/tbq4 | 8.843 | +21.7% | +3.4% | +11.6% |
| qwen35_4b | 12 | f16/f16 | 5.131 | +0.0% | -14.7% | -13.4% |
| qwen35_4b | 12 | q8_0/q8_0 | 6.015 | +17.2% | +0.0% | +1.5% |
| qwen35_4b | 12 | q4_0/q4_0 | 5.924 | +15.5% | -1.5% | +0.0% |
| qwen35_4b | 12 | tbq4/tbq4 | 6.495 | +26.6% | +8.0% | +9.6% |
| qwen35_4b | 12 | q8_0/tbq4 | 6.287 | +22.5% | +4.5% | +6.1% |
| qwen35_4b | 6 | f16/f16 | 5.334 | +0.0% | -16.6% | -15.1% |
| qwen35_4b | 6 | q8_0/q8_0 | 6.392 | +19.8% | +0.0% | +1.7% |
| qwen35_4b | 6 | q4_0/q4_0 | 6.284 | +17.8% | -1.7% | +0.0% |
| qwen35_4b | 6 | tbq4/tbq4 | 6.923 | +29.8% | +8.3% | +10.2% |
| qwen35_4b | 6 | q8_0/tbq4 | 6.615 | +24.0% | +3.5% | +5.3% |

## Perplexity

| model | config | ppl | delta vs f16 | returncode |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 117.949 | +0.0% | 0 |
| gemma4_e4b | q4_0/q4_0 | 133.774 | +13.4% | 0 |
| gemma4_e4b | q8_0/q8_0 | 117.470 | -0.4% | 0 |
| gemma4_e4b | q8_0/tbq4 | 116.719 | -1.0% | 0 |
| gemma4_e4b | tbq4/tbq4 | 113.864 | -3.5% | 0 |
| qwen35_4b | f16/f16 | 10.319 | +0.0% | 0 |
| qwen35_4b | q4_0/q4_0 | 10.401 | +0.8% | 0 |
| qwen35_4b | q8_0/q8_0 | 10.331 | +0.1% | 0 |
| qwen35_4b | q8_0/tbq4 | 10.390 | +0.7% | 0 |
| qwen35_4b | tbq4/tbq4 | 10.413 | +0.9% | 0 |

## Deterministic Prompt Judge

| model | setting | n | mean score | degenerate rate |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q4_0/q4_0 | 10 | 3.500 | 0.000 |
| gemma4_e4b | q8_0/q8_0 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q8_0/tbq4 | 10 | 3.500 | 0.000 |
| gemma4_e4b | tbq4/tbq4 | 10 | 3.500 | 0.000 |
| qwen35_4b | f16/f16 | 10 | 4.400 | 0.000 |
| qwen35_4b | q4_0/q4_0 | 10 | 4.400 | 0.000 |
| qwen35_4b | q8_0/q8_0 | 10 | 4.400 | 0.000 |
| qwen35_4b | q8_0/tbq4 | 10 | 4.400 | 0.000 |
| qwen35_4b | tbq4/tbq4 | 10 | 4.400 | 0.000 |

## Sustained 8K Decode

| model | threads | config | tok/s | max RSS MB | energy J |
|---|---:|---|---:|---:|---:|
| gemma4_e4b | 6 | f16/f16 | 7.230 | 5534.230 | n/a |
| gemma4_e4b | 6 | tbq4/tbq4 | 9.166 | 5363.812 | n/a |
| gemma4_e4b | 6 | q8_0/tbq4 | 8.827 | 5364.883 | n/a |
| gemma4_e4b | 12 | f16/f16 | 7.042 | 5534.250 | n/a |
| gemma4_e4b | 12 | tbq4/tbq4 | 8.953 | 5370.762 | n/a |
| gemma4_e4b | 12 | q8_0/tbq4 | 8.800 | 5338.863 | n/a |
| qwen35_4b | 6 | f16/f16 | 5.270 | 3300.727 | n/a |
| qwen35_4b | 6 | tbq4/tbq4 | 6.921 | 2926.922 | n/a |
| qwen35_4b | 6 | q8_0/tbq4 | 6.620 | 2991.918 | n/a |
| qwen35_4b | 12 | f16/f16 | 5.071 | 3300.746 | n/a |
| qwen35_4b | 12 | tbq4/tbq4 | 6.498 | 2926.934 | n/a |
| qwen35_4b | 12 | q8_0/tbq4 | 6.254 | 2991.957 | n/a |


## Interpretation Scaffold

- Treat `q8_0/tbq4` as the primary deployment candidate if it preserves PPL and prompt scores while improving or staying close to F16/Q8 sustained speed.
- Treat `tbq4/tbq4` as model-dependent unless it clears speed, PPL, and prompt quality on both Gemma and Qwen.
- Do not call the technique lossless unless outputs and PPL are indistinguishable within noise across the full prompt set and both model families.
