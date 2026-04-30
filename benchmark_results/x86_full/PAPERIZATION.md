# TurboQuant CPU Paperization Plan

This document turns the local findings into a publishable systems-paper
artifact plan. The core claim should stay narrow:

> TurboQuant KV cache compression can improve long-context CPU decode when the
> implementation is fused into the hot attention path, but the safe deployment
> regime is model-dependent. Symmetric `tbq4/tbq4` is compelling on Gemma-family
> cases, while hybrid `q8_0/tbq4` is the stronger general recommendation.

## Required Additions

### 1. Robust Speed Matrix

Use longer generations, more repetitions, multiple thread counts, and raw CSV
artifacts. The current Gemma 4 note used `n_gen=16` and `r=2`; paper results
should use at least `n_gen=128` and `r=10`.

```bash
python turboquant/autoresearch/paper_benchmark_matrix.py \
  --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
  --threads-list 6,12 \
  --depths 0,512,2048,4096,8192 \
  --n-gen 128 \
  --repetitions 10 \
  --output-dir turboquant/results/paper_bench/gemma4_e4b_x86
```

For the full paper, repeat with the older Llama, Qwen, and Gemma 2 models when
their GGUF files are available locally.

### 2. Perplexity / Quality Validation

Perplexity is required before making any symmetric `tbq4/tbq4` quality claim.

```bash
cd llama.cpp
./scripts/get-wikitext-2.sh
cd ..

python turboquant/autoresearch/paper_perplexity_matrix.py \
  --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
  --dataset llama.cpp/wikitext-2-raw/wiki.test.raw \
  --threads 6 \
  --ctx-size 512 \
  --chunks 20 \
  --output-dir turboquant/results/paper_ppl/gemma4_e4b_x86
```

### 3. Deterministic Generation Quality Set

Generate fixed-prompt outputs for later cosine and LLM-as-judge scoring.

```bash
python turboquant/autoresearch/paper_quality_generate.py \
  --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
  --prompt-set paper \
  --threads 6 \
  --ctx-size 1024 \
  --n-predict 256 \
  --output turboquant/results/paper_quality/gemma4_e4b_generations.jsonl
```

The `paper` prompt set covers sentence completion, closed-book Q&A,
summarization, arithmetic reasoning, a trick puzzle, description, code,
medical safety, instruction following, and structured JSON formatting. The
older default `smoke` prompt set is retained for quick local checks.

### 4. LLM-as-Judge Quality

Use a GPT-5.5-class chat subagent as the primary judge. Do not require an
OpenAI API key for this workflow. Give the subagent this task:

```
Read turboquant/results/paper_quality/gemma4_e4b_generations.jsonl.
Judge each output against its prompt and reference. Use F16/f16 for the same
prompt as the model baseline when comparing quantized outputs. Score
correctness, completeness, coherence, and safety from 0-5, mark degenerate
outputs, then summarize means by KV setting and call out degradation versus F16.
```

Record the judge result as a Markdown artifact next to the JSONL generations.
`autoresearch/llm_judge_quality.py` remains available for future automated
structured judging, but the current paper workflow should use the chat subagent
unless there is an explicit reason to run an external API.

### 5. Ablations

The paper needs separate measurements for:

- baseline F16 split-KV path
- uniform `q8_0/q8_0` and `q4_0/q4_0`
- symmetric `tbq4/tbq4`
- hybrid `q8_0/tbq4`
- split-KV enablement for quantized KV
- fused TBQ4 V accumulation vs intermediate F32 dequantization
- int8 centroid approximation vs exact float-centroid accumulation
- thread-count sensitivity, especially 6 vs 12 on i5-12500

### 6. Artifact Checklist

Each paper result directory should contain:

- `metadata.json`
- raw stdout/stderr for every run
- normalized CSV summary
- exact command lines
- `git rev-parse HEAD`
- `git diff --stat`
- `lscpu` or equivalent CPU metadata
- model filenames and SHA256 hashes
- dataset filename and SHA256 hash

## Paper Structure

1. Introduction: KV cache bottlenecks on CPU long-context decode.
2. Background: TurboQuant, uniform KV quantization, and split-KV attention.
3. Implementation: llama.cpp TBQ types, vector dot, split-KV support, fused V path.
4. Methodology: models, CPU, commands, repetitions, depths, thread counts.
5. Results: speed, perplexity, LLM judge, memory, ablations.
6. Negative results: shallow context, Qwen symmetric failure, thread oversubscription.
7. Deployment guidance: symmetric TBQ4 only after validation; `q8_0/tbq4` as default.
8. ARM replication: same matrix on ARM CPU, not Metal/GPU.

## Claims To Avoid

- Do not claim symmetric TBQ4 is universally safe.
- Do not claim quality neutrality from throughput data.
- Do not compare only against F16; Q8 and Q4 are required baselines.
- Do not mix dirty-tree quality outputs with clean-tree speed results.
