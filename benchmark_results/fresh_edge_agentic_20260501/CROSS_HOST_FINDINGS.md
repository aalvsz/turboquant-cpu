# Cross-Host Fresh TurboQuant Findings

## Current ARM Caveat

The ARM/Gemma TBQ4 speed rows should not be used as publication-grade evidence
until they are rerun under the CPU-load gate added on 2026-05-01. A follow-up
investigation found the current ARM host at load average 5-6 with no model
process active, and the old optimized binary no longer reproduced its
historical `q8_0/tbq4` speedup under that noisy host state. See
`ARM_TBQ4_REGRESSION_INVESTIGATION.md`.

## Current Qwen Caveat

The older Qwen3.5 quality rows in this cross-host report are superseded. The
old TurboQuant build routed `qwen35` through an incomplete Qwen3Next graph path,
which produced degenerate text even with F16 KV. The ARM fix and replacement
focused Qwen quality run are documented in
`qwen_quality_fix/QWEN_QUALITY_FIX_REPORT.md`; the x86 host still needs the same
rebuild/rerun before cross-host Qwen quality is updated.

# Fresh Findings: arm_m4

## 8K Decode Speed

| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |
|---|---:|---|---:|---:|---:|---:|
| gemma4_e4b | 10 | f16/f16 | 26.064 | +0.0% | +0.6% | +9.8% |
| gemma4_e4b | 10 | q8_0/q8_0 | 25.901 | -0.6% | +0.0% | +9.1% |
| gemma4_e4b | 10 | q4_0/q4_0 | 23.738 | -8.9% | -8.4% | +0.0% |
| gemma4_e4b | 10 | tbq4/tbq4 | 19.754 | -24.2% | -23.7% | -16.8% |
| gemma4_e4b | 10 | q8_0/tbq4 | 23.758 | -8.8% | -8.3% | +0.1% |
| gemma4_e4b | 6 | f16/f16 | 36.449 | +0.0% | +11.7% | +14.0% |
| gemma4_e4b | 6 | q8_0/q8_0 | 32.624 | -10.5% | +0.0% | +2.1% |
| gemma4_e4b | 6 | q4_0/q4_0 | 31.963 | -12.3% | -2.0% | +0.0% |
| gemma4_e4b | 6 | tbq4/tbq4 | 23.684 | -35.0% | -27.4% | -25.9% |
| gemma4_e4b | 6 | q8_0/tbq4 | 25.709 | -29.5% | -21.2% | -19.6% |
| qwen35_4b | 10 | f16/f16 | 15.721 | +0.0% | +9.7% | +8.5% |
| qwen35_4b | 10 | q8_0/q8_0 | 14.327 | -8.9% | +0.0% | -1.2% |
| qwen35_4b | 10 | q4_0/q4_0 | 14.495 | -7.8% | +1.2% | +0.0% |
| qwen35_4b | 10 | tbq4/tbq4 | 12.136 | -22.8% | -15.3% | -16.3% |
| qwen35_4b | 10 | q8_0/tbq4 | 14.160 | -9.9% | -1.2% | -2.3% |
| qwen35_4b | 6 | f16/f16 | 17.450 | +0.0% | +8.6% | +6.5% |
| qwen35_4b | 6 | q8_0/q8_0 | 16.065 | -7.9% | +0.0% | -2.0% |
| qwen35_4b | 6 | q4_0/q4_0 | 16.390 | -6.1% | +2.0% | +0.0% |
| qwen35_4b | 6 | tbq4/tbq4 | 14.332 | -17.9% | -10.8% | -12.6% |
| qwen35_4b | 6 | q8_0/tbq4 | 14.895 | -14.6% | -7.3% | -9.1% |

## Perplexity

| model | config | ppl | delta vs f16 | returncode |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 117.662 | +0.0% | 0 |
| gemma4_e4b | q4_0/q4_0 | 134.733 | +14.5% | 0 |
| gemma4_e4b | q8_0/q8_0 | 117.761 | +0.1% | 0 |
| gemma4_e4b | q8_0/tbq4 | 116.887 | -0.7% | 0 |
| gemma4_e4b | tbq4/tbq4 | 113.843 | -3.2% | 0 |
| qwen35_4b | f16/f16 | 398.124 | +0.0% | 0 |
| qwen35_4b | q4_0/q4_0 | 404.342 | +1.6% | 0 |
| qwen35_4b | q8_0/q8_0 | 393.263 | -1.2% | 0 |
| qwen35_4b | q8_0/tbq4 | 400.796 | +0.7% | 0 |
| qwen35_4b | tbq4/tbq4 | 415.395 | +4.3% | 0 |

