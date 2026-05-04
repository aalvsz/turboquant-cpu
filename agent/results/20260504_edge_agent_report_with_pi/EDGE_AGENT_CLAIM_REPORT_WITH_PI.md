# Edge Agent TurboQuant Claim Report With Raspberry Pi

Generated: 2026-05-05

## Scope

- Devices now covered: Apple M4 Max ARM64, Axelera x86 CPU host, and Raspberry Pi 5 8GB over Tailscale.
- Agent workload: CPU-only local `llama-server`, 5 tool-heavy edge-agent tasks per row, LLM planner, deterministic tools, LLM-powered helper tools, and final structured JSON synthesis.
- KV configs: `f16/f16`, `q8_0/q8_0`, `q4_0/q4_0`, `q8_0/tbq4`, `tbq4/tbq4`.
- Pi coverage: Qwen 3.5 4B at 8K context; Gemma 4 E4B at 4K context because the 4.6 GiB Gemma GGUF already reached about 7.4 GiB RSS at 4K. Running Gemma F16 at 8K on this 8 GiB Pi would be an avoidable OOM risk.
- Pi validity: 10/10 full Pi rows completed, 50/50 Pi agent tasks executed, 0 server failures, 100% final JSON validity, and `vcgencmd get_throttled` stayed `0x0` in every Pi row.

## Bottom Line

We now have enough evidence for a credible edge-agent framing: `KV-Cache Quantization for CPU-Only Edge Agents: Latency, Energy, and Tool-Use Reliability`. The strongest supported claim is workload-scoped: TurboQuant KV cache formats can improve CPU-only edge-agent latency versus Q4 while preserving tool/JSON reliability in the tested suite. On Raspberry Pi 5 with Qwen at 8K, both TurboQuant variants also beat F16 end-to-end.

We still should not claim strict losslessness. Quality is stable or better than Q4 in the Pi rows, but prior M4/x86 Qwen rows remain mixed, and all current paper rows are single repeats. The paper claim should be `quality-preserving in the tested agent suite`, not `lossless`.

## Raspberry Pi 5 Qwen 3.5 4B, 8K Context

| config | wall s | vs Q4 wall | vs F16 wall | quality | quality vs Q4 | JSON | plan valid | max RSS MB | max temp C | throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f16/f16 | 1822.6 | -12.3% | +0.0% | 0.713 | +0.000 | 1.000 | 0.800 | 6798 | 77.1 | 0x0 |
| q4_0/q4_0 | 2079.4 | +0.0% | +14.1% | 0.713 | +0.000 | 1.000 | 0.600 | 6299 | 76.5 | 0x0 |
| q8_0/q8_0 | 2078.1 | -0.1% | +14.0% | 0.673 | -0.040 | 1.000 | 0.800 | 6552 | 77.1 | 0x0 |
| q8_0/tbq4 | 1745.9 | -16.0% | -4.2% | 0.760 | +0.047 | 1.000 | 0.800 | 6332 | 76.5 | 0x0 |
| tbq4/tbq4 | 1650.4 | -20.6% | -9.4% | 0.747 | +0.033 | 1.000 | 0.800 | 6219 | 76.5 | 0x0 |

Key Pi Qwen result: `tbq4/tbq4` was fastest at 1650.4s, 20.6% lower wall time than Q4 and 9.5% lower than F16. `q8_0/tbq4` was second at 1745.9s, 16.0% lower than Q4 and 4.2% lower than F16. Both preserved final JSON validity and exceeded Q4 quality.

## Raspberry Pi 5 Gemma 4 E4B, 4K Context

| config | wall s | vs Q4 wall | vs F16 wall | quality | quality vs Q4 | JSON | plan valid | max RSS MB | max temp C | throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f16/f16 | 1091.8 | -16.9% | +0.0% | 0.727 | -0.060 | 1.000 | 1.000 | 7387 | 77.7 | 0x0 |
| q4_0/q4_0 | 1313.5 | +0.0% | +20.3% | 0.787 | +0.000 | 1.000 | 1.000 | 7310 | 76.5 | 0x0 |
| q8_0/q8_0 | 1140.4 | -13.2% | +4.5% | 0.787 | +0.000 | 1.000 | 1.000 | 7377 | 77.7 | 0x0 |
| q8_0/tbq4 | 1127.0 | -14.2% | +3.2% | 0.787 | +0.000 | 1.000 | 1.000 | 7410 | 77.1 | 0x0 |
| tbq4/tbq4 | 1136.3 | -13.5% | +4.1% | 0.800 | +0.013 | 1.000 | 1.000 | 7429 | 77.1 | 0x0 |

