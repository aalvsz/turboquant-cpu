# ARM CPU Replication Plan

The ARM run should replicate the exact x86 paper matrix, changing only hardware
and build target. Keep GPU/Metal off unless the section is explicitly about
accelerated ARM systems.

## Hardware Metadata

Capture one metadata file before running benchmarks:

```bash
uname -a > arm_host_metadata.txt
lscpu >> arm_host_metadata.txt 2>/dev/null || true
sysctl -a | grep -E 'machdep.cpu|hw.optional|hw.perflevel|hw.memsize' >> arm_host_metadata.txt 2>/dev/null || true
```

Record:

- CPU model and core layout
- memory capacity and bandwidth if known
- OS and kernel version
- compiler version
- whether the run is Linux ARM, Apple Silicon CPU-only, or another ARM target

## CPU-Only Build

Linux ARM:

```bash
cmake -S llama.cpp -B llama.cpp/build-arm-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_METAL=OFF \
  -DGGML_CUDA=OFF

cmake --build llama.cpp/build-arm-cpu \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$(nproc)"
```

Apple Silicon CPU-only:

```bash
cmake -S llama.cpp -B llama.cpp/build-arm-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_METAL=OFF \
  -DGGML_ACCELERATE=ON

cmake --build llama.cpp/build-arm-cpu \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$(sysctl -n hw.ncpu)"
```

## Benchmark Matrix

Use the same configs and depths as x86:

```bash
python turboquant/autoresearch/paper_benchmark_matrix.py \
  --bench-bin llama.cpp/build-arm-cpu/bin/llama-bench \
  --model gemma4_e4b=/path/to/gemma-4-E4B-it-Q4_0.gguf \
  --threads-list 4,6,8 \
  --depths 0,512,2048,4096,8192 \
  --n-gen 128 \
  --repetitions 10 \
  --output-dir turboquant/results/paper_bench/gemma4_e4b_arm_cpu
```

Adjust `--threads-list` to the physical performance-core counts of the ARM
machine. Report efficiency by thread count rather than choosing only the best
number.

## Quality and Judge

Use the same generated prompts and GPT-5.5 judge rubric as x86:

```bash
python turboquant/autoresearch/paper_quality_generate.py \
  --llama-cli llama.cpp/build-arm-cpu/bin/llama-cli \
  --model gemma4_e4b=/path/to/gemma-4-E4B-it-Q4_0.gguf \
  --threads 6 \
  --output turboquant/results/paper_quality/gemma4_e4b_arm_generations.jsonl

OPENAI_API_KEY=... OPENAI_JUDGE_MODEL=gpt-5.5 \
python turboquant/autoresearch/llm_judge_quality.py \
  --jsonl turboquant/results/paper_quality/gemma4_e4b_arm_generations.jsonl \
  --output turboquant/results/paper_quality/gemma4_e4b_arm_llm_judgments.jsonl \
  --summary turboquant/results/paper_quality/gemma4_e4b_arm_llm_judge_summary.csv
```

## ARM-Specific Questions

The ARM section should answer:

- Does TBQ4 stay faster than Q8/Q4 at long KV depth?
- Is the fused V path still the winning implementation without AVX2 shuffles?
- Does thread oversubscription appear earlier on heterogeneous cores?
- Does `q8_0/tbq4` remain the safest quality recommendation?
- Are NEON/SVE implementations needed for parity with the x86 AVX2 path?
