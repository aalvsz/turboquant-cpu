#!/usr/bin/env python3
"""Run the full Gemma 4 CPU benchmark suite on the current host.

This is the macOS/ARM replication entry point, but it also works on Linux. It
keeps the benchmark parameters aligned with the x86 report:

- speed: 6 CPU threads, n_prompt=0, n_gen=16, repetitions=2
- PPL: WikiText-2, 20 chunks, ctx=512
- quality: hard prompt set, n_predict=256, ctx=2048
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def command_text(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def run(cmd: list[str], *, cwd: Path, log_path: Path | None = None) -> None:
    print(command_text(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"$ {command_text(cmd)}\n\n--- STDOUT ---\n{proc.stdout}\n\n--- STDERR ---\n{proc.stderr}",
            encoding="utf-8",
            errors="replace",
        )
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {command_text(cmd)}")


def capture(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, text=True, capture_output=True, check=False).stdout.strip()
    except OSError as exc:
        return f"unavailable: {exc}"


def host_metadata() -> dict:
    metadata = {
        "timestamp_unix": time.time(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "cwd": os.getcwd(),
        "uname": capture(["uname", "-a"]),
        "compiler_cc": capture(["cc", "--version"]),
        "git_head": capture(["git", "rev-parse", "HEAD"]),
    }
    if platform.system() == "Darwin":
        metadata.update(
            {
                "sysctl_hw": capture(["sysctl", "-a"]),
                "system_profiler": capture(["system_profiler", "SPHardwareDataType"]),
            }
        )
    else:
        metadata["lscpu"] = capture(["lscpu"])
    return metadata


def build_llama(root: Path, build_dir: Path, log_root: Path, skip_build: bool) -> None:
    if skip_build:
        return
    system = platform.system()
    cmake_args = [
        "cmake",
        "-S",
        "llama.cpp",
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DGGML_NATIVE=ON",
    ]
    if system == "Darwin":
        cmake_args.extend(["-DGGML_METAL=OFF", "-DGGML_ACCELERATE=ON"])
    else:
        cmake_args.extend(["-DGGML_METAL=OFF", "-DGGML_CUDA=OFF"])
    run(cmake_args, cwd=root, log_path=log_root / "build_configure.log")

    jobs = capture(["sysctl", "-n", "hw.ncpu"]) if system == "Darwin" else str(os.cpu_count() or 6)
    run(
        [
            "cmake",
            "--build",
            str(build_dir),
            "--target",
            "llama-cli",
            "llama-bench",
            "llama-perplexity",
            "-j",
            jobs.strip() or "6",
        ],
        cwd=root,
        log_path=log_root / "build_compile.log",
    )


def ensure_dataset(root: Path, dataset: Path, allow_download: bool) -> Path:
    if dataset.exists():
        return dataset
    if not allow_download:
        raise SystemExit(f"missing dataset: {dataset}")
    script = root / "llama.cpp/scripts/get-wikitext-2.sh"
    if not script.exists():
        raise SystemExit(f"missing dataset and downloader: {script}")
    run(["bash", str(script)], cwd=root, log_path=root / "turboquant/results/macos_cpu/wikitext_download.log")
    if not dataset.exists():
        raise SystemExit(f"dataset still missing after downloader: {dataset}")
    return dataset


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Path to Gemma 4 E4B Q4_0 GGUF")
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--label", default="macos_cpu")
    parser.add_argument("--build-dir", default="")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--no-download-dataset", action="store_true")
    parser.add_argument("--dataset", default=str(root / "llama.cpp/wikitext-2-raw/wiki.test.raw"))
    args = parser.parse_args()

    model = Path(args.model).expanduser().resolve()
    if not model.exists():
        raise SystemExit(f"missing model: {model}")

    label_root = root / "turboquant/results" / args.label
    label_root.mkdir(parents=True, exist_ok=True)
    (label_root / "host_metadata.json").write_text(json.dumps(host_metadata(), indent=2) + "\n", encoding="utf-8")

    default_build = "llama.cpp/build-macos-cpu" if platform.system() == "Darwin" else "llama.cpp/build-cpu-suite"
    build_dir = root / (args.build_dir or default_build)
    build_llama(root, build_dir, label_root, args.skip_build)

    bin_dir = build_dir / "bin"
    bench_bin = bin_dir / "llama-bench"
    cli_bin = bin_dir / "llama-cli"
    ppl_bin = bin_dir / "llama-perplexity"
    for binary in [bench_bin, cli_bin, ppl_bin]:
        if not binary.exists():
            raise SystemExit(f"missing binary: {binary}")

    dataset = ensure_dataset(root, Path(args.dataset).expanduser(), not args.no_download_dataset)

    speed_dir = label_root / "paper_bench/gemma4_e4b_cpu"
    run(
        [
            sys.executable,
            "turboquant/autoresearch/paper_benchmark_matrix.py",
            "--bench-bin",
            str(bench_bin),
            "--model",
            f"gemma4_e4b={model}",
            "--threads-list",
            str(args.threads),
            "--depths",
            "0,512,2048,4096,8192",
            "--n-gen",
            "16",
            "--repetitions",
            "2",
            "--output-dir",
            str(speed_dir),
        ],
        cwd=root,
        log_path=label_root / "speed_matrix.log",
    )

    ppl_dir = label_root / "paper_ppl/gemma4_e4b_cpu_ppl20"
    run(
        [
            sys.executable,
            "turboquant/autoresearch/paper_perplexity_matrix.py",
            "--perplexity-bin",
            str(ppl_bin),
            "--model",
            f"gemma4_e4b={model}",
            "--dataset",
            str(dataset),
            "--threads",
            str(args.threads),
            "--ctx-size",
            "512",
            "--chunks",
            "20",
            "--output-dir",
            str(ppl_dir),
        ],
        cwd=root,
        log_path=label_root / "ppl_matrix.log",
    )

    quality_dir = label_root / "paper_quality"
    run(
        [
            sys.executable,
            "turboquant/autoresearch/paper_quality_generate.py",
            "--llama-cli",
            str(cli_bin),
            "--model",
            f"gemma4_e4b={model}",
            "--prompt-set",
            "hard",
            "--threads",
            str(args.threads),
            "--ctx-size",
            "2048",
            "--n-predict",
            "256",
            "--output",
            str(quality_dir / "gemma4_e4b_hard_generations.jsonl"),
            "--raw-dir",
            str(quality_dir / "hard_raw"),
            "--resume",
        ],
        cwd=root,
        log_path=label_root / "quality_hard_generation.log",
    )

    print(f"\ncompleted benchmark suite under {label_root}")
    print("next: copy this results directory back to the x86 workspace and run:")
    print(f"  python turboquant/autoresearch/compare_gemma4_cpu_hosts.py --macos-root {label_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
