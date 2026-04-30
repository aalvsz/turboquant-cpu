# turboquant-cpu

Standalone snapshot of the TurboQuant CPU work and the modified `llama.cpp`
tree used for the benchmarks.

## Contents

- `llama.cpp/` - full `llama.cpp` source snapshot with TurboQuant CPU changes.
  Generated `build/` artifacts are not included.
- `turboquant/` - research notes, scripts, plots, and raw results for the
  TurboQuant CPU benchmark work. The nested `autoresearch` checkout is flattened
  into normal source files.
- `patches/` - reproducibility artifacts for the modified `llama.cpp` source:
  full working-tree diff vs upstream, uncommitted patch, commit log, and the
  older WIP stash patch.

## Build

```bash
./scripts/build_llama_cpu.sh
```

This configures `llama.cpp/build` with native CPU flags and builds:
`llama-cli`, `llama-bench`, `llama-perplexity`, and `test-quantize-fns`.
The saved `llama.cpp/tests/test-turboquant.c` source is included for audit, but
this snapshot does not wire it into CMake as a build target.

Example hybrid KV benchmark:

```bash
./llama.cpp/build/bin/llama-bench \
  -m /path/to/model.gguf \
  -ctk q8_0 -ctv tbq4 \
  -t 12 -p 0 -n 128 -r 2 -fa 1 -d 8192
```

## Notes

The benchmark scripts in `turboquant/autoresearch/` use configurable worker and
model paths. The model files are not included because they are large external
GGUF artifacts.

Recent sanitized benchmark findings:

- `turboquant/GEMMA4_E4B_CPU_FINDINGS.md` - Gemma 4 E4B CPU decode results for
  F16, Q8_0, Q4_0, and TBQ4 KV cache types, plus preliminary Gemma 4
  perplexity and deterministic prompt-quality follow-up.
- `turboquant/PAPERIZATION.md` - paper-grade benchmark, quality, GPT-5.5
  judge, ablation, and artifact plan.
- `turboquant/ARM_REPLICATION.md` - later ARM CPU replication protocol.
