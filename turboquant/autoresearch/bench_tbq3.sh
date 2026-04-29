#!/bin/bash
# Fast TBQ3 benchmark for autoresearch loop
# Tests at d=2048 (2 min) for rapid iteration
set -e

WORKER=10.15.1.154
BENCH=/home/ubuntu/llama.cpp/build/bin/llama-bench
MODEL=/home/ubuntu/models/llm/reasoning_gilda_Q4KM.gguf

# Ensure no competing processes
ssh ubuntu@$WORKER "pgrep -f llama-bench >/dev/null && exit 1 || true" 2>/dev/null

# Remove old binary and deploy new one
ssh ubuntu@$WORKER "rm -f $BENCH" 2>/dev/null
scp /home/ubuntu/llama.cpp/build/bin/llama-bench ubuntu@$WORKER:$BENCH >/dev/null 2>&1

# Run at d=2048 (faster iteration)
DEPTH=${1:-2048}
TYPE=${2:-tbq3}

ssh ubuntu@$WORKER "$BENCH -m $MODEL -ctk $TYPE -ctv $TYPE -t 12 -p 0 -n 32 -r 2 -fa 1 -d $DEPTH 2>&1" | grep -oP '\d+\.\d+ ± \d+\.\d+' | head -1
