# ARM64 macOS TurboQuant llama.cpp Build

## Artifact

Build directory:

```bash
llama.cpp/build-arm-turboquant
```

Key binaries:

```bash
llama.cpp/build-arm-turboquant/bin/llama-bench
llama.cpp/build-arm-turboquant/bin/llama-cli
llama.cpp/build-arm-turboquant/bin/llama-perplexity
llama.cpp/build-arm-turboquant/bin/test-quantize-fns
```

This is the final optimized Apple M4 Max CPU build used for the ARM follow-up.

## Baseline

The starting point was the existing custom TurboQuant llama.cpp tree after the
x86 work. A separate macOS ARM build directory was created so the final ARM
build did not overwrite the earlier local CPU build:

```bash
cmake -S llama.cpp -B llama.cpp/build-arm-turboquant \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_METAL=OFF \
  -DGGML_ACCELERATE=ON

cmake --build llama.cpp/build-arm-turboquant \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$(sysctl -n hw.ncpu)"
```

The copied build cache records `CMAKE_BUILD_TYPE=Release`, `GGML_NATIVE=ON`,
`GGML_CPU=ON`, `GGML_METAL=OFF`, and `GGML_ACCELERATE=ON`.

## Customization Steps

1. Fixed non-x86 linkage for the TurboQuant vector-dot entry points. The x86
   implementation already had TBQ wrappers, but macOS ARM needed portable
   scalar wrapper exports for `ggml_vec_dot_tbq2_q8_0`,
   `ggml_vec_dot_tbq3_q8_0`, and `ggml_vec_dot_tbq4_q8_0`.

2. Built and smoke-tested the scalar ARM port first to confirm the custom
   TurboQuant type plumbing worked on Apple Silicon.

3. Added the final ARM TBQ4 K-cache NEON path:

```text
ggml/src/ggml-cpu/arch/arm/quants.c
ggml_vec_dot_tbq4_q8_0
```

4. Added the final ARM TBQ4 V-cache fused accumulation path:

```text
ggml/src/ggml-cpu/quants.c
ggml_vec_mad_tbq4
```

5. Tested an Apple I8MM `.nrows = 2` TBQ4 experiment. It was numerically
   correct, but slower in the real `llama-bench` decode path, so it was not
   kept in the final build.

6. Kept the final benchmark comparison at 6 CPU threads and 8K KV depth to
   match the x86 investigation while avoiding the OOM issues seen during
   broader reruns.

## Validation

The final ARM benchmark binary is:

```text
Mach-O 64-bit executable arm64
```

The final optimized ARM speed outputs are kept under:

```bash
benchmark_results/arm_full/macos_cpu_arm_turboquant/t6_t10_8k_r3_pre_nrows
```

The broader ARM replication outputs, including PPL and prompt-quality data,
are kept under:

```bash
benchmark_results/arm_full/macos_cpu
```
