#!/bin/bash
# Patched-quality eval: same prompts, same models, all KV configs, but using
# the amax-norm tbq_norm patch. Symmetric tbq4 should now produce sane text on Qwen.

set -e

MODEL_DIR="${MODEL_DIR:-$HOME/models/llm}"
WORKER_HOST="${WORKER_HOST:-10.15.1.154}"
WORKER_USER="${WORKER_USER:-}"
WORKER="${WORKER_USER:+$WORKER_USER@}$WORKER_HOST"
LDIR="${LDIR:-$HOME/llama_patched/bin}"
OUT_DIR="${OUT_DIR:-$HOME/turboquant_runs/quality_patched_amax_$(date +%Y%m%d_%H%M%S)}"
ssh "$WORKER" "mkdir -p '$OUT_DIR'"
echo "Worker out dir: $OUT_DIR"

declare -A MODELS
MODELS=(
    ["llama3.1_8b"]="$MODEL_DIR/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    ["qwen2.5_7b"]="$MODEL_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    ["gemma2_9b"]="$MODEL_DIR/gemma-2-9b-it-Q4_K_M.gguf"
)

# Configs: K V
declare -a CONFIGS=(
    "f16:f16"
    "q8_0:q8_0"
    "q4_0:q4_0"
    "tbq4:tbq4"
    "q8_0:tbq4"
)

PROMPTS=(
    "The capital of France is"
    "Explain photosynthesis in one paragraph."
    "Write a Python function to compute the nth Fibonacci number."
    "What are the main symptoms of a stroke?"
    "Describe the structure of a haiku with an example."
)

for model in "${!MODELS[@]}"; do
    path="${MODELS[$model]}"
    for cfg in "${CONFIGS[@]}"; do
        K="${cfg%%:*}"
        V="${cfg##*:}"
        out="$OUT_DIR/${model}_K${K}_V${V}.txt"
        ssh "$WORKER" "test -f '$out' && grep -q 'Prompt 5' '$out' 2>/dev/null" && {
            echo "[$model K=$K V=$V] SKIP - already done"; continue;
        }
        echo "=== $model × K=$K V=$V (PATCHED) ===" | ssh "$WORKER" "cat > '$out'"
        for i in "${!PROMPTS[@]}"; do
            prompt="${PROMPTS[$i]}"
            ssh "$WORKER" "echo '### Prompt $((i+1)): $prompt' >> '$out'"
            ssh "$WORKER" "while pidof -x llama-bench >/dev/null 2>&1; do sleep 5; done; LD_LIBRARY_PATH='$LDIR' '$LDIR/llama-cli' -m '$path' --cache-type-k $K --cache-type-v $V --flash-attn on -p '$prompt' -n 120 -t 12 -c 1024 --temp 0 --top-k 1 --single-turn --simple-io --log-disable --no-display-prompt 2>/dev/null >> '$out' 2>&1 || echo '[FAILED]' >> '$out'"
            ssh "$WORKER" "echo '' >> '$out'"
        done
        echo "[$model K=$K V=$V] done"
    done
done

echo "=== ALL DONE. Worker dir: $OUT_DIR ==="
