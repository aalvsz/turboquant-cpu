# x86 Qwen3.5 Agent Fix

## Diagnosis

The failed x86 agent run used:

```text
/home/ubuntu/dev/repos/turboquant-cpu/llama.cpp/build/bin/llama-server
version: 3 (fd44c01)
```

The valid M4 agent run used:

```text
benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-qualityfix/bin/llama-server
version: 7 (90b03b6)
```

The rebuilt x86 quality-fix server currently reports:

```text
benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-x86-qwen35-tbq4-qualityfix/bin/llama-server
version: 6 (ef7047a)
```

The older x86 server loads the Qwen3.5 GGUF but follows the broken Qwen3.5
graph path previously documented in
`benchmark_results/fresh_edge_agentic_20260501/qwen_quality_fix/QWEN_QUALITY_FIX_REPORT.md`.
The symptom is repetitive natural language such as `The user's message is...`
instead of the requested JSON.

## Required x86 rebuild

Build x86 from the Qwen3.5 quality-fix source tree, not from the older root
`llama.cpp/build` tree:

```bash
cd /home/ubuntu/dev/repos/turboquant-cpu

cmake -S benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp \
  -B benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-x86-qwen35-tbq4-qualityfix \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_CUDA=OFF

cmake --build benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-x86-qwen35-tbq4-qualityfix \
  --target llama-server llama-cli llama-bench llama-perplexity \
  -j "$(nproc)"

benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-x86-qwen35-tbq4-qualityfix/bin/llama-server --version
```

The version must be at least `6`, and it must come from the
`qwen35-tbq4-qualityfix` source tree. The agent harness now refuses Qwen runs
with older server versions unless `--allow-legacy-qwen-server` is passed
explicitly for diagnosis.

## Model sanity check

The local known-good Qwen model hash is:

```text
298fcb5fe7a77ccc79745ae24751560c5ac56874caff4bb39b1f2055bd72b8bb  Qwen3.5-4B-Q4_0.gguf
```

Check the x86 copy before rerunning:

```bash
sha256sum /home/ubuntu/models/Qwen3.5-4B-Q4_0.gguf
```

## Smoke run

After rebuilding, run a Qwen-only smoke test before the full matrix:

```bash
python3 agent/run_agent_benchmark.py \
  --server-bin benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-x86-qwen35-tbq4-qualityfix/bin/llama-server \
  --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
  --model qwen35_4b=/home/ubuntu/models/Qwen3.5-4B-Q4_0.gguf \
  --models qwen35_4b \
  --kv-configs q4,tbq4,q8_0_tbq4 \
  --host-label x86_axelera_qwen_fix \
  --threads 6 \
  --threads-batch 6 \
  --ctx-size 8192 \
  --task-suite core \
  --limit-tasks 2 \
  --planner-mode llm \
  --telemetry
```

Expected acceptance criterion: `final_json_valid_rate=1.0` in every Qwen smoke
summary row, with no repetitive `The user's message is...` outputs in
`tasks.csv`.
