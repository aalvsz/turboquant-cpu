# macOS CPU Benchmark Procedure

This workspace is currently running on Ubuntu x86_64, so macOS CPU numbers must
be produced on the Mac itself or on a macOS host reachable by SSH. The runner
below executes the same Gemma 4 E4B matrix used in the current x86 report.

## Run on the Mac

From the repository root on macOS:

```bash
python3 turboquant/autoresearch/run_gemma4_cpu_benchmark_suite.py \
  --model /path/to/gemma-4-E4B-it-Q4_0.gguf \
  --threads 6 \
  --label macos_cpu
```

The run is CPU-only:

- `llama.cpp` build: `GGML_METAL=OFF`, `GGML_ACCELERATE=ON`, `GGML_NATIVE=ON`
- Speed: `n_prompt=0`, `n_gen=16`, `repetitions=2`, depths `0,512,2048,4096,8192`
- K/V configs: `f16/f16`, `q8_0/q8_0`, `q4_0/q4_0`, `tbq4/tbq4`, `q8_0/tbq4`
- PPL: WikiText-2, ctx `512`, `20` chunks
- Quality: `hard` prompt set, ctx `2048`, `n_predict=256`

Results are written under:

```text
turboquant/results/macos_cpu/
```

The suite loads the 4.5 GB GGUF repeatedly and can put pressure on a 36 GB Mac
if other large processes are resident. For lower memory risk, resume one phase
at a time with the skip flags, for example:

```bash
python3 turboquant/autoresearch/run_gemma4_cpu_benchmark_suite.py \
  --model /path/to/gemma-4-E4B-it-Q4_0.gguf \
  --threads 6 \
  --label macos_cpu \
  --skip-build \
  --skip-ppl \
  --skip-quality
```

Use `--skip-speed`, `--skip-ppl`, and `--skip-quality` to avoid rerunning
completed phases.

## ARM-Optimized Build Variant

To keep the original macOS CPU build intact while testing ARM-specific
TurboQuant kernels:

```bash
cmake -S llama.cpp -B llama.cpp/build-arm-turboquant \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_METAL=OFF \
  -DGGML_ACCELERATE=ON

cmake --build llama.cpp/build-arm-turboquant \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$(sysctl -n hw.ncpu)"
```

Use `llama.cpp/build-arm-turboquant/bin/llama-bench` for speed-only ARM
follow-up runs. Avoid rerunning PPL or quality unless the speed result changed
enough to justify the extra memory pressure.

For a low-memory tuning pass at the 8K depth:

```bash
python3 turboquant/autoresearch/paper_benchmark_matrix.py \
  --bench-bin llama.cpp/build-arm-turboquant/bin/llama-bench \
  --model gemma4_e4b=/path/to/gemma-4-E4B-it-Q4_0.gguf \
  --threads-list 6 \
  --depths 8192 \
  --n-gen 16 \
  --repetitions 3 \
  --configs f16:f16,q8_0:q8_0,q4_0:q4_0,tbq4:tbq4,q8_0:tbq4 \
  --output-dir turboquant/results/macos_cpu_arm_turboquant/t6_8k_r3
```

On the measured M4 Max, `q8_0/tbq4` was the best 8K CPU-only configuration.
An attempted TBQ4 `.nrows = 2` I8MM dispatch was numerically correct but slower
and should stay disabled unless future profiling shows a different schedule.

## Compare Against x86

After the Mac results are available in this repository:

```bash
python3 turboquant/autoresearch/compare_gemma4_cpu_hosts.py \
  --macos-root turboquant/results/macos_cpu
```

This writes:

```text
turboquant/results/macos_cpu/comparison/summary.md
turboquant/results/macos_cpu/comparison/speed_x86_vs_macos.csv
turboquant/results/macos_cpu/comparison/ppl_x86_vs_macos.csv
turboquant/results/macos_cpu/comparison/quality_task_x86_vs_macos.csv
```

## LLM Judge

The runner produces the hard-prompt generations. The GPT-5.5 chat-subagent
judge should be run from this chat after the Mac JSONL is copied back, matching
the x86 judging workflow without using an API key.
