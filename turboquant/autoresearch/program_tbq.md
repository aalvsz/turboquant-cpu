# TurboQuant Autonomous Research

Adapted from karpathy/autoresearch for TBQ KV cache kernel optimization on CPU.

## Setup

1. **Run tag**: `tbq-apr12`
2. **Branch**: Work directly on the current worktree
3. **Code to modify**: TBQ SIMD kernels in llama.cpp:
   - `$LLAMA_CPP_DIR/ggml/src/ggml-cpu/quants.c` — vec_mad_{tbq2,tbq3,tbq4}, quantize_row_{tbq2,tbq3,tbq4}
   - `$LLAMA_CPP_DIR/ggml/src/ggml-cpu/arch/x86/quants.c` — vec_dot_{tbq2,tbq3,tbq4}_q8_0
   - `$LLAMA_CPP_DIR/ggml/src/ggml-turboquant.h` — centroid tables, block structs
4. **Build command**: `cmake --build "$LLAMA_CPP_DIR/build" -j$(nproc)`
5. **Deploy**: `scp "$LLAMA_CPP_DIR/build/bin/llama-bench" "$WORKER:$REMOTE_LLAMA_CPP_DIR/build/bin/"`
6. **Worker**: configurable via `WORKER`, `WORKER_HOST`, and `WORKER_USER` (tested on Intel i5-12500, 12 threads, AVX2 + AVXVNNI, 32GB DDR5)

## The Goal

Make TBQ2 faster than TBQ3, TBQ3 faster than TBQ4, TBQ4 faster than F16 at d=8192.
This is the natural order since TBQ2 < TBQ3 < TBQ4 < F16 in memory footprint.

Current status (d=8192, tg32, Gilda 3.2B):
- F16:  7.53 t/s (baseline)
- TBQ4: 10.31 t/s (+37% — good, bandwidth wins)
- TBQ3:  3.69 t/s (-51% — BAD, compute-bound in vec_mad)
- TBQ2:  4.55 t/s (-40% — BAD, compute-bound in vec_mad)

Target: TBQ2 > TBQ3 > TBQ4 > 10 t/s at d=8192.

## Why TBQ3/TBQ2 Are Slow

The bottleneck is `vec_mad` (V accumulation in tiled flash attention). At d=8192,
vec_mad is called 8192 times per token per head. Instruction counts per 32-value block:

- **TBQ4 vec_mad**: ~22 SIMD instructions (nibble split + vpshufb LUT + FMA)
- **TBQ3 vec_mad**: ~54 SIMD instructions (ql/qh split: 4 shifts + 3 blends + broadcast + AND + cmpeq + combine + vpshufb + cvt + FMA)
- **TBQ2 vec_mad**: ~36 SIMD instructions (shift/mask + blend + vpshufb + cvt + FMA)

TBQ3 has 2.5x more instructions than TBQ4 but only reads 25% less data (12B vs 16B per block).

## Optimization Strategies to Try

### For vec_mad_tbq3:
1. **Avoid cvtepi8_epi32**: Currently converts i8 centroids → i32 → f32 (8 values at a time).
   Instead, use FP16 centroids in a 256-bit register and vpshufb directly in FP16.
2. **Eliminate the blend chain**: The 4-shift + 3-blend ql expansion is 7 ops.
   Try: load 4 bytes, use _mm_multishift_epi64_epi8 (if available) or a LUT-based approach.
3. **Combine ql+qh into a single lookup**: Pre-combine the 2-bit ql and 1-bit qh into
   a 3-bit index using fewer instructions.
4. **Process 32 values without the half loop**: Currently loops half=0,1 processing
   16 values each. Try processing all 32 at once using 256-bit registers.
5. **Use float centroid LUT**: Instead of i8 centroid + cvt, precompute 8 float centroids
   × scale, use _mm256_permutevar_ps or gather.
6. **Register-tiled accumulation**: Keep VKQ32 in registers across multiple vec_mad calls
   to reduce load/store.

### For vec_mad_tbq2:
1. **Same cvtepi8 elimination**: Use float LUT approach.
2. **Simpler 2-bit unpacking**: Only 4 centroids — try _mm256_permutevar8x32_ps with
   32-bit index packing.
3. **Remove dead code**: Lines 446-451 have unused _mm_srlv_epi32 code.

### For vec_mad_tbq4:
1. **Already fast**, but try: process 64 values per iteration (2 blocks).
2. **Avoid cvtepi8_epi32**: Use f16 centroid vector + vpshufb.

### For vec_dot:
1. **Ensure AVXVNNI DPBUSD is used for tbq3/tbq2** (currently only tbq4 uses it).

## Benchmark Command

Quick sanity (each config ~10-30s):
```bash
ssh "$WORKER" "$REMOTE_LLAMA_CPP_DIR/build/bin/llama-bench \
  -m $MODEL_DIR/reasoning_gilda_Q4KM.gguf \
  -ctk tbq3 -ctv tbq3 -t 12 -p 0 -n 32 -r 1 -fa 1 -d 8192"
```

Full comparison (matching types only):
```bash
for kv in f16 tbq4 tbq3 tbq2; do
  ssh "$WORKER" "$REMOTE_LLAMA_CPP_DIR/build/bin/llama-bench \
    -m $MODEL_DIR/reasoning_gilda_Q4KM.gguf \
    -ctk $kv -ctv $kv -t 12 -p 0 -n 32 -r 2 -fa 1 -d 8192" | grep tg
done
```

## Models for Final Evaluation

After optimization, run the full comparison on:
1. Gilda 3.2B (Llama family): `$MODEL_DIR/reasoning_gilda_Q4KM.gguf`
2. Qwen2.5 7B (Qwen family): `$MODEL_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf`
3. Gemma 2 9B (Gemma family): `$MODEL_DIR/gemma-2-9b-it-Q4_K_M.gguf`

KV types to compare: f16, q8_0, q4_0, tbq4, tbq3, tbq2
Depths: 0, 2048, 4096, 8192
Metrics: pp512 (t/s), tg128 (t/s), peak memory

## Experiment Loop

LOOP FOREVER:

1. Read the current vec_mad code for the target TBQ type
2. Identify the bottleneck (instruction count, data movement, dependency chain)
3. Implement an optimization idea
4. Build: `cmake --build "$LLAMA_CPP_DIR/build" -j$(nproc) 2>&1 | tail -3`
5. Deploy: `scp "$LLAMA_CPP_DIR/build/bin/llama-bench" "$WORKER:$REMOTE_LLAMA_CPP_DIR/build/bin/"`
6. Benchmark TBQ3 at d=8192: `ssh "$WORKER" "llama-bench ... -ctk tbq3 -ctv tbq3 -d 8192"`
7. Record result in results.tsv
8. If faster → keep the change (git commit)
9. If slower or same → revert (git checkout -- file)
10. Move to next optimization idea

**NEVER STOP. The human may be sleeping. Keep iterating.**

## Results Format (results.tsv)

```
experiment	tbq2_d8192	tbq3_d8192	tbq4_d8192	f16_d8192	status	description
baseline	4.55	3.69	10.31	7.53	keep	current state
```