## Deterministic Prompt Judge

| model | setting | n | mean score | degenerate rate |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q4_0/q4_0 | 10 | 3.500 | 0.000 |
| gemma4_e4b | q8_0/q8_0 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q8_0/tbq4 | 10 | 3.500 | 0.000 |
| gemma4_e4b | tbq4/tbq4 | 10 | 3.500 | 0.000 |
| qwen35_4b | f16/f16 | 10 | 0.150 | 0.100 |
| qwen35_4b | q4_0/q4_0 | 10 | 0.150 | 0.100 |
| qwen35_4b | q8_0/q8_0 | 10 | 0.050 | 0.100 |
| qwen35_4b | q8_0/tbq4 | 10 | 0.050 | 0.100 |
| qwen35_4b | tbq4/tbq4 | 10 | 0.050 | 0.000 |

## Sustained 8K Decode

| model | threads | config | tok/s | max RSS MB | energy J |
|---|---:|---|---:|---:|---:|
| gemma4_e4b | 6 | f16/f16 | 36.320 | 4793.109 | n/a |
| gemma4_e4b | 6 | tbq4/tbq4 | 23.611 | 5889.578 | n/a |
| gemma4_e4b | 6 | q8_0/tbq4 | 25.480 | 5863.922 | n/a |
| gemma4_e4b | 10 | f16/f16 | 23.934 | 6134.672 | n/a |
| gemma4_e4b | 10 | tbq4/tbq4 | 20.446 | 5890.172 | n/a |
| gemma4_e4b | 10 | q8_0/tbq4 | 24.742 | 5868.578 | n/a |
| qwen35_4b | 6 | f16/f16 | 17.375 | 4414.406 | n/a |
| qwen35_4b | 6 | tbq4/tbq4 | 14.348 | 4036.375 | n/a |
| qwen35_4b | 6 | q8_0/tbq4 | 14.872 | 4105.672 | n/a |
| qwen35_4b | 10 | f16/f16 | 15.771 | 4410.891 | n/a |
| qwen35_4b | 10 | tbq4/tbq4 | 11.621 | 4036.578 | n/a |
| qwen35_4b | 10 | q8_0/tbq4 | 14.100 | 4101.406 | n/a |


# Fresh Findings: x86_axelera

## 8K Decode Speed

| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |
|---|---:|---|---:|---:|---:|---:|
| gemma4_e4b | 12 | f16/f16 | 7.082 | +0.0% | -15.6% | -8.0% |
| gemma4_e4b | 12 | q8_0/q8_0 | 8.387 | +18.4% | +0.0% | +8.9% |
| gemma4_e4b | 12 | q4_0/q4_0 | 7.700 | +8.7% | -8.2% | +0.0% |
| gemma4_e4b | 12 | tbq4/tbq4 | 8.896 | +25.6% | +6.1% | +15.5% |
| gemma4_e4b | 12 | q8_0/tbq4 | 8.887 | +25.5% | +6.0% | +15.4% |
| gemma4_e4b | 6 | f16/f16 | 7.251 | +0.0% | -15.2% | -7.8% |
| gemma4_e4b | 6 | q8_0/q8_0 | 8.553 | +18.0% | +0.0% | +8.7% |
| gemma4_e4b | 6 | q4_0/q4_0 | 7.866 | +8.5% | -8.0% | +0.0% |
| gemma4_e4b | 6 | tbq4/tbq4 | 9.205 | +27.0% | +7.6% | +17.0% |
| gemma4_e4b | 6 | q8_0/tbq4 | 8.806 | +21.4% | +3.0% | +11.9% |
| qwen35_4b | 12 | f16/f16 | 5.386 | +0.0% | -14.2% | -12.5% |
| qwen35_4b | 12 | q8_0/q8_0 | 6.276 | +16.5% | +0.0% | +1.9% |
| qwen35_4b | 12 | q4_0/q4_0 | 6.159 | +14.3% | -1.9% | +0.0% |
| qwen35_4b | 12 | tbq4/tbq4 | 6.784 | +25.9% | +8.1% | +10.1% |
| qwen35_4b | 12 | q8_0/tbq4 | 6.553 | +21.7% | +4.4% | +6.4% |
| qwen35_4b | 6 | f16/f16 | 5.490 | +0.0% | -16.2% | -14.5% |
| qwen35_4b | 6 | q8_0/q8_0 | 6.550 | +19.3% | +0.0% | +2.0% |
| qwen35_4b | 6 | q4_0/q4_0 | 6.420 | +16.9% | -2.0% | +0.0% |
| qwen35_4b | 6 | tbq4/tbq4 | 7.247 | +32.0% | +10.6% | +12.9% |
| qwen35_4b | 6 | q8_0/tbq4 | 6.859 | +24.9% | +4.7% | +6.8% |

