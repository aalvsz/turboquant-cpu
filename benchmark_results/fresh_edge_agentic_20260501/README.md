# Fresh TurboQuant CPU Edge/Agentic Evaluation

This directory is for the fresh-from-scratch evaluation requested on 2026-05-01.
It intentionally treats older result folders as historical context only, not as
evidence for the new conclusion.

Models:

- `gemma4_e4b`: existing `gemma-4-E4B-it-Q4_0.gguf`
- `qwen35_4b`: `unsloth/Qwen3.5-4B-GGUF`, file `Qwen3.5-4B-Q4_0.gguf`

KV configurations:

- `f16/f16`
- `q8_0/q8_0`
- `q4_0/q4_0`
- `tbq4/tbq4`
- `q8_0/tbq4`

Fresh host folders:

- `arm_m4/`
- `x86_axelera/`
- `arm_m4_tbq4_opt/`: focused follow-up run with a unified Qwen-capable ARM
  build plus NEON TBQ4 K/V paths

Scripts live in `scripts/`. Raw command output is kept next to normalized CSV
summaries so every table can be audited back to the originating command.

Follow-up assessment:

- `ARM_TBQ4_OPT_BUILD_ASSESSMENT.md` summarizes the unified ARM build, memory
  guard validation, focused 8K results, and claim impact.

OOM safety:

- `scripts/fresh_eval.py` runs model commands sequentially.
- Before each model command it records a memory snapshot and refuses to start if
  free memory is below `--min-memory-free-pct` (default `15`) or, when set,
  `--min-memory-free-gb`.
- Do not run separate `llama-bench`, `llama-cli`, or `llama-perplexity`
  processes in parallel for these 4B model tests unless the machine has been
  checked for sufficient free RAM first.