Key Pi Gemma result: F16 remained fastest at 4K, but all non-Q4 alternatives beat Q4. Full `tbq4/tbq4` had the best quality at 0.800 and was 13.5% faster than Q4, though 4.1% slower than F16. This supports TurboQuant as a better option than Q4, not as universally faster than F16.

## Pi Compact Low-Level Profile

CPU-only `llama-bench`, 4 threads, flash attention on, 1024-token prompt and 32-token decode, 1 repetition. This isolates prompt/decode behavior from agent planning choices.

| model | config | prompt tok/s | prompt vs F16 | prompt vs Q4 | decode tok/s | decode vs F16 | decode vs Q4 |
|---|---|---:|---:|---:|---:|---:|---:|
| gemma4_e4b | f16/f16 | 20.233 | +0.0% | +22.6% | 3.402 | +0.0% | +2.8% |
| gemma4_e4b | q4_0/q4_0 | 16.497 | -18.5% | +0.0% | 3.309 | -2.7% | +0.0% |
| gemma4_e4b | q8_0/q8_0 | 18.736 | -7.4% | +13.6% | 3.362 | -1.2% | +1.6% |
| gemma4_e4b | q8_0/tbq4 | 19.021 | -6.0% | +15.3% | 3.286 | -3.4% | -0.7% |
| gemma4_e4b | tbq4/tbq4 | 18.867 | -6.8% | +14.4% | 3.377 | -0.7% | +2.0% |

| qwen35_4b | f16/f16 | 20.559 | +0.0% | +5.9% | 2.201 | +0.0% | -1.5% |
| qwen35_4b | q4_0/q4_0 | 19.416 | -5.6% | +0.0% | 2.234 | +1.5% | +0.0% |
| qwen35_4b | q8_0/q8_0 | 20.311 | -1.2% | +4.6% | 2.221 | +0.9% | -0.6% |
| qwen35_4b | q8_0/tbq4 | 20.527 | -0.2% | +5.7% | 2.223 | +1.0% | -0.5% |
| qwen35_4b | tbq4/tbq4 | 20.516 | -0.2% | +5.7% | 2.228 | +1.2% | -0.3% |

Interpretation: the low-level Pi profile explains why TBQ is not automatically faster than F16. For Gemma, F16 still has the best prompt throughput; TBQ is 6-7% behind F16 but 14-15% ahead of Q4. For Qwen, TBQ prompt throughput is effectively tied with F16 and about 5.7% ahead of Q4. End-to-end agent wins can be larger because planner/tool choices and repeated long prompt evaluations amplify these differences.

## Claim Assessment

- Supported: CPU-only edge agents can run with TurboQuant KV formats on M4, x86, and Raspberry Pi while keeping final JSON validity at 100% in this task suite.
- Supported: TurboQuant is a better option than Q4 for Pi Qwen 8K and Pi Gemma 4K on latency, with Pi Qwen also beating F16 end-to-end.
- Supported: The Pi adds a real constrained edge target, and the no-throttling telemetry makes the latency comparison usable.
- Not supported: a broad `lossless optimization` claim across models, tasks, and CPUs.
- Not yet full-paper complete: we still need 3-5 repeats, a larger task suite, and controlled power measurement if energy is a central claim. Pi SoC power was not captured, only temperature/throttle state.

## Artifacts

- `agent/results/20260504_pi_qwen_core8k/`: full Pi Qwen 8K agent matrix.
- `agent/results/20260504_pi_gemma_core4k/`: full Pi Gemma 4K agent matrix.
- `agent/results/20260504_pi_llama_bench_compact/`: compact Pi low-level prompt/decode profile.
- `agent/results/20260504_edge_agent_report_with_pi/`: combined aggregate tables across M4, x86, and Pi.
