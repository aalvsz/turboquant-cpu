#!/bin/bash
# Fast TBQ3 benchmark for autoresearch loop
# Tests at d=2048 (2 min) for rapid iteration
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LLAMA_CPP_DIR="${LLAMA_CPP_DIR:-$REPO_ROOT/llama.cpp}"
REMOTE_LLAMA_CPP_DIR="${REMOTE_LLAMA_CPP_DIR:-$LLAMA_CPP_DIR}"
MODEL_DIR="${MODEL_DIR:-$HOME/models/llm}"
WORKER_HOST="${WORKER_HOST:-10.15.1.154}"
WORKER_USER="${WORKER_USER:-}"
WORKER="${WORKER_USER:+$WORKER_USER@}$WORKER_HOST"
BENCH="${BENCH:-$REMOTE_LLAMA_CPP_DIR/build/bin/llama-bench}"
LOCAL_BENCH="${LOCAL_BENCH:-$LLAMA_CPP_DIR/build/bin/llama-bench}"
MODEL="${MODEL:-$MODEL_DIR/reasoning_gilda_Q4KM.gguf}"

# Ensure no competing processes
ssh "$WORKER" "pgrep -f llama-bench >/dev/null && exit 1 || true" 2>/dev/null

# Remove old binary and deploy new one
ssh "$WORKER" "rm -f '$BENCH'" 2>/dev/null
scp "$LOCAL_BENCH" "$WORKER:$BENCH" >/dev/null 2>&1

# Run at d=2048 (faster iteration)
DEPTH=${1:-2048}
TYPE=${2:-tbq3}

ssh "$WORKER" "'$BENCH' -m '$MODEL' -ctk $TYPE -ctv $TYPE -t 12 -p 0 -n 32 -r 2 -fa 1 -d $DEPTH 2>&1" | grep -oP '\d+\.\d+ ± \d+\.\d+' | head -1
