#!/usr/bin/env python3
"""Compare Gemma 4 CPU benchmark artifacts between x86 and a macOS run."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report_notebook import SETTING_LABELS, SETTINGS, read_jsonl, task_adherence_series  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
X86_SPEED = ROOT / "turboquant/results/gemma4_e4b_cpu_summary.csv"
X86_PPL = ROOT / "turboquant/results/paper_ppl/gemma4_e4b_x86_ppl20/paper_ppl_results.csv"
X86_QUALITY = ROOT / "turboquant/results/paper_quality/gemma4_e4b_hard_generations.jsonl"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def speed_key(setting: str, depth: int) -> tuple[str, int]:
    return setting, int(depth)


def load_x86_speed() -> dict[tuple[str, int], float]:
    rows = read_csv(X86_SPEED)
    out = {}
    for row in rows:
        setting = f"{row['type_k']}/{row['type_v']}"
        out[speed_key(setting, int(row["kv_depth"]))] = float(row["tokens_per_second"])
    return out


def load_host_speed(path: Path) -> dict[tuple[str, int], float]:
    rows = read_csv(path)
    out = {}
    for row in rows:
        setting = row.get("paper_config") or f"{row.get('type_k')}/{row.get('type_v')}"
        depth = int(row.get("n_depth") or row.get("kv_depth"))
        tps = float(row.get("avg_ts") or row.get("tokens_per_second"))
        out[speed_key(setting, depth)] = tps
    return out


def compare_speed(macos_root: Path, out_dir: Path) -> list[dict]:
    mac_path = macos_root / "paper_bench/gemma4_e4b_cpu/paper_bench_results.csv"
    if not mac_path.exists():
        raise SystemExit(f"missing macOS speed results: {mac_path}")
    x86 = load_x86_speed()
    mac = load_host_speed(mac_path)
    keys = sorted(set(x86) | set(mac), key=lambda k: (SETTINGS.index(k[0]) if k[0] in SETTINGS else 99, k[1]))
    rows = []
    for setting, depth in keys:
        xr = x86.get((setting, depth))
        mr = mac.get((setting, depth))
        rows.append(
            {
                "setting": setting,
                "setting_label": SETTING_LABELS.get(setting, setting),
                "depth": depth,
                "x86_tok_s": "" if xr is None else f"{xr:.6f}",
                "macos_tok_s": "" if mr is None else f"{mr:.6f}",
                "macos_vs_x86": "" if xr is None or mr is None else f"{mr / xr:.4f}",
                "macos_delta_pct": "" if xr is None or mr is None else f"{100 * (mr / xr - 1):+.2f}",
            }
        )
    write_csv(out_dir / "speed_x86_vs_macos.csv", rows)
    return rows


def compare_ppl(macos_root: Path, out_dir: Path) -> list[dict]:
    mac_path = macos_root / "paper_ppl/gemma4_e4b_cpu_ppl20/paper_ppl_results.csv"
    if not mac_path.exists():
        raise SystemExit(f"missing macOS PPL results: {mac_path}")
    x86 = {r["config"]: r for r in read_csv(X86_PPL)}
    mac = {r["config"]: r for r in read_csv(mac_path)}
    rows = []
    for setting in SETTINGS:
        xr = x86.get(setting)
        mr = mac.get(setting)
        if not xr and not mr:
            continue
        xp = float(xr["ppl"]) if xr and xr.get("ppl") else None
        mp = float(mr["ppl"]) if mr and mr.get("ppl") else None
        rows.append(
            {
                "setting": setting,
                "setting_label": SETTING_LABELS.get(setting, setting),
                "x86_ppl": "" if xp is None else f"{xp:.6f}",
                "macos_ppl": "" if mp is None else f"{mp:.6f}",
                "macos_minus_x86": "" if xp is None or mp is None else f"{mp - xp:+.6f}",
                "macos_delta_pct": "" if xp is None or mp is None else f"{100 * (mp / xp - 1):+.2f}",
            }
        )
    write_csv(out_dir / "ppl_x86_vs_macos.csv", rows)
    return rows


def task_means(jsonl: Path) -> dict[str, float]:
    rows = read_jsonl(jsonl)
    series = task_adherence_series(rows)
    return {setting: sum(v for _, v in pts) / len(pts) for setting, pts in series.items() if pts}


def compare_quality(macos_root: Path, out_dir: Path) -> list[dict]:
    mac_path = macos_root / "paper_quality/gemma4_e4b_hard_generations.jsonl"
    if not mac_path.exists():
        raise SystemExit(f"missing macOS quality generations: {mac_path}")
    x86 = task_means(X86_QUALITY)
    mac = task_means(mac_path)
    rows = []
    for setting in SETTINGS:
        xv = x86.get(setting)
        mv = mac.get(setting)
        if xv is None and mv is None:
            continue
        rows.append(
            {
                "setting": setting,
                "setting_label": SETTING_LABELS.get(setting, setting),
                "x86_mean_task_score": "" if xv is None else f"{xv:.6f}",
                "macos_mean_task_score": "" if mv is None else f"{mv:.6f}",
                "macos_minus_x86": "" if xv is None or mv is None else f"{mv - xv:+.6f}",
            }
        )
    write_csv(out_dir / "quality_task_x86_vs_macos.csv", rows)
    return rows


def md_table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines)


def write_summary(out_dir: Path, macos_root: Path, speed: list[dict], ppl: list[dict], quality: list[dict]) -> None:
    speed_8k = [r for r in speed if str(r["depth"]) == "8192"]
    host_meta = macos_root / "host_metadata.json"
    meta = json.loads(host_meta.read_text()) if host_meta.exists() else {}
    text = [
        "# Gemma 4 CPU Comparison: x86 vs macOS",
        "",
        f"macOS result root: `{macos_root}`",
        f"macOS platform: `{meta.get('platform', 'unknown')}`",
        f"macOS machine: `{meta.get('machine', 'unknown')}`",
        "",
        "## 8K Decode Throughput",
        "",
        md_table(speed_8k, ["setting_label", "x86_tok_s", "macos_tok_s", "macos_vs_x86", "macos_delta_pct"]),
        "",
        "## Perplexity",
        "",
        md_table(ppl, ["setting_label", "x86_ppl", "macos_ppl", "macos_minus_x86", "macos_delta_pct"]),
        "",
        "## Hard-Prompt Task Score",
        "",
        md_table(quality, ["setting_label", "x86_mean_task_score", "macos_mean_task_score", "macos_minus_x86"]),
        "",
    ]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.md").write_text("\n".join(text), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--macos-root", default=str(ROOT / "turboquant/results/macos_cpu"))
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    macos_root = Path(args.macos_root).expanduser()
    out_dir = Path(args.output_dir).expanduser() if args.output_dir else macos_root / "comparison"

    speed = compare_speed(macos_root, out_dir)
    ppl = compare_ppl(macos_root, out_dir)
    quality = compare_quality(macos_root, out_dir)
    write_summary(out_dir, macos_root, speed, ppl, quality)
    print(out_dir / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
