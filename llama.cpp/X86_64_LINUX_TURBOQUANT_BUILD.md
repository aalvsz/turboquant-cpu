# x86_64 Linux TurboQuant llama.cpp Build

## Artifact

Build directory:

```bash
llama.cpp/build-x86_64-linux-turboquant
```

Key binaries:

```bash
llama.cpp/build-x86_64-linux-turboquant/bin/llama-bench
llama.cpp/build-x86_64-linux-turboquant/bin/llama-cli
llama.cpp/build-x86_64-linux-turboquant/bin/llama-perplexity
llama.cpp/build-x86_64-linux-turboquant/bin/test-quantize-fns
```

This build was copied from:

```bash
axelera-ander-wfh:/home/ubuntu/dev/repos/turboquant-cpu/llama.cpp/build
```

It is a Linux x86_64 build and will not execute on this macOS ARM machine.

## Baseline

The starting point was a regular CPU-only `llama.cpp` release build on the x86
host, using native CPU code generation:

```bash
cmake -S llama.cpp -B llama.cpp/build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_CUDA=OFF

cmake --build llama.cpp/build \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$(nproc)"
```

The copied build cache records `CMAKE_BUILD_TYPE=Release`, `GGML_NATIVE=ON`,
`GGML_CPU=ON`, and `GGML_CUDA=OFF`.

## Customization Steps

1. Added TurboQuant K/V cache type plumbing for `tbq2`, `tbq3`, and `tbq4`.
   This made the new cache types visible to llama.cpp type traits, CLI cache
   type parsing, quantization dispatch, and K/V cache allocation.

2. Allowed quantized K/V cache types into the CPU split-KV decode path when the
   type has a CPU vector-dot implementation and query conversion path. Without
   this, long-context quantized K/V decode does not use the intended parallel
   path.

3. Added the x86 TBQ4 K-cache vector-dot implementation in the x86 quantization
   backend. The important performance path is the AVX2 TBQ4 dot against Q8_0
   query blocks.

4. Added a fused TBQ4 V-cache accumulation path. This avoids materializing an
   intermediate F32 dequantization buffer inside the flash-attention decode
   loop.

5. Kept the scoped Gemma 4 tokenizer fix required for generation and
   perplexity. Gemma 4 BPE merges can contain whitespace-bearing merge sides,
   so the custom tree avoids the generic no-whitespace merge-side assertion for
   that model family.

## Validation

The local copied binary was checked against the remote source binary:

```text
sha256(llama-bench) = 3cdd742c089a907a1b4a571e788b5cc19d88e8dafc965e82a0f9c7c1dad3e519
```

The binary type is:

```text
ELF 64-bit LSB pie executable, x86-64
```

The x86 benchmark outputs produced by this build are kept under:

```bash
benchmark_results/x86_full
```
