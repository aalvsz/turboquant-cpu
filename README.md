# TurboQuant CPU Benchmark Artifacts

This repository is now an artifact snapshot for the TurboQuant CPU x86 vs ARM
investigation. It intentionally keeps only:

- benchmark results for the previous x86 run
- benchmark results for the Apple M4 Max ARM follow-up
- the custom `llama.cpp` build artifacts used for each architecture
- one build note per architecture explaining how the custom build differs from
  regular `llama.cpp`

The original source trees, scripts, virtualenv, and intermediate cleanup files
were removed to keep this repo focused on reproducible evidence.

## Layout

```text
benchmark_results/
  x86_full/
  arm_full/
llama.cpp/
  X86_64_LINUX_TURBOQUANT_BUILD.md
  ARM64_MACOS_TURBOQUANT_BUILD.md
  build-x86_64-linux-turboquant/
  build-arm-turboquant/
```

## Results

`benchmark_results/x86_full` contains the full previous x86 benchmark bundle,
including the original notebook, CSV summaries, PPL outputs, prompt-quality
outputs, figures, and source-code snapshots from that run.

`benchmark_results/arm_full` contains the M4 Max ARM follow-up bundle,
including the scalar replication outputs, final optimized ARM speed outputs,
PPL outputs, prompt-quality outputs, host metadata, and run logs.

## Builds

The x86 build is preserved here:

```text
llama.cpp/build-x86_64-linux-turboquant
```

It was copied from the previous x86 host and contains Linux x86_64 ELF
binaries. It will not run on macOS ARM, but can be copied back to a compatible
x86 Linux host.

The final ARM build is preserved here:

```text
llama.cpp/build-arm-turboquant
```

It contains macOS arm64 Mach-O binaries for the Apple M4 Max CPU follow-up.

Build provenance:

- [x86_64 Linux TurboQuant build](llama.cpp/X86_64_LINUX_TURBOQUANT_BUILD.md)
- [ARM64 macOS TurboQuant build](llama.cpp/ARM64_MACOS_TURBOQUANT_BUILD.md)

## Quick Verification

```bash
file \
  llama.cpp/build-x86_64-linux-turboquant/bin/llama-bench \
  llama.cpp/build-arm-turboquant/bin/llama-bench
```

Expected:

```text
llama.cpp/build-x86_64-linux-turboquant/bin/llama-bench: ELF 64-bit ... x86-64
llama.cpp/build-arm-turboquant/bin/llama-bench:          Mach-O 64-bit executable arm64
```

## Main Entry Points

- x86 report notebook:
  `benchmark_results/x86_full/TURBOQUANT_CPU_EXTENSIVE_REPORT.ipynb`
- x86 speed summary:
  `benchmark_results/x86_full/results/gemma4_e4b_cpu_summary.csv`
- ARM final optimized speed run:
  `benchmark_results/arm_full/macos_cpu_arm_turboquant/t6_t10_8k_r3_pre_nrows`
- ARM broader replication run:
  `benchmark_results/arm_full/macos_cpu`
