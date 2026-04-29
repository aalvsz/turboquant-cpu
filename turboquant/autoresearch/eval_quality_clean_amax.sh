#!/bin/bash
set -u
MODEL_DIR="${MODEL_DIR:-$HOME/models/llm}"
LDIR="${LDIR:-$HOME/llama_amax_clean/bin}"
OUT="${OUT:-$HOME/turboquant_runs/quality_clean_amax_20260427}"
mkdir -p "$OUT"
NAMES=(llama3.1_8b qwen2.5_7b gemma2_9b)
PATHS=(
    "$MODEL_DIR/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    "$MODEL_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    "$MODEL_DIR/gemma-2-9b-it-Q4_K_M.gguf"
)
CFG=(
    "f16 f16 f16"
    "q8_0 q8_0 q8_0"
    "q4_0 q4_0 q4_0"
    "tbq4 tbq4 tbq4"
    "q8_0 tbq4 q8_0_tbq4"
)
PROMPTS=(
    "The capital of France is"
    "Explain photosynthesis in one paragraph."
    "Write a Python function to compute the nth Fibonacci number."
    "What are the main symptoms of a stroke?"
    "Describe the structure of a haiku with an example."
)
for i in 0 1 2; do
    name=${NAMES[$i]}; M=${PATHS[$i]}
    for c in "${CFG[@]}"; do
        set -- $c; K=$1; V=$2; TAG=$3
        OUTF="$OUT/${name}_${TAG}.txt"
        if [ -f "$OUTF" ] && grep -q "Prompt 5" "$OUTF" 2>/dev/null && awk '/^### Prompt 5/{p=1} p && /\[ Prompt:/{f=1; exit} END{exit !f}' "$OUTF"; then
            echo "[$name $TAG] skip"; continue
        fi
        echo "=== $name K=$K V=$V (CLEAN + AMAX) ===" > "$OUTF"
        for p in 0 1 2 3 4; do
            prompt="${PROMPTS[$p]}"
            echo "### Prompt $((p+1)): $prompt" >> "$OUTF"
            LD_LIBRARY_PATH=$LDIR "$LDIR/llama-cli" -m "$M" --cache-type-k $K --cache-type-v $V --flash-attn on -p "$prompt" -n 120 -t 12 -c 1024 --temp 0 --top-k 1 --single-turn --simple-io --log-disable --no-display-prompt 2>/dev/null >> "$OUTF" 2>&1 || echo "[FAILED]" >> "$OUTF"
            echo "" >> "$OUTF"
        done
        echo "[$name $TAG] done"
    done
done
echo "=== ALL DONE ==="
