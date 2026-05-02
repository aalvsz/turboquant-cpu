# Qwen3.5 Quality Fix

Date: 2026-05-01

## Scope

This report covers the ARM/M4 Qwen3.5 quality failure observed with
`unsloth/Qwen3.5-4B-GGUF` (`Qwen3.5-4B-Q4_0.gguf`) and the TurboQuant CPU
build. The x86 `axelera` host was not reachable from this session
(`ssh: Could not resolve hostname axelera`), so the x86 side still needs the
same rebuild and focused Qwen validation before cross-host Qwen conclusions are
updated.

## Root Cause

The local TurboQuant source identified the model architecture as `qwen35`, but
it routed `LLM_ARCH_QWEN35` through the older Qwen3Next graph. That path did
not load/use Qwen3.5-specific RoPE dimension sections and did not use the
upstream Qwen3.5 graph.

Control test with current upstream llama.cpp (`aab68217`) proved the GGUF file
itself is usable:

| Build | Prompt | Output |
|---|---|---|
| old TurboQuant build | `Return only OK.` | `The user's message is asking for "Return only" is a phrase.` |
| upstream llama.cpp `aab68217` | `Return only OK.` | `OK` |
| patched TurboQuant build | `Return only OK.` | `OK` |
| patched TurboQuant build | `What is 2+2? Answer with one number.` | `4` |

Raw probe outputs are in `qwen_quality_fix/raw/`.

## Patch

New ARM build:

`benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/build-arm-qwen35-tbq4-qualityfix`

Source changes:

- Added/adapted upstream `src/models/qwen35.cpp`.
- Added/adapted upstream `src/models/delta-net-base.cpp`.
- Routed `LLM_ARCH_QWEN35` to `llm_build_qwen35`.
- Loaded `qwen35.full_attention_interval` and `qwen35.rope.dimension_sections`.
- Added missing local metadata enum/value support needed by Qwen3.5.
- Adapted upstream Qwen3.5 graph calls to the older local llama.cpp API.
- Added explicit contiguous/repeated operands in the Qwen3.5 autoregressive
  delta-net path where this older CPU backend cannot safely broadcast.
- Updated `fresh_eval.py` with `--quality-extra-args` and automatic
  `--reasoning-budget 0` for Qwen quality runs.

## Focused Quality Run

Command output folder:

`qwen_quality_fix/focused_quality/`

Model:

`/Users/ander.alvarez/Downloads/Qwen3.5-4B-Q4_0.gguf`

KV settings:

- `f16/f16`
- `tbq4/tbq4`
- `q8_0/tbq4`

Results:

| Setting | prompts | mean heuristic score | degenerate outputs | returncode failures |
|---|---:|---:|---:|---:|
| `f16/f16` | 10 | 4.4 / 5 | 0 | 0 |
| `tbq4/tbq4` | 10 | 4.4 / 5 | 0 | 0 |
| `q8_0/tbq4` | 10 | 4.6 / 5 | 0 | 0 |

Runtime/memory:

| Setting | avg elapsed per prompt | max RSS |
|---|---:|---:|
| `f16/f16` | 4.45 s | 5.18 GiB |
| `tbq4/tbq4` | 4.35 s | 5.09 GiB |
| `q8_0/tbq4` | 4.66 s | 5.11 GiB |

The run completed 30/30 generations with return code 0. No raw stderr files in
the focused quality run contain `GGML_ASSERT`, `failed`, `Traceback`, or
`error:`.

## Interpretation

Qwen quality is fixed on ARM for the evaluated prompt suite. The previous
near-zero Qwen quality result should be discarded because it measured an
incorrect/incomplete Qwen3.5 graph path, not TurboQuant KV behavior.

For this focused ARM run, `tbq4/tbq4` preserved the same mean heuristic quality
as `f16/f16`, and `q8_0/tbq4` was slightly higher on this heuristic judge.
The remaining lower-scoring prompts are shared with F16 and are not TBQ-specific
regressions.

This does not make TurboQuant "lossless" in the strict mathematical sense. It
supports the narrower claim that, after fixing Qwen3.5 support, TurboQuant KV is
quality-preserving on this ARM Qwen prompt suite. The x86 host still needs the
same rebuild and Qwen focused rerun before updating cross-host Qwen claims.
