# Findings: Agentic KV-Cache Quantization on M4 and Raspberry Pi

## Scope

This report measures end-to-end local agent behavior: LLM planning, deterministic tools, LLM-powered tools, and final JSON synthesis. The model weights are fixed 4-bit GGUF files; the tested variable is the KV-cache format.

## Raspberry Pi 5 8GB

### Qwen3.5 4B, 8K Context

| config | wall s | vs Q4 | quality | delta Q4 | JSON | tool | max RSS MB |
|---|---:|---:|---:|---:|---:|---:|---:|
| f16/f16 | 1617.973 | -16.7% | 0.796 | 0.000 | 1.000 | 1.000 | 7152.6 |
| q4_0/q4_0 | 1386.054 | 0.0% | 0.796 | 0.000 | 1.000 | 1.000 | 7045.2 |
| q8_0/q8_0 | 1406.362 | -1.5% | 0.760 | -0.035 | 1.000 | 1.000 | 6985.8 |
| q8_0/tbq4 | 1333.212 | 3.8% | 0.794 | -0.002 | 1.000 | 1.000 | 7056.2 |
| tbq4/tbq4 | 1400.740 | -1.1% | 0.769 | -0.027 | 1.000 | 1.000 | 7045.2 |

Best Qwen Pi result is `q8_0/tbq4`: it is 3.8% faster than Q4 and 17.6% faster than F16 while preserving JSON/tool reliability and nearly matching Q4 quality.

### Gemma 4 E4B, 4K Context

| config | wall s | vs Q4 | quality | delta Q4 | JSON | tool | max RSS MB |
|---|---:|---:|---:|---:|---:|---:|---:|
| f16/f16 | 1008.648 | 2.7% | 0.812 | 0.037 | 1.000 | 1.000 | 6818.8 |
| q4_0/q4_0 | 1036.571 | 0.0% | 0.775 | 0.000 | 1.000 | 1.000 | 7343.8 |
| q8_0/q8_0 | 977.822 | 5.7% | 0.812 | 0.037 | 1.000 | 1.000 | 7367.8 |
| q8_0/tbq4 | 951.917 | 8.2% | 0.829 | 0.054 | 1.000 | 1.000 | 7441.3 |
| tbq4/tbq4 | 976.312 | 5.8% | 0.829 | 0.054 | 1.000 | 1.000 | 7456.9 |

Best Gemma Pi result is `q8_0/tbq4`: it is 8.2% faster than Q4 and 5.6% faster than F16, with the highest measured quality. Gemma at 8K was not attempted because 4K already pushed RSS above 7.4 GB.

## M4 Max

- Gemma at 8K: `q8_0/tbq4` was fastest, and `tbq4/tbq4` preserved high quality while beating Q4 latency.
- Qwen at 8K: `tbq4/tbq4` was slightly faster and lower RSS than Q4, but quality dipped; `q8_0/tbq4` was not quality-safe on M4 Qwen in this run.

## Claim Implication

The data supports a workload-scoped claim, not a universal one:

> KV-cache quantization, especially mixed `q8_0/tbq4`, can improve CPU-only edge-agent latency while preserving JSON/tool reliability in the tested local-agent suite.

The data does not support saying TurboQuant is universally lossless. A safer paper framing is:

> KV-Cache Quantization for CPU-Only Edge Agents: Latency, Energy, and Tool-Use Reliability.

Use "task-level non-inferior in the tested suite" rather than "lossless" unless a stricter equivalence proof is added.
