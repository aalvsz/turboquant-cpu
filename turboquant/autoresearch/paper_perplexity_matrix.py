#!/usr/bin/env python3
"""Run llama-perplexity across model/KV settings and save reproducible outputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
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


def command_text(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def parse_ppl(text: str) -> tuple[str, str]:
    final = re.search(r"Final estimate:\s*PPL\s*=\s*([0-9.eE+-]+)(?:\s*\+/-\s*([0-9.eE+-]+))?", text)
    if final:
        return final.group(1), final.group(2) or ""

    chunk_values = re.findall(r"\[\s*\d+\]\s*([0-9.eE+-]+)", text)
    if chunk_values:
        return chunk_values[-1], ""
    return "", ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="NAME=/path/model.gguf")
    parser.add_argument("--dataset", required=True, help="Text dataset, e.g. wiki.test.raw")
    parser.add_argument(
        "--perplexity-bin",
        default=str(repo_root() / "llama.cpp/build/bin/llama-perplexity"),
    )
    parser.add_argument("--configs", default=DEFAULT_CONFIGS)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--ctx-size", type=int, default=512)
    parser.add_argument("--chunks", type=int, default=20)
    parser.add_argument("--flash-attn", choices=["on", "off", "auto"], default="on")
    parser.add_argument("--gpu-layers", type=int, default=0)
    parser.add_argument(
        "--log-disable",
        action="store_true",
        help="Pass --log-disable to llama-perplexity. Do not use for paper runs if it suppresses PPL output.",
    )
    parser.add_argument("--output-dir", default=str(repo_root() / "turboquant/results/paper_ppl"))
    parser.add_argument("--extra-arg", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    models = parse_models(args.model)
    configs = parse_configs(args.configs)
    dataset = Path(args.dataset).expanduser()
    if not dataset.exists():
        raise SystemExit(f"missing dataset: {dataset}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "timestamp_unix": time.time(),
        "argv": sys.argv,
        "dataset": str(dataset),
        "models": {name: str(path) for name, path in models},
        "configs": [{"type_k": k, "type_v": v, "tag": tag} for k, v, tag in configs],
        "threads": args.threads,
        "ctx_size": args.ctx_size,
        "chunks": args.chunks,
        "flash_attention": args.flash_attn,
        "gpu_layers": args.gpu_layers,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    rows = []
    for model_name, model_path in models:
        if not model_path.exists():
            raise SystemExit(f"missing model: {model_path}")
        for type_k, type_v, tag in configs:
            raw_stem = f"{model_name}_{tag}"
            out_path = out_dir / f"{raw_stem}.stdout.txt"
            err_path = out_dir / f"{raw_stem}.stderr.txt"
            cmd = [
                args.perplexity_bin,
                "-m",
                str(model_path),
                "-f",
                str(dataset),
                "-t",
                str(args.threads),
                "-c",
                str(args.ctx_size),
                "--chunks",
                str(args.chunks),
                "-ctk",
                type_k,
                "-ctv",
                type_v,
                "-fa",
                args.flash_attn,
                "-ngl",
                str(args.gpu_layers),
            ]
            if args.log_disable:
                cmd.append("--log-disable")
            cmd.extend(args.extra_arg)
            print(command_text(cmd), flush=True)
            if args.dry_run:
                continue
            started = time.time()
            proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
            elapsed = time.time() - started
            out_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
            err_path.write_text(proc.stderr, encoding="utf-8", errors="replace")
            ppl, ppl_stderr = parse_ppl(proc.stdout + "\n" + proc.stderr)
            rows.append(
                {
                    "model": model_name,
                    "model_path": str(model_path),
                    "type_k": type_k,
                    "type_v": type_v,
                    "config": f"{type_k}/{type_v}",
                    "threads": args.threads,
                    "ctx_size": args.ctx_size,
                    "chunks": args.chunks,
                    "ppl": ppl,
                    "ppl_stderr": ppl_stderr,
                    "elapsed_sec": f"{elapsed:.3f}",
                    "returncode": proc.returncode,
                    "stdout": str(out_path),
                    "stderr": str(err_path),
                    "command": command_text(cmd),
                }
            )

    if rows and not args.dry_run:
        with (out_dir / "paper_ppl_results.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
