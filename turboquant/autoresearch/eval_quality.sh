#!/bin/bash
# Output quality evaluation: same prompts across all KV types
# Requires llama-cli to be deployed to Worker 2

set -e

WORKER=10.15.1.154
CLI=/home/ubuntu/llama.cpp/build/bin/llama-cli
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TURBOQUANT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$TURBOQUANT_DIR/results/quality_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT_DIR"

declare -A MODELS
MODELS=(
    ["llama3.1_8b"]="/home/ubuntu/models/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    ["qwen2.5_7b"]="/home/ubuntu/models/llm/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    ["gemma2_9b"]="/home/ubuntu/models/llm/gemma-2-9b-it-Q4_K_M.gguf"
    ["llama4_scout_17b"]="/home/ubuntu/models/llm/Llama-4-Scout-17B-16E-Instruct-Q4_K_M.gguf"
)

KV_TYPES=(f16 q8_0 q4_0 tbq4 tbq3 tbq2)

PROMPTS=(
    "The capital of France is"
    "Explain photosynthesis in one paragraph."
    "Write a Python function to compute the nth Fibonacci number."
    "What are the main symptoms of a stroke?"
    "Describe the structure of a haiku with an example."
)

for model in "${!MODELS[@]}"; do
    path="${MODELS[$model]}"
    # Skip missing models (e.g., if Scout download failed)
    if ! ssh ubuntu@$WORKER "test -f '$path'" 2>/dev/null; then
        echo "[$model] SKIP - model file not found on worker"
        continue
    fi
    for kv in "${KV_TYPES[@]}"; do
        out="$OUT_DIR/${model}_${kv}.txt"
        # Skip if already done (has trailing output)
        if [ -f "$out" ] && grep -q "Prompt 5" "$out" 2>/dev/null; then
            echo "[$model × $kv] SKIP - already done"
            continue
        fi
        echo "=== $model × $kv ===" > "$out"
        for i in "${!PROMPTS[@]}"; do
            prompt="${PROMPTS[$i]}"
            echo "### Prompt $((i+1)): $prompt" >> "$out"
            ssh ubuntu@$WORKER "$CLI -m '$path' --cache-type-k $kv --cache-type-v $kv --flash-attn on -p '$prompt' -n 120 -t 12 -c 1024 --temp 0 --top-k 1 --single-turn --simple-io --log-disable --no-display-prompt 2>/dev/null" >> "$out" 2>&1 || echo "[FAILED]" >> "$out"
            echo "" >> "$out"
        done
        echo "[$model × $kv] done"
    done
done

echo "=== Quality eval done. Results in $OUT_DIR ==="
