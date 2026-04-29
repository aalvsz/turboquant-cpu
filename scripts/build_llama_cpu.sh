#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMAKE_BIN="${CMAKE_BIN:-cmake}"
BUILD_DIR="${BUILD_DIR:-$ROOT/llama.cpp/build}"
JOBS="${JOBS:-$(nproc)}"

"$CMAKE_BIN" -S "$ROOT/llama.cpp" -B "$BUILD_DIR" \
  -DGGML_NATIVE=ON \
  -DLLAMA_BUILD_TESTS=ON

"$CMAKE_BIN" --build "$BUILD_DIR" \
  --target llama-cli llama-bench llama-perplexity test-quantize-fns \
  -j "$JOBS"