## Perplexity

| model | config | ppl | delta vs f16 | returncode |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 117.949 | +0.0% | 0 |
| gemma4_e4b | q4_0/q4_0 | 133.774 | +13.4% | 0 |
| gemma4_e4b | q8_0/q8_0 | 117.470 | -0.4% | 0 |
| gemma4_e4b | q8_0/tbq4 | 116.719 | -1.0% | 0 |
| gemma4_e4b | tbq4/tbq4 | 113.864 | -3.5% | 0 |
| qwen35_4b | f16/f16 | 392.419 | +0.0% | 0 |
| qwen35_4b | q4_0/q4_0 | 398.039 | +1.4% | 0 |
| qwen35_4b | q8_0/q8_0 | 396.062 | +0.9% | 0 |
| qwen35_4b | q8_0/tbq4 | 401.109 | +2.2% | 0 |
| qwen35_4b | tbq4/tbq4 | 413.479 | +5.4% | 0 |

## Deterministic Prompt Judge

| model | setting | n | mean score | degenerate rate |
|---|---|---:|---:|---:|
| gemma4_e4b | f16/f16 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q4_0/q4_0 | 10 | 3.500 | 0.000 |
| gemma4_e4b | q8_0/q8_0 | 10 | 3.700 | 0.000 |
| gemma4_e4b | q8_0/tbq4 | 10 | 3.500 | 0.000 |
| gemma4_e4b | tbq4/tbq4 | 10 | 3.500 | 0.000 |
| qwen35_4b | f16/f16 | 10 | 0.050 | 0.000 |
| qwen35_4b | q4_0/q4_0 | 10 | 0.200 | 0.300 |
| qwen35_4b | q8_0/q8_0 | 10 | 0.050 | 0.000 |
| qwen35_4b | q8_0/tbq4 | 10 | 0.050 | 0.000 |
| qwen35_4b | tbq4/tbq4 | 10 | 0.150 | 0.000 |

## Sustained 8K Decode

| model | threads | config | tok/s | max RSS MB | energy J |
|---|---:|---|---:|---:|---:|
| gemma4_e4b | 6 | f16/f16 | 7.206 | 5534.215 | n/a |
| gemma4_e4b | 6 | tbq4/tbq4 | 9.166 | 5403.449 | n/a |
| gemma4_e4b | 6 | q8_0/tbq4 | 8.805 | 5332.258 | n/a |
| gemma4_e4b | 12 | f16/f16 | 7.047 | 5534.246 | n/a |
| gemma4_e4b | 12 | tbq4/tbq4 | 8.850 | 5289.781 | n/a |
| gemma4_e4b | 12 | q8_0/tbq4 | 8.869 | 5383.582 | n/a |
| qwen35_4b | 6 | f16/f16 | 5.431 | 3297.590 | n/a |
| qwen35_4b | 6 | tbq4/tbq4 | 7.173 | 2923.727 | n/a |
| qwen35_4b | 6 | q8_0/tbq4 | 6.824 | 2988.723 | n/a |
| qwen35_4b | 12 | f16/f16 | 5.321 | 3297.629 | n/a |
| qwen35_4b | 12 | tbq4/tbq4 | 6.794 | 2923.805 | n/a |
| qwen35_4b | 12 | q8_0/tbq4 | 6.568 | 2988.836 | n/a |


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


## Interpretation Scaffold

- Treat `q8_0/tbq4` as the primary deployment candidate if it preserves PPL and prompt scores while improving or staying close to F16/Q8 sustained speed.
- Treat `tbq4/tbq4` as model-dependent unless it clears speed, PPL, and prompt quality on both Gemma and Qwen.
- Do not call the technique lossless unless outputs and PPL are indistinguishable within noise across the full prompt set and both model families.
