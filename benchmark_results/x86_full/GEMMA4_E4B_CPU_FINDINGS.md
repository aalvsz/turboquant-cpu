# Gemma 4 E4B CPU Decode Findings

**Date:** 2026-04-30

**CPU:** Intel Core i5-12500 class x86 CPU, AVX2/AVX-VNNI capable

**Model:** Gemma 4 E4B IT, Q4_0 GGUF

**Benchmark:** `llama-bench`, CPU only, 6 threads, flash attention enabled,
`n_prompt=0`, `n_gen=16`, `repetitions=2`

This note records the local Gemma 4 E4B CPU investigation after adding scoped
Gemma 4 support to the bundled `llama.cpp` tree and optimizing the TurboQuant
decode path. Raw benchmark CSV files are intentionally not checked in because
they include local absolute model paths. The sanitized summary is stored in
`results/gemma4_e4b_cpu_summary.csv`.

## Summary

The useful TurboQuant speedup appears at longer KV depths. At shallow depth,
TBQ4 is neutral to slightly slower than F16/Q8. Once the KV cache is large
enough for attention bandwidth and cache traversal to matter, TBQ4 becomes the
fastest tested symmetric KV cache type.

Follow-up quality checks now exist for the same local Gemma 4 E4B GGUF. The
preliminary 20-chunk WikiText-2 perplexity run does not show a TBQ4 quality
regression; `tbq4/tbq4` is actually the lowest-PPL setting in this small run.
That result is promising but still needs a larger eval before paper submission.

At 8192 KV depth:

- `f16/f16`: 7.071 tok/s
- `q8_0/q8_0`: 8.575 tok/s
- `q4_0/q4_0`: 7.880 tok/s
- `tbq4/tbq4`: 9.193 tok/s

That makes `tbq4/tbq4`:

- 30.0% faster than F16
- 7.2% faster than Q8
- 16.7% faster than Q4_0

## Results

Throughput is decode tokens per second.

| KV depth | F16/F16 | Q8_0/Q8_0 | Q4_0/Q4_0 | TBQ4/TBQ4 | TBQ4 vs F16 | TBQ4 vs Q8 | TBQ4 vs Q4 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 10.041 | 10.026 | n/a | 9.908 | -1.3% | -1.2% | n/a |
| 512 | 9.785 | 9.756 | n/a | 9.783 | -0.0% | +0.3% | n/a |
| 2048 | 9.248 | 9.512 | 8.961 | 9.668 | +4.5% | +1.6% | +7.9% |
| 4096 | 8.681 | 9.161 | 8.552 | 9.536 | +9.8% | +4.1% | +11.5% |
| 8192 | 7.071 | 8.575 | 7.880 | 9.193 | +30.0% | +7.2% | +16.7% |

## Quality Follow-Up

These are preliminary quality checks collected after fixing Gemma 4 prompt
tokenization in the local `llama.cpp` tree. The benchmark-only result above did
not exercise tokenizer or generation quality because it used `n_prompt=0`.

### WikiText-2 perplexity

Command family:

```bash
python turboquant/autoresearch/paper_perplexity_matrix.py \
  --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
  --dataset llama.cpp/wikitext-2-raw/wiki.test.raw \
  --threads 6 \
  --ctx-size 512 \
  --chunks 20 \
  --output-dir turboquant/results/paper_ppl/gemma4_e4b_x86_ppl20
```

| KV config | PPL | stderr |
|---|---:|---:|
| `f16/f16` | 117.9486 | 8.7215 |
| `q8_0/q8_0` | 117.4703 | 8.6774 |
| `q4_0/q4_0` | 133.7736 | 10.0038 |
| `tbq4/tbq4` | **113.8643** | 8.3380 |
| `q8_0/tbq4` | 116.7188 | 8.6032 |

Raw artifacts are in `results/paper_ppl/gemma4_e4b_x86_ppl20/`.

