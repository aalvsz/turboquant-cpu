#!/usr/bin/env python3
"""Generate deterministic quality samples for later cosine and LLM judging."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_sets import get_prompt_records  # noqa: E402


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


def clean_generation_text(raw: str, prompt: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    text = re.sub(r"\n\[\s*Prompt:.*?\]\s*", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\nExiting\.\.\.\s*$", "", text)
    marker = f"> {prompt}"
    if marker in text:
        text = text.split(marker, 1)[1]
    text = re.sub(r"(?s)^.*?available commands:.*?\n\n", "", text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="NAME=/path/model.gguf")
    parser.add_argument("--llama-cli", default=str(repo_root() / "llama.cpp/build/bin/llama-cli"))
    parser.add_argument("--configs", default=DEFAULT_CONFIGS)
    parser.add_argument("--prompt-set", choices=["smoke", "paper", "hard"], default="smoke")
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--ctx-size", type=int, default=1024)
    parser.add_argument("--n-predict", type=int, default=160)
    parser.add_argument("--flash-attn", choices=["on", "off", "auto"], default="on")
    parser.add_argument("--temperature", default="0")
    parser.add_argument("--top-k", default="1")
    parser.add_argument("--gpu-layers", type=int, default=0)
    parser.add_argument(
        "--output",
        default=str(repo_root() / "turboquant/results/paper_quality/generations.jsonl"),
    )
    parser.add_argument("--raw-dir", default="")
    parser.add_argument("--extra-arg", action="append", default=[])
    parser.add_argument("--resume", action="store_true", help="Skip model/config/prompt rows already present in the output JSONL")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    models = parse_models(args.model)
    configs = parse_configs(args.configs)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_dir = Path(args.raw_dir) if args.raw_dir else output_path.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    completed: set[tuple[str, str, int]] = set()
    if args.resume and output_path.exists():
        with output_path.open(encoding="utf-8") as existing:
            for line in existing:
                if not line.strip():
                    continue
                row = json.loads(line)
                completed.add((row["model"], row["setting"], int(row["prompt_id"])))

    prompts = get_prompt_records(args.prompt_set)
    with output_path.open("a", encoding="utf-8") as out:
        for model_name, model_path in models:
            if not model_path.exists():
                raise SystemExit(f"missing model: {model_path}")
            for type_k, type_v, tag in configs:
                for idx, record in enumerate(prompts, start=1):
                    prompt = record.prompt
                    reference = record.reference
                    setting = f"{type_k}/{type_v}"
                    if (model_name, setting, idx) in completed:
                        print(f"skip existing {model_name} {setting} prompt {idx}", flush=True)
                        continue
                    raw_path = raw_dir / f"{model_name}_{tag}_p{idx}.txt"
                    cmd = [
                        args.llama_cli,
                        "-m",
                        str(model_path),
                        "-t",
                        str(args.threads),
                        "-c",
                        str(args.ctx_size),
                        "-n",
                        str(args.n_predict),
                        "-ctk",
                        type_k,
                        "-ctv",
                        type_v,
                        "-fa",
                        args.flash_attn,
                        "-ngl",
                        str(args.gpu_layers),
                        "-p",
                        prompt,
                        "--temp",
                        args.temperature,
                        "--top-k",
                        args.top_k,
                        "--single-turn",
                        "--simple-io",
                        "--log-disable",
                        "--no-display-prompt",
                        "--no-show-timings",
                    ]
                    cmd.extend(args.extra_arg)
                    print(command_text(cmd), flush=True)
                    if args.dry_run:
                        continue
                    started = time.time()
                    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
                    elapsed = time.time() - started
                    raw_text = proc.stdout + ("\n--- STDERR ---\n" + proc.stderr if proc.stderr else "")
                    raw_path.write_text(raw_text, encoding="utf-8", errors="replace")
                    record = {
                        "model": model_name,
                        "model_path": str(model_path),
                        "type_k": type_k,
                        "type_v": type_v,
                        "setting": setting,
                        "tag": tag,
                        "prompt_id": idx,
                        "category": record.category,
                        "prompt": prompt,
                        "reference": reference,
                        "output": clean_generation_text(proc.stdout, prompt),
                        "raw_output_path": str(raw_path),
                        "returncode": proc.returncode,
                        "elapsed_sec": round(elapsed, 3),
                        "command": command_text(cmd),
                    }
                    out.write(json.dumps(record, ensure_ascii=True) + "\n")
                    out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
