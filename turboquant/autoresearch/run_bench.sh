#!/bin/bash
# Benchmark runner that ensures exclusive CPU access
# Usage: ./run_bench.sh <kv_type> <depth> [n] [r]
# Returns: raw t/s value

set -e

KV=${1:-tbq3}
DEPTH=${2:-2048}
N=${3:-32}
R=${4:-2}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LLAMA_CPP_DIR="${LLAMA_CPP_DIR:-$REPO_ROOT/llama.cpp}"
REMOTE_LLAMA_CPP_DIR="${REMOTE_LLAMA_CPP_DIR:-$LLAMA_CPP_DIR}"
MODEL_DIR="${MODEL_DIR:-$HOME/models/llm}"
WORKER_HOST="${WORKER_HOST:-10.15.1.154}"
WORKER_USER="${WORKER_USER:-}"
WORKER="${WORKER_USER:+$WORKER_USER@}$WORKER_HOST"
BENCH="${BENCH:-$REMOTE_LLAMA_CPP_DIR/build/bin/llama-bench}"
MODEL="${MODEL:-$MODEL_DIR/reasoning_gilda_Q4KM.gguf}"

# Wait for any running llama-bench to finish (max 10 min)
for i in {1..120}; do
  if ! ssh "$WORKER" "pgrep -f llama-bench >/dev/null 2>&1"; then
    break
  fi
  sleep 5
done

# Run benchmark and extract t/s value
ssh "$WORKER" "'$BENCH' -m '$MODEL' -ctk $KV -ctv $KV -t 12 -p 0 -n $N -r $R -fa 1 -d $DEPTH 2>&1" \
  | grep -oP '\d+\.\d+(?= ±)' | head -1