### Deterministic prompt set

Five fixed prompts were generated for F16, Q8, Q4, TBQ4, and hybrid
`q8_0/tbq4` using the original `smoke` prompt set in
`paper_quality_generate.py`. Local cosine similarity to the reference answers
is clustered across KV settings:

| KV config | N | Mean cosine |
|---|---:|---:|
| `f16/f16` | 5 | 0.601 |
| `q8_0/q8_0` | 5 | 0.601 |
| `q4_0/q4_0` | 5 | 0.607 |
| `tbq4/tbq4` | 5 | **0.617** |
| `q8_0/tbq4` | 5 | 0.600 |

The generated JSONL is `results/paper_quality/gemma4_e4b_generations.jsonl`.
A GPT-5.5-class chat subagent judge was run without using an API key. It found
no correctness or safety degradation for `tbq4/tbq4` or `q8_0/tbq4` versus F16;
the dominant issue was 120-token truncation across all settings. The subagent
judge summary is stored in
`results/paper_quality/gemma4_e4b_subagent_judge.md`.

A broader `paper` prompt set has been added for the next run. It covers
sentence completion, closed-book Q&A, summarization, arithmetic reasoning, a
trick puzzle, description, code, medical safety, instruction following, and
structured JSON formatting. That broader set has not yet been rerun for Gemma 4.

## What Changed

The speedup was not obtained by only trying different K/V quantization schemes.
Two implementation changes mattered:

1. Quantized KV cache types were allowed into the split-KV decode path when the
   type has a CPU vector-dot implementation and a query conversion path. Before
   this, quantized KV decode was under-parallelized at long depth.

2. TBQ4 V-cache accumulation gained an AVX2 fused path that avoids building an
   intermediate F32 dequantization buffer in the hot flash-attention loop.

3. Follow-up generation quality exposed a scoped Gemma 4 tokenizer issue: the
   Gemma 4 BPE merge table contains whitespace-bearing merge sides, but the
   generic BPE rank lookup asserted that merge sides contain no spaces or
   newlines. The local fix skips that assert only for Gemma 4, allowing
   `llama-cli` and `llama-perplexity` to run. The original `llama-bench`
   throughput table was not affected because it used `n_prompt=0`.

The final TBQ4 AVX2 V path uses the existing int8 centroid approximation also
used by the TBQ4 K-dot path. Exact float-centroid gather and higher-precision
int16-centroid shuffle variants were tested, but both were slower and did not
preserve the long-depth advantage over Q8.

## Negative Results

- `q4_0/q4_0` was measured after the first summary because it had already been
  trailing in earlier runs. The final measurement confirmed it is not
  competitive on this Gemma 4 E4B CPU setup.
- 12 threads were slower than 6 threads on this CPU for the tested decode setup.
- TBQ4 does not help at depth 0 and is effectively neutral at depth 512.
- Exact float-centroid V accumulation is cleaner semantically, but too slow on
  this AVX2 path because gathers dominate the small per-block workload.

## Caveats

These are still early quality findings. The 20-chunk WikiText-2 PPL and
five-prompt cosine checks are encouraging for this Gemma 4 E4B setup, but they
are not enough to treat symmetric `tbq4/tbq4` as a general default. The
optimized TBQ4 V path is approximate in the same style as the existing TBQ4
K-dot path, so larger quality evaluation and longer LLM-as-judge generations
remain required before publication. For quality-sensitive usage, the earlier hybrid
recommendation `q8_0/tbq4` remains worth testing per model.

## Reproduction Template

Use a local Gemma 4 E4B IT GGUF path in place of `/path/to/model.gguf`:

```bash
./llama.cpp/build/bin/llama-bench \
  -m /path/to/model.gguf \
  -t 6 \
  -p 0 \
  -n 16 \
  -d 2048,4096,8192 \
  -r 2 \
  -ctk tbq4 \
  -ctv tbq4 \
  -fa 1
```
