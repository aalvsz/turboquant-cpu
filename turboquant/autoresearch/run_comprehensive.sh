#!/bin/bash
# Comprehensive TurboQuant comparison benchmark
# 3 models × 6 KV types × 3 depths

set -e

WORKER=10.15.1.154
BENCH=/home/ubuntu/llama.cpp/build/bin/llama-bench
# Allow resuming an existing dir via env var
RDIR=${RDIR:-/home/ubuntu/dev/repos/chameleon-system-black/docs/turboquant/results/comprehensive_$(date +%Y%m%d_%H%M%S)}
mkdir -p "$RDIR"

echo "Results dir: $RDIR"

# Models: native Llama 3.1, Qwen 2.5, Gemma 2, Llama 4 Scout (MoE)
declare -A MODELS
MODELS=(
    ["llama3.1_8b"]="/home/ubuntu/models/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    ["qwen2.5_7b"]="/home/ubuntu/models/llm/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    ["gemma2_9b"]="/home/ubuntu/models/llm/gemma-2-9b-it-Q4_K_M.gguf"
    ["llama4_scout_17b"]="/home/ubuntu/models/llm/Q4_K_M/Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00001-of-00002.gguf"
)

KV_TYPES=(f16 q8_0 q4_0 tbq4 tbq3 tbq2)
DEPTHS=(0 2048 4096 8192)

# Ensure no other benchmarks are running
ssh ubuntu@$WORKER "pkill -f '/home/ubuntu/llama.cpp/build/bin/llama-bench' 2>/dev/null; sleep 2" || true

for model in "${!MODELS[@]}"; do
    path="${MODELS[$model]}"
    echo "========================="
    echo "Model: $model"
    echo "========================="

    # Skip if model file not available
    if ! ssh ubuntu@$WORKER "test -f '$path'" 2>/dev/null; then
        echo "  [skip - model file not found on worker]"
        continue
    fi

    for kv in "${KV_TYPES[@]}"; do
        echo "--- $model × $kv ---"
        out="$RDIR/${model}_${kv}.txt"

        # Skip if already done (file has "build:" line at the end)
        if [ -f "$out" ] && grep -q "^build:" "$out" 2>/dev/null; then
            echo "  [skip - already complete]"
            continue
        fi

        # Build depth list
        depths_str=$(IFS=,; echo "${DEPTHS[*]}")

        # Wait for any running llama-bench process (pidof avoids matching grep/pgrep itself)
        ssh ubuntu@$WORKER "while pidof -x llama-bench >/dev/null 2>&1; do sleep 5; done" 2>/dev/null

        # tg128 only (pp is secondary) - much faster
        ssh ubuntu@$WORKER "$BENCH -m '$path' -ctk $kv -ctv $kv -t 12 -p 0 -n 128 -r 2 -fa 1 -d $depths_str 2>&1" > "$out"
        grep -E "tg|pp" "$out" | head
    done
done

echo "=== ALL DONE. Results in $RDIR ==="
