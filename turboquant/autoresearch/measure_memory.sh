#!/bin/bash
# Measure peak memory footprint of each (model, kv_type) combination
# Uses llama-bench's built-in memory stats

set -e

WORKER=10.15.1.154
BENCH=/home/ubuntu/llama.cpp/build/bin/llama-bench
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TURBOQUANT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT="$TURBOQUANT_DIR/results/memory_$(date +%Y%m%d_%H%M%S).tsv"

declare -A MODELS
MODELS=(
    ["gilda_3.2b"]="/home/ubuntu/models/llm/reasoning_gilda_Q4KM.gguf"
    ["qwen2.5_7b"]="/home/ubuntu/models/llm/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    ["gemma2_9b"]="/home/ubuntu/models/llm/gemma-2-9b-it-Q4_K_M.gguf"
)

KV_TYPES=(f16 q8_0 q4_0 tbq4 tbq3 tbq2)

echo -e "model\tkv_type\tctx_size\tkv_cache_mb\tprocess_rss_mb" > "$OUT"

for model in "${!MODELS[@]}"; do
    path="${MODELS[$model]}"
    for kv in "${KV_TYPES[@]}"; do
        # Start llama-cli with a short prompt, let it load, measure memory
        # Use --ctx-size 8192 so we see KV cache allocations
        ssh ubuntu@$WORKER "pidof llama-cli >/dev/null && pkill -9 llama-cli; sleep 1" 2>/dev/null || true

        # Run llama-cli briefly to allocate the cache
        mem_info=$(ssh ubuntu@$WORKER "timeout 30 /home/ubuntu/llama.cpp/build/bin/llama-cli -m '$path' \
            --cache-type-k $kv --cache-type-v $kv --flash-attn on \
            -p 'hi' -n 1 -t 12 -c 8192 --single-turn --simple-io --log-disable 2>&1 \
            | grep -E 'KV self size|kv_self|context' | head -5" 2>&1 || echo "failed")

        # Get process RSS max during run
        # Simpler: re-run and capture rss at the end via /proc
        rss_mb=$(ssh ubuntu@$WORKER "timeout 60 /home/ubuntu/llama.cpp/build/bin/llama-cli -m '$path' \
            --cache-type-k $kv --cache-type-v $kv --flash-attn on \
            -p 'hi' -n 1 -t 12 -c 8192 --single-turn --simple-io --log-disable 2>&1 \
            | grep 'peak memory' | head -1 | grep -oE '[0-9]+(\.[0-9]+)?' | head -1" 2>&1 || echo "0")

        echo -e "${model}\t${kv}\t8192\t${mem_info}\t${rss_mb}" | tr '\n' ' '
        echo ""
        echo -e "${model}\t${kv}\t8192\t${mem_info}\t${rss_mb}" >> "$OUT"
    done
done

echo ""
echo "Memory results saved to: $OUT"
cat "$OUT"
