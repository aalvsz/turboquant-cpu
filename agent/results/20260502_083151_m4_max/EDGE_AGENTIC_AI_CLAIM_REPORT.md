# Edge Agentic AI Claim Report

Run folder: `agent/results/20260502_083151_m4_max`

## Scope

This run tested a local CPU-only edge-agent workload on the M4 host label
`m4_max`. The measured runner used `llama-server` with GPU layers disabled,
10 inference threads, an 8192-token context, Gemma 4 E4B and Qwen3.5 4B GGUF
models, and the same agent pipeline for every KV-cache configuration.

The agent workload is intentionally end-to-end: an orchestrator LLM chooses
tools, deterministic tools run locally, LLM-powered helper tools call the same
local model, and a final LLM step emits a strict JSON decision. The tool catalog
includes log reading, metric lookup, speedup calculation, KV-memory estimation,
JSON validation, safety-policy inspection, incident scanning, report retrieval,
host snapshotting, LLM summarization, LLM risk classification, LLM schema repair,
and LLM config recommendation.

## Validation Summary

- All 10 model/config combinations completed 5 of 5 tasks.
- All `llama-server` processes exited with return code 0.
- Final answer JSON validity was 100% for every configuration.
- No OOM, kill, fatal, abort, traceback, or segmentation signal was found in the
  run logs.
- The log scan did find invalid JSON events inside the intentional
  `schema_repair` task. Those are task artifacts, not server failures.
- Initial free memory was recorded at 58.0%, and each server launch checked the
  memory guard before starting.

## Q4 Baseline Comparison

Lower wall time is better. Mean score is a lightweight task-success proxy for
this fast agent benchmark, not a replacement for human evaluation or a broad
academic quality benchmark.

| model | config | total wall s | vs Q4 wall | mean score | completion tok/s | max RSS MB |
|---|---|---:|---:|---:|---:|---:|
| gemma4_e4b | q4_0/q4_0 | 81.410 | baseline | 0.733 | 21.705 | 7766.0 |
| gemma4_e4b | tbq4/tbq4 | 70.850 | 13.0% faster | 0.733 | 23.176 | 7752.6 |
| gemma4_e4b | q8_0/tbq4 | 72.193 | 11.3% faster | 0.533 | 23.673 | 7837.7 |
| qwen35_4b | q4_0/q4_0 | 114.374 | baseline | 0.600 | 16.612 | 6339.4 |
| qwen35_4b | tbq4/tbq4 | 97.610 | 14.7% faster | 0.800 | 19.957 | 6278.6 |
| qwen35_4b | q8_0/tbq4 | 112.340 | 1.8% faster | 0.867 | 19.414 | 6569.2 |

## Findings

For Gemma 4, `tbq4/tbq4` is the strongest agent setting in this run. It was
13.0% faster than `q4_0/q4_0`, matched the Q4 mean score, preserved final JSON
validity, and slightly reduced observed server RSS.

For Qwen3.5 4B, `tbq4/tbq4` is also a strong setting. It was 14.7% faster than
`q4_0/q4_0`, improved the benchmark's mean task score from 0.600 to 0.800,
preserved final JSON validity, and slightly reduced observed server RSS.

The mixed `q8_0/tbq4` setting is not uniformly better. It looked attractive for
Qwen because it reached the highest mean score in this run with a small wall-time
gain over Q4. For Gemma, however, it was faster than Q4 but reduced the mean
score proxy. That makes `q8_0/tbq4` a candidate for additional testing, not the
default recommendation.

`f16/f16` was not the best practical edge-agent setting here. It used the most
RSS for both models and did not beat `tbq4/tbq4` on end-to-end wall time.

## Claim Assessment

The M4 CPU results now support this narrower claim:

> On this local CPU-only M4 edge-agent workload, TurboQuant `tbq4/tbq4` KV cache
> improved end-to-end agent wall time versus the Q4 KV baseline for both Gemma 4
> E4B and Qwen3.5 4B while preserving JSON/tool discipline and avoiding observed
> memory failures.

The current evidence does not yet justify calling TurboQuant a strictly
"lossless" optimization for edge agentic AI. The measured task score is a fast
regression signal, the suite has only five tasks per config, and the outputs have
not been judged by a broader quality benchmark or repeated enough times for
statistical confidence. The safer paper language is "quality-preserving in this
agent workload" or "near-lossless under the tested workload."

## Paper Readiness

This is useful evidence for a paper, but it is not sufficient by itself for a
full edge-agentic-AI claim. The M4 run should be treated as the first agentic
workload result. A stronger paper still needs:

- repeated runs on M4 to estimate variance;
- the same harness on Raspberry Pi or another constrained edge CPU;
- the prior x86 CPU results integrated into the same agent report format;
- a quality evaluation beyond the lightweight task score;
- a sustained/thermal run, especially for Raspberry Pi;
- explicit comparison against standard KV-cache settings using the same model,
  prompts, task suite, context length, and thread policy.

## Recommendation

Use `tbq4/tbq4` as the current default TurboQuant candidate for the edge-agent
story. Keep `q4_0/q4_0` as the baseline and keep `q8_0/tbq4` as an exploratory
quality-preserving candidate, especially for Qwen. Do not publish the stronger
"lossless edge agentic AI" claim until the Raspberry Pi and repeated-run evidence
are added.
