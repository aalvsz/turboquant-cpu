# Gemma 4 E4B Subagent LLM Judge

**Date:** 2026-04-30

**Input:** `turboquant/results/paper_quality/gemma4_e4b_generations.jsonl`

**Judge:** GPT-5.5-class chat subagent in this Codex session. No OpenAI API key
or external API call was used.

## Rubric

- Correctness: 0-5
- Completeness: 0-5
- Coherence: 0-5
- Safety: 0-5
- Degenerate: boolean

The judge compared each quantized output to the prompt, the reference answer,
and the F16 output for the same prompt.

## Summary

| KV setting | Correctness | Completeness | Coherence | Safety | Degenerate rate | Qualitative issues |
|---|---:|---:|---:|---:|---:|---|
| `f16/f16` | 3.80 | 2.60 | 3.20 | 4.80 | 0/5 | Accurate starts, but prompts 2-5 are cut off by token limit; Fibonacci lacks a complete function; haiku lacks the requested example. |
| `q8_0/q8_0` | 3.80 | 2.60 | 3.20 | 4.80 | 0/5 | Byte-identical to `f16/f16` on all prompts. |
| `q4_0/q4_0` | 3.80 | 2.60 | 3.20 | 4.80 | 0/5 | Minor wording differences only; same truncation-driven failures as baseline. |
| `tbq4/tbq4` | 3.80 | 2.60 | 3.00 | 4.80 | 0/5 | Same factual quality overall, but stroke answer ends slightly more awkwardly mid-bullet than baseline. |
| `q8_0/tbq4` | 3.80 | 2.60 | 3.20 | 4.80 | 0/5 | Minor wording differences; no meaningful quality loss relative to baseline. |

## Interpretation

`tbq4/tbq4` shows only a very small coherence degradation versus `f16/f16`,
not a correctness or safety degradation. `q8_0/tbq4` does not show meaningful
degradation versus `f16/f16`.

The dominant quality issue is not quantization; it is the 120-token generation
limit. Prompts 2-5 are truncated across settings, which depresses completeness.
No output is degenerate, nonsensical, unsafe, or obviously corrupted by KV
quantization.
