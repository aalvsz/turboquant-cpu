# TurboQuant Agent Benchmark

This folder contains an edge-agent benchmark for comparing KV-cache formats with
the same Gemma 4 and Qwen3.5 4B GGUF models used in the CPU benchmark matrix.

The benchmark has two layers:

- `turboquant_agent/adk_agent.py` exposes an ADK `LlmAgent` with a shared tool
  catalog. Use this with `adk run` or `adk web` when Google ADK and LiteLLM are
  installed.
- `run_agent_benchmark.py` is the measured runner. It launches local
  `llama-server` instances, runs the same agent/tool pipeline for each KV
  setting, records raw events, and writes CSV/Markdown reports.

The measured runner intentionally has no Python package dependency. It uses the
OpenAI-compatible endpoint exposed by `llama-server` and a JSON tool-planning
protocol so that the local GGUF models can be compared consistently.

## KV Configurations

The default matrix matches the previous benchmark:

- `f16/f16`
- `q8_0/q8_0`
- `q4_0/q4_0`
- `tbq4/tbq4`
- `q8_0/tbq4`

## Quick Run

```bash
python3 agent/run_agent_benchmark.py \
  --host-label m4_max \
  --threads 10 \
  --ctx-size 8192
```

Results are written under `agent/results/<run_id>/`.

Full M4 run used for the checked-in result:

```bash
python3 agent/run_agent_benchmark.py \
  --host-label m4_max \
  --models gemma4_e4b,qwen35_4b \
  --kv-configs all \
  --threads 10 \
  --threads-batch 10 \
  --ctx-size 8192 \
  --server-timeout 240 \
  --min-memory-free-pct 15
```

Raspberry Pi follow-up should use the same command with a Pi-specific host label
and a conservative thread count for the device:

```bash
python3 agent/run_agent_benchmark.py \
  --host-label raspberry_pi \
  --models gemma4_e4b,qwen35_4b \
  --kv-configs all \
  --threads 4 \
  --threads-batch 4 \
  --ctx-size 8192 \
  --server-timeout 600 \
  --min-memory-free-pct 20
```

## Optional ADK Setup

```bash
python3.12 -m venv agent/.venv
source agent/.venv/bin/activate
pip install -r agent/requirements.txt
export OPENAI_API_BASE=http://127.0.0.1:18100/v1
export OPENAI_API_KEY=local
adk run agent/turboquant_agent
```

The ADK path expects a compatible local model endpoint to already be running.
