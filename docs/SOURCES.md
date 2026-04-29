# Source Audit

Snapshot date: 2026-04-29.

## TurboQuant Research Tree

Copied from:

`/home/ubuntu/dev/repos/chameleon-system-black/.claude/worktrees/turboquant2`

Original git state:

- Branch: `worktree-turboquant2...origin/main`
- Remote: `git@gitlab.com:multiverse1/apps/perte-chip-chameleon/chameleon-system-black.git`
- Untracked content was intentionally included: `FINDINGS_AMAX.md`,
  `REPORT.md`, `autoresearch/`, plots, and `results/`.

The nested `autoresearch` directory was a checkout of
`https://github.com/karpathy/autoresearch.git` on `master`. Its `.git`
directory was omitted and its tracked plus untracked files were copied as normal
repo content.

## Modified llama.cpp

Copied from:

`/home/ubuntu/llama.cpp`

Original git state:

- Remote: `https://github.com/ggml-org/llama.cpp.git`
- Upstream base: `22cae832188a1f08d18bd0a707a4ba5cd03c7349`
- Local HEAD: `a53c2d225d205b1cc8e77abb9f512218d6acb398`
- Local branch was 10 commits ahead of upstream.
- Local working tree also had:
  - `ggml/src/ggml-turboquant.c` modified with the TBQ4 amax scale patch.
  - `tools/llama-bench/llama-bench.cpp` staged with `tbq2`, `tbq3`, `tbq4`
    type parsing.

The copied `llama.cpp/` directory includes those working-tree changes. Generated
`llama.cpp/build/` artifacts were omitted.

Important patch artifacts:

- `patches/llama-cpp-working-tree-vs-upstream.patch` - complete source delta
  from upstream base to the copied working tree.
- `patches/llama-cpp-uncommitted-amax-and-bench.patch` - only the local
  uncommitted amax and llama-bench parser changes.
- `patches/llama-cpp-turboquant-commit-log.txt` - 10 local TurboQuant commits.
- `patches/llama-cpp-wip-stash-2026-04-27.patch` - older WIP stash preserved
  for audit only.

## External Runtime Inputs

Original scripts reference these external paths and hosts:

- Worker host: `ubuntu@10.15.1.154`
- Local/worker llama binaries:
  - `/home/ubuntu/llama.cpp/build/bin/llama-bench`
  - `/home/ubuntu/llama.cpp/build/bin/llama-cli`
  - `/home/ubuntu/llama_patched/bin`
  - `/home/ubuntu/llama_amax_clean/bin`
- GGUF model paths:
  - `/home/ubuntu/models/llm/reasoning_gilda_Q4KM.gguf`
  - `/home/ubuntu/models/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
  - `/home/ubuntu/models/llm/Qwen2.5-7B-Instruct-Q4_K_M.gguf`
  - `/home/ubuntu/models/llm/gemma-2-9b-it-Q4_K_M.gguf`
  - `/home/ubuntu/models/llm/Llama-4-Scout-17B-16E-Instruct-Q4_K_M.gguf`
  - `/home/ubuntu/models/llm/Q4_K_M/Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00001-of-00002.gguf`

These files are not included in this repository.

## Known Caveat

`turboquant/FINDINGS_AMAX.md` notes that the older dirty WIP source had a flash
attention dispatch regression affecting symmetric quantized KV. The current
copied `llama.cpp/` source is the clean `a53c2d225` TurboQuant line plus the
TBQ4 amax patch and llama-bench parser change. Treat the stash patch as audit
history, not the recommended build.

## Local Verification

`./scripts/build_llama_cpu.sh` was run successfully on this snapshot and built
`llama-cli`, `llama-bench`, `llama-perplexity`, and `test-quantize-fns`.

Running `./llama.cpp/build/bin/test-quantize-fns` produced three failures in the
existing experimental TBQ checks:

- `tbq2 absolute quantization error`
- `tbq2 dot product error`
- `tbq3 absolute quantization error`

No model benchmark was run during packaging because the required GGUF model
files are external to this repository.
