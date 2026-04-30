#!/usr/bin/env python3
"""Cosine-similarity summary for paper_quality_generate.py JSONL outputs."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]{2,}", text.lower())


def tf_vec(tokens: list[str]) -> dict[str, int]:
    return dict(Counter(tokens))


def cosine_similarity(a: dict[str, int], b: dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", nargs="+")
    args = parser.parse_args()

    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    examples = {}
    for raw_path in args.jsonl:
        path = Path(raw_path)
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                reference = row.get("reference", "")
                output = row.get("output", "")
                score = cosine_similarity(tf_vec(tokenize(reference)), tf_vec(tokenize(output)))
                key = (row["model"], row["setting"])
                groups[key].append(score)
                examples.setdefault(key, output[:160].replace("\n", " "))

    print("| Model | Setting | N | Mean cosine | First output excerpt |")
    print("|---|---|---:|---:|---|")
    for (model, setting), scores in sorted(groups.items()):
        mean = sum(scores) / len(scores) if scores else 0.0
        print(f"| {model} | `{setting}` | {len(scores)} | {mean:.3f} | {examples[(model, setting)]} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
