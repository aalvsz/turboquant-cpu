# Q4 vs TurboQuant Report

Run folder: `benchmark_results/fresh_edge_agentic_20260501/rerun_qwen35_qualityfix_20260501_161433`

## Question

Is TurboQuant a better option than Q4?

Short answer: yes, if "Q4" means the KV-cache setting `q4_0/q4_0`. In this run, `tbq4/tbq4` is faster than `q4_0/q4_0` in every 8K decode comparison on both ARM and x86. It also gives much better Gemma PPL and essentially equivalent Qwen PPL. The safest deployment candidate is `q8_0/tbq4`, because it also beats Q4 speed in every 8K decode comparison while matching Q4 prompt quality across both devices.

Important caveat: the model files themselves are Q4_0 GGUF weights in every setting. This report compares KV-cache formats, not model-weight quantization formats.

## Recommendation

- Use `tbq4/tbq4` when decode speed and KV memory pressure are the priority.
- Use `q8_0/tbq4` when the deployment needs a more conservative quality posture.
- Do not prefer `q4_0/q4_0` as the default KV-cache option from these results. It is slower than both TBQ candidates at 8K and clearly worse on Gemma PPL.

`q4_0/q4_0` has one narrow advantage: on ARM prompt quality, it scores slightly above `tbq4/tbq4` for both models. But `q8_0/tbq4` matches Q4 prompt quality there while still being faster than Q4 at 8K, so Q4 is not the best overall choice.

## Completion And Validity

All final result rows completed with return code `0`.

| host | speed | sustained | ppl | quality | judge |
|---|---:|---:|---:|---:|---:|
| ARM M4 | 60/60 | 12/12 | 10/10 | 100/100 | 100/100 |
| x86 Axelera | 60/60 | 12/12 | 10/10 | 100/100 | 100/100 |

Qwen PPL was rerun with explicit one-sequence batching (`-b 512 -ub 512`) because the default multi-sequence PPL path was invalid for Qwen3.5 and crashed on `K=q8_0`.

## ARM M4

### 8K Decode Speed vs Q4

Higher is better.

| model | threads | Q4 tok/s | TBQ tok/s | TBQ vs Q4 | Q8/TBQ tok/s | Q8/TBQ vs Q4 |
|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | 6 | 31.582 | 37.635 | +19.2% | 34.552 | +9.4% |
| gemma4_e4b | 10 | 33.663 | 39.392 | +17.0% | 37.753 | +12.2% |
| qwen35_4b | 6 | 22.965 | 27.350 | +19.1% | 24.584 | +7.0% |
| qwen35_4b | 10 | 25.677 | 29.103 | +13.3% | 26.201 | +2.0% |

ARM speed conclusion: both TBQ options beat Q4 in every 8K decode comparison. `tbq4/tbq4` is the speed winner. `q8_0/tbq4` is still faster than Q4, but less aggressively.

### PPL vs Q4

Lower is better.

| model | Q4 PPL | TBQ PPL | TBQ vs Q4 | Q8/TBQ PPL | Q8/TBQ vs Q4 |
|---|---:|---:|---:|---:|---:|
| gemma4_e4b | 134.733 | 114.261 | -15.2% | 113.747 | -15.6% |
| qwen35_4b | 10.399 | 10.399 | +0.0% | 10.411 | +0.1% |

ARM PPL conclusion: TBQ is clearly better than Q4 for Gemma. For Qwen, TBQ and Q4 are effectively tied; `q8_0/tbq4` is only `+0.1%` worse than Q4 PPL.

### Prompt Quality vs Q4

Heuristic score is 0 to 5. Higher is better.

| model | Q4 score | TBQ score | Q8/TBQ score |
|---|---:|---:|---:|
| gemma4_e4b | 3.500 | 3.350 | 3.500 |
| qwen35_4b | 4.600 | 4.400 | 4.600 |

ARM quality conclusion: `q8_0/tbq4` matches Q4 on this prompt suite. `tbq4/tbq4` is slightly weaker than Q4 in the heuristic judge, though it has no degenerate outputs and remains close.

### Sustained Decode

Q4 sustained was not measured in this matrix. Sustained rows include F16, `tbq4/tbq4`, and `q8_0/tbq4`.

| model | threads | F16 tok/s | TBQ tok/s | TBQ vs F16 | Q8/TBQ tok/s | Q8/TBQ vs F16 |
|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | 6 | 35.401 | 37.214 | +5.1% | 34.430 | -2.7% |
| gemma4_e4b | 10 | 35.087 | 39.020 | +11.2% | 37.329 | +6.4% |
| qwen35_4b | 6 | 24.195 | 27.495 | +13.6% | 24.342 | +0.6% |
| qwen35_4b | 10 | 26.827 | 28.800 | +7.4% | 26.232 | -2.2% |

