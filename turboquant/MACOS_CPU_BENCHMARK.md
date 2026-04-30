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
