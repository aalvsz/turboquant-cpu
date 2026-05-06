# Findings: Agentic KV-Cache Quantization on M4, Raspberry Pi, and x86

## Execution Status

- Completed fresh x86 CPU run on `axelera-ander-wfh` / `x86_i5_12500_agentic_8k`.
- Copied the completed x86 folder into `agent/results/20260506_x86_agentic_impact_8k`.
- Regenerated the combined report in this folder from M4, Raspberry Pi, and x86 inputs.
- x86 memory stayed safe throughout the run; final post-run state had about 22 GiB available.
- x86 telemetry captured RAPL package energy and package thermal peaks. The x86 run reached 90-91 C package peaks but reported no throttling flag.

## Benchmark Coverage

The suite has 8 agentic tasks per model/config:

- `safety_gate`
- `schema_repair`
- `tool_timeout_recovery`
- `retrieval_dedup`
- `reasoning_budget_tradeoff`
- `reasoning_memory_latency_tradeoff`
- `claim_language_audit`
- `deployment_rank_quality`

Each row reports end-to-end wall time, JSON validity, plan validity, tool-use score, correctness/reasoning score, safety score, RSS, and device telemetry where available. Model weights stay 4-bit GGUF; only KV-cache type changes.

## x86 Results

### Gemma 4 E4B, ctx 8192

| config | wall s | vs Q4 | quality | correct | RSS MB | energy J | therm C |
|---|---:|---:|---:|---:|---:|---:|---:|
| q4_0/q4_0 | 345.1 | 0.0% | 0.800 | 0.750 | 7662.8 | 22626 | 90 |
| f16/f16 | 327.8 | 5.0% | 0.812 | 0.729 | 8610.6 | 21437 | 90 |
| q8_0/q8_0 | 327.2 | 5.2% | 0.812 | 0.729 | 7995.6 | 21418 | 90 |
| q8_0/tbq4 | 342.6 | 0.7% | 0.808 | 0.771 | 7818.6 | 22340 | 90 |
| tbq4/tbq4 | 332.0 | 3.8% | 0.840 | 0.802 | 7647.1 | 21667 | 88 |

Gemma on x86 is the strongest TurboQuant result: `tbq4/tbq4` has the best quality, is faster than Q4, uses less RSS than F16, and is only slightly slower than F16/Q8. It does not beat F16 on raw latency, but it is a better quality/memory compromise.

### Qwen3.5 4B, ctx 8192

| config | wall s | vs Q4 | quality | correct | RSS MB | energy J | therm C |
|---|---:|---:|---:|---:|---:|---:|---:|
| q4_0/q4_0 | 458.8 | 0.0% | 0.819 | 0.635 | 7029.6 | 29849 | 91 |
| f16/f16 | 450.0 | 1.9% | 0.840 | 0.740 | 7480.6 | 29317 | 90 |
| q8_0/q8_0 | 451.7 | 1.6% | 0.800 | 0.542 | 7200.4 | 29419 | 91 |
| q8_0/tbq4 | 424.2 | 7.5% | 0.773 | 0.531 | 6946.6 | 27700 | 90 |
| tbq4/tbq4 | 439.8 | 4.1% | 0.802 | 0.552 | 6978.8 | 28690 | 91 |

Qwen on x86 is not a lossless TurboQuant win. The fastest and lowest-energy row is `q8_0/tbq4`, but it takes a visible quality/correctness hit. `f16/f16` remains the quality leader when memory fits.

## Cross-Device Read

- Gemma is consistently favorable to TBQ: M4 and Raspberry Pi both show TBQ-containing configs improving latency over Q4 without breaking JSON/tool use, and x86 `tbq4/tbq4` gives the best x86 quality.
- Qwen is mixed: Raspberry Pi `q8_0/tbq4` is a useful latency result with near-Q4 quality, but x86 and M4 show quality sensitivity in several TBQ/Q8 rows.
- JSON and tool-use validity were stable across all x86 rows at 1.0, so the main regression signal is not parser failure; it is task correctness/reasoning quality.
- F16 remains competitive or faster when the full context fits in memory. KV quantization is most compelling under memory pressure, longer contexts, concurrency, or lower-power devices.

## Claim Status

The data supports a paper framed as "KV-Cache Quantization for CPU-Only Edge Agents: Latency, Energy, and Tool-Use Reliability".

The data does not yet support a universal claim that TurboQuant is lossless for edge agentic AI. The defensible claim is narrower: TurboQuant/TBQ-containing KV-cache configurations can improve CPU-only edge-agent latency and memory footprint while preserving JSON/tool reliability, with model- and device-dependent quality tradeoffs. Gemma is currently the best positive case; Qwen needs careful config selection and should be reported as a mixed case.

## Files

- Main report: `AGENTIC_KV_IMPACT_REPORT.md`
- Aggregated runs: `run_summary.csv`
- Per-category breakdown: `category_impact.csv`
- x86 raw run: `../20260506_x86_agentic_impact_8k`