ARM sustained conclusion: `tbq4/tbq4` is consistently better than F16 in sustained 8K decode. `q8_0/tbq4` is mixed against F16, but the short 8K speed matrix still shows it beating Q4.

## x86 Axelera

### 8K Decode Speed vs Q4

Higher is better.

| model | threads | Q4 tok/s | TBQ tok/s | TBQ vs Q4 | Q8/TBQ tok/s | Q8/TBQ vs Q4 |
|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | 6 | 7.924 | 9.193 | +16.0% | 8.843 | +11.6% |
| gemma4_e4b | 12 | 7.706 | 8.986 | +16.6% | 8.868 | +15.1% |
| qwen35_4b | 6 | 6.284 | 6.923 | +10.2% | 6.615 | +5.3% |
| qwen35_4b | 12 | 5.924 | 6.495 | +9.6% | 6.287 | +6.1% |

x86 speed conclusion: TBQ dominates Q4 in every 8K decode comparison. The gain is especially strong for Gemma, but Qwen also benefits consistently.

### PPL vs Q4

Lower is better.

| model | Q4 PPL | TBQ PPL | TBQ vs Q4 | Q8/TBQ PPL | Q8/TBQ vs Q4 |
|---|---:|---:|---:|---:|---:|
| gemma4_e4b | 133.774 | 113.864 | -14.9% | 116.719 | -12.7% |
| qwen35_4b | 10.401 | 10.413 | +0.1% | 10.390 | -0.1% |

x86 PPL conclusion: TBQ is much better than Q4 for Gemma. For Qwen, all three settings are effectively tied; `q8_0/tbq4` is slightly better than Q4 and `tbq4/tbq4` is slightly worse, both by about one tenth of a percent.

### Prompt Quality vs Q4

Heuristic score is 0 to 5. Higher is better.

| model | Q4 score | TBQ score | Q8/TBQ score |
|---|---:|---:|---:|
| gemma4_e4b | 3.500 | 3.500 | 3.500 |
| qwen35_4b | 4.400 | 4.400 | 4.400 |

x86 quality conclusion: TBQ and Q4 are tied on the deterministic prompt judge.

### Sustained Decode

Q4 sustained was not measured in this matrix. Sustained rows include F16, `tbq4/tbq4`, and `q8_0/tbq4`.

| model | threads | F16 tok/s | TBQ tok/s | TBQ vs F16 | Q8/TBQ tok/s | Q8/TBQ vs F16 |
|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | 6 | 7.230 | 9.166 | +26.8% | 8.827 | +22.1% |
| gemma4_e4b | 12 | 7.042 | 8.953 | +27.1% | 8.800 | +25.0% |
| qwen35_4b | 6 | 5.270 | 6.921 | +31.3% | 6.620 | +25.6% |
| qwen35_4b | 12 | 5.071 | 6.498 | +28.1% | 6.254 | +23.3% |

x86 sustained conclusion: both TBQ options are strongly better than F16. Since both TBQ options also beat Q4 in the short 8K speed matrix, Q4 has no clear x86 advantage in this run.

## Cross-Device Decision

### `tbq4/tbq4` vs Q4

`tbq4/tbq4` is the better speed option.

- Faster than Q4 in all 8 out of 8 8K decode comparisons.
- Speed gain range vs Q4: `+9.6%` to `+19.2%`.
- Better Gemma PPL by about `15%`.
- Qwen PPL is effectively tied with Q4.
- Prompt quality is tied on x86 but slightly below Q4 on ARM.

Use it when speed and memory bandwidth are the top priority and the slight ARM heuristic-score dip is acceptable.

### `q8_0/tbq4` vs Q4

`q8_0/tbq4` is the better default replacement for Q4.

- Faster than Q4 in all 8 out of 8 8K decode comparisons.
- Speed gain range vs Q4: `+2.0%` to `+15.1%`.
- Better Gemma PPL by about `13-16%`.
- Qwen PPL is effectively tied with Q4.
- Prompt quality matches Q4 on both ARM and x86.

Use it when you want a conservative quality posture for edge agentic deployment.

## Final Answer

Yes, TurboQuant is a better option than Q4 for KV-cache deployment in this test matrix.

The strongest statement supported by the data is:

> TurboQuant KV, especially `q8_0/tbq4` for conservative quality and `tbq4/tbq4` for maximum speed, outperforms `q4_0/q4_0` KV on both ARM and x86 while preserving PPL and prompt quality within this benchmark suite.

The claim should still avoid the word "lossless". The results support "quality-preserving" or "near-lossless in this matrix", not strict losslessness.
