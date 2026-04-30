#!/usr/bin/env python3
"""Run a paper-grade llama-bench matrix and save raw plus normalized results.

Example:
    python turboquant/autoresearch/paper_benchmark_matrix.py \
      --model gemma4_e4b=/home/ubuntu/models/gemma-4-E4B-it-Q4_0.gguf \
      --threads-list 6,12 \
      --depths 0,512,2048,4096,8192 \
      --n-gen 128 \
      --repetitions 10
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_CONFIGS = "f16:f16,q8_0:q8_0,q4_0:q4_0,tbq4:tbq4,q8_0:tbq4"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_models(items: list[str]) -> list[tuple[str, Path]]:
    models = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"model must be NAME=PATH, got: {item}")
        name, path = item.split("=", 1)
        if not name:
            raise SystemExit(f"empty model name in: {item}")
        models.append((name, Path(path).expanduser()))
    return models


def parse_configs(value: str) -> list[tuple[str, str, str]]:
    configs = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        if ":" in raw:
            k_type, v_type = raw.split(":", 1)
        elif "/" in raw:
            k_type, v_type = raw.split("/", 1)
        else:
            k_type = v_type = raw
        tag = f"{k_type}_{v_type}" if k_type != v_type else k_type
        configs.append((k_type, v_type, tag))
    return configs


def parse_int_list(value: str) -> list[int]:
    result = []
    for raw in value.split(","):
        raw = raw.strip()
        if raw:
            result.append(int(raw))
    return result


def command_text(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def collect_host_metadata() -> dict:
    metadata = {
        "timestamp_unix": time.time(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
    }
    for name, cmd in {
        "uname": ["uname", "-a"],
        "lscpu": ["lscpu"],
    }.items():
        try:
            proc = subprocess.run(cmd, check=False, text=True, capture_output=True)
            metadata[name] = proc.stdout.strip()
        except OSError as exc:
            metadata[name] = f"unavailable: {exc}"
    return metadata


def parse_llama_bench_csv(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []

    header_index = None
    for i, line in enumerate(lines):
        if "model_filename" in line or ("model" in line and "avg_ts" in line):
            header_index = i
            break
    if header_index is None:
        for i, line in enumerate(lines):
            if "," in line and "build_commit" in line:
                header_index = i
                break
    if header_index is None:
        return []

    reader = csv.DictReader(lines[header_index:])
    return [dict(row) for row in reader]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        action="append",
        required=True,
        help="Model entry as NAME=/path/model.gguf. Repeat for multiple models.",
    )
    parser.add_argument(
        "--bench-bin",
        default=str(repo_root() / "llama.cpp/build/bin/llama-bench"),
        help="Path to llama-bench.",
    )
    parser.add_argument("--configs", default=DEFAULT_CONFIGS)
    parser.add_argument("--depths", default="0,512,2048,4096,8192")
    parser.add_argument("--threads-list", default="6")
    parser.add_argument("--n-gen", type=int, default=128)
    parser.add_argument("--n-prompt", type=int, default=0)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--flash-attn", choices=["0", "1"], default="1")
    parser.add_argument("--gpu-layers", type=int, default=0)
    parser.add_argument("--output-dir", default=str(repo_root() / "turboquant/results/paper_bench"))
    parser.add_argument("--extra-arg", action="append", default=[], help="Extra llama-bench arg. Repeat as needed.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    models = parse_models(args.model)
    configs = parse_configs(args.configs)
    threads_list = parse_int_list(args.threads_list)
    depths = args.depths
    bench_bin = Path(args.bench_bin)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata = collect_host_metadata()
    metadata.update(
        {
            "bench_bin": str(bench_bin),
            "models": {name: str(path) for name, path in models},
            "configs": [{"type_k": k, "type_v": v, "tag": tag} for k, v, tag in configs],
            "depths": depths,
            "threads_list": threads_list,
            "n_prompt": args.n_prompt,
            "n_gen": args.n_gen,
            "repetitions": args.repetitions,
            "flash_attention": args.flash_attn,
            "gpu_layers": args.gpu_layers,
        }
    )
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    normalized_rows: list[dict[str, str]] = []
    for model_name, model_path in models:
        if not model_path.exists():
            raise SystemExit(f"missing model: {model_path}")
        for threads in threads_list:
            for type_k, type_v, tag in configs:
                raw_stem = f"{model_name}_t{threads}_{tag}"
                stdout_path = out_dir / f"{raw_stem}.stdout.csv"
                stderr_path = out_dir / f"{raw_stem}.stderr.txt"
                cmd = [
                    str(bench_bin),
                    "-m",
                    str(model_path),
                    "-t",
                    str(threads),
                    "-p",
                    str(args.n_prompt),
                    "-n",
                    str(args.n_gen),
                    "-r",
                    str(args.repetitions),
                    "-d",
                    depths,
                    "-ctk",
                    type_k,
                    "-ctv",
                    type_v,
                    "-fa",
                    args.flash_attn,
                    "-ngl",
                    str(args.gpu_layers),
                    "-o",
                    "csv",
                ]
                cmd.extend(args.extra_arg)
                print(command_text(cmd), flush=True)
                if args.dry_run:
                    continue
                started = time.time()
                proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
                elapsed = time.time() - started
                stdout_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
                stderr_path.write_text(proc.stderr, encoding="utf-8", errors="replace")

                rows = parse_llama_bench_csv(proc.stdout)
                if not rows:
                    rows = [{"parse_error": "no llama-bench csv rows parsed"}]
                for row in rows:
                    row.update(
                        {
                            "paper_model": model_name,
                            "paper_model_path": str(model_path),
                            "paper_threads": str(threads),
                            "paper_type_k": type_k,
                            "paper_type_v": type_v,
                            "paper_config": f"{type_k}/{type_v}",
                            "paper_depths_requested": depths,
                            "paper_n_prompt": str(args.n_prompt),
                            "paper_n_gen": str(args.n_gen),
                            "paper_repetitions": str(args.repetitions),
                            "paper_elapsed_sec": f"{elapsed:.3f}",
                            "paper_returncode": str(proc.returncode),
                            "paper_command": command_text(cmd),
                            "paper_stdout": str(stdout_path),
                            "paper_stderr": str(stderr_path),
                        }
                    )
                    normalized_rows.append(row)

    if normalized_rows and not args.dry_run:
        fieldnames = sorted({key for row in normalized_rows for key in row})
        with (out_dir / "paper_bench_results.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(normalized_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
