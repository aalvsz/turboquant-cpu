#!/usr/bin/env python3
"""Compute theoretical KV cache memory footprint for each (model, kv_type).

Prints a table of KV cache memory at ctx=8192.
"""

# Model configs: (n_layers, n_kv_heads, d_k)
MODEL_CONFIGS = {
    "llama3.1_8b": (32, 8, 128),    # Standard Llama 3.1
    "qwen2.5_7b": (28, 4, 128),     # GQA 7:4
    "gemma2_9b": (42, 8, 256),      # 8 KV heads, d_k=256
    "llama4_scout_17b": (48, 8, 128),  # Llama 4 Scout MoE (16 experts, 17B active)
}

# Bytes per value for each KV type
KV_BYTES = {
    "f16":  2.0,
    "q8_0": 1.0625,    # 1 byte + 0.0625 (2B scale / 32 values)
    "q4_0": 0.5625,    # 0.5 byte + 0.0625
    "tbq4": 0.5625,    # same as Q4_0
    "tbq3": 0.4375,    # 0.375 + 0.0625 (14 B / 32 values)
    "tbq2": 0.3125,    # 0.25 + 0.0625 (10 B / 32 values)
}

CTX_SIZE = 8192

def kv_memory_mb(n_layers, n_kv_heads, d_k, kv_type):
    bytes_per_val = KV_BYTES[kv_type]
    # K cache + V cache, both shape (ctx, n_kv_heads, d_k)
    total_bytes = 2 * CTX_SIZE * n_layers * n_kv_heads * d_k * bytes_per_val
    return total_bytes / (1024 * 1024)


def main():
    print(f"## KV Cache Memory Footprint at ctx={CTX_SIZE}\n")

    header = "| Model | " + " | ".join(KV_BYTES.keys()) + " |"
    sep = "|---|" + "|".join("---:" for _ in KV_BYTES) + "|"
    print(header)
    print(sep)

    for model, (nL, nH, dk) in MODEL_CONFIGS.items():
        cells = []
        for kv in KV_BYTES.keys():
            mb = kv_memory_mb(nL, nH, dk, kv)
            cells.append(f"{mb:.0f}")
        print(f"| {model} (L={nL}, H={nH}, dk={dk}) | " + " | ".join(cells) + " |")

    print()
    print("All values in MB. K cache + V cache combined.")
    print()

    # Reduction ratios
    print(f"\n## Memory Reduction vs F16 (ratio)\n")
    header = "| KV Type | Bytes/value | Reduction |"
    print(header)
    print("|---|---:|---:|")
    for kv, bpv in KV_BYTES.items():
        ratio = 2.0 / bpv
        print(f"| {kv} | {bpv:.4f} | {ratio:.2f}× |")


if __name__ == "__main__":
    main()
