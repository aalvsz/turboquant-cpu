#!/usr/bin/env python3
"""Analyze TurboQuant edge-agent benchmark output."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def pct(candidate: float, baseline: float) -> str:
    if baseline == 0:
        return "n/a"
    return f"{(candidate / baseline - 1.0) * 100.0:+.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    args = parser.parse_args()
    summary = read_csv(args.run_root / "summary.csv")
    by_model = {}
    for row in summary:
        by_model.setdefault(row["model"], {})[row["config"]] = row

    lines = [
        "# Agent KV Comparison",
        "",
        f"Run folder: `{args.run_root}`",
        "",
        "## Wall Time vs Q4",
        "",
        "Lower is better.",
        "",
        "| model | config | total wall s | vs Q4 | mean score | completion tok/s | max RSS MB |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    preferred = ["f16/f16", "q8_0/q8_0", "q4_0/q4_0", "tbq4/tbq4", "q8_0/tbq4"]
    for model, rows in sorted(by_model.items()):
        q4 = fnum(rows.get("q4_0/q4_0", {}).get("total_wall_sec", "0"))
        for cfg in preferred:
            if cfg not in rows:
                continue
            row = rows[cfg]
            wall = fnum(row["total_wall_sec"])
            lines.append(
                f"| {model} | {cfg} | {wall:.3f} | {pct(wall, q4)} | "
                f"{fnum(row['mean_score']):.3f} | {fnum(row['completion_tokens_per_sec']):.3f} | "
                f"{fnum(row['server_max_rss_mb']):.1f} |"
            )

    lines.extend([
        "",
        "## Decision Scaffold",
        "",
        "- Prefer `q8_0/tbq4` if it beats Q4 wall time while preserving mean score and JSON/tool discipline.",
        "- Prefer `tbq4/tbq4` if maximum speed is needed and task score does not drop.",
        "- Do not treat these agent scores as human-quality proof; they are a fast end-to-end regression signal.",
    ])
    (args.run_root / "AGENT_KV_COMPARISON.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

