#!/usr/bin/env python3
"""Aggregate agentic KV-cache impact results across devices."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def stats(values: Iterable[float]) -> Dict[str, float]:
    vals = [float(v) for v in values]
    if not vals:
        return {"n": 0, "mean": 0.0, "std": 0.0, "ci95": 0.0}
    mean = sum(vals) / len(vals)
    if len(vals) == 1:
        return {"n": 1, "mean": mean, "std": 0.0, "ci95": 0.0}
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    std = math.sqrt(var)
    return {"n": len(vals), "mean": mean, "std": std, "ci95": 1.96 * std / math.sqrt(len(vals))}


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_runs(inputs: List[Path]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    summaries: List[Dict[str, str]] = []
    tasks: List[Dict[str, str]] = []
    for root in inputs:
        for row in read_csv(root / "summary.csv"):
            row["run_dir"] = str(root)
            summaries.append(row)
        for row in read_csv(root / "tasks.csv"):
            row["run_dir"] = str(root)
            tasks.append(row)
    return summaries, tasks


def aggregate_summary(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["host_label"], row["ctx_size"], row["model"], row["config"], row.get("task_suite", ""))
        grouped[key].append(row)

    q4_wall: Dict[Tuple[str, str, str, str], float] = {}
    q4_quality: Dict[Tuple[str, str, str, str], float] = {}
    for (host, ctx, model, config, suite), vals in grouped.items():
        if config == "q4_0/q4_0":
            base_key = (host, ctx, model, suite)
            q4_wall[base_key] = stats(fnum(v["total_wall_sec"]) for v in vals)["mean"]
            q4_quality[base_key] = stats(fnum(v["mean_quality_total"]) for v in vals)["mean"]

    out: List[Dict[str, Any]] = []
    for (host, ctx, model, config, suite), vals in sorted(grouped.items()):
        wall = stats(fnum(v["total_wall_sec"]) for v in vals)
        quality = stats(fnum(v["mean_quality_total"]) for v in vals)
        json_valid = stats(fnum(v["final_json_valid_rate"]) for v in vals)
        plan_valid = stats(fnum(v["plan_valid_rate"]) for v in vals)
        tool = stats(fnum(v["mean_tool_use_score"]) for v in vals)
        correct = stats(fnum(v["mean_correctness_score"]) for v in vals)
        rapl_joules = stats(fnum(v.get("rapl_package_joules")) for v in vals)
        rapl_watts = stats(fnum(v.get("rapl_package_watts_avg")) for v in vals)
        battery_joules = stats(fnum(v.get("battery_joules")) for v in vals)
        battery_watts = stats(fnum(v.get("battery_power_w_avg")) for v in vals)
        throttled = max(int(fnum(v.get("vcgencmd_throttled_or"))) for v in vals)
        energy_joules = rapl_joules["mean"] if rapl_joules["mean"] > 0 else battery_joules["mean"]
        power_watts = rapl_watts["mean"] if rapl_watts["mean"] > 0 else battery_watts["mean"]
        base_key = (host, ctx, model, suite)
        q4w = q4_wall.get(base_key, 0.0)
        q4q = q4_quality.get(base_key, 0.0)
        out.append({
            "host_label": host,
            "ctx_size": int(float(ctx)),
            "model": model,
            "task_suite": suite,
            "config": config,
            "repeats": int(wall["n"]),
            "wall_mean_sec": wall["mean"],
            "wall_ci95_sec": wall["ci95"],
            "speedup_vs_q4_pct": 100.0 * (q4w - wall["mean"]) / q4w if q4w else 0.0,
            "quality_mean": quality["mean"],
            "quality_ci95": quality["ci95"],
            "quality_delta_vs_q4": quality["mean"] - q4q if q4q else 0.0,
            "json_valid_mean": json_valid["mean"],
            "plan_valid_mean": plan_valid["mean"],
            "tool_use_mean": tool["mean"],
            "correctness_mean": correct["mean"],
            "rss_max_mb": max(fnum(v.get("server_max_rss_mb")) for v in vals),
            "thermal_max_c": max(fnum(v.get("thermal_max_c")) for v in vals),
            "throttled_or": throttled,
            "rapl_joules_mean": rapl_joules["mean"],
            "rapl_watts_avg": rapl_watts["mean"],
            "battery_joules_mean": battery_joules["mean"],
            "battery_power_w_avg": battery_watts["mean"],
            "energy_joules_mean": energy_joules,
            "power_w_avg": power_watts,
        })
    return out


def aggregate_categories(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["host_label"],
            row["ctx_size"],
            row["model"],
            row["config"],
            row.get("task_suite", ""),
            row.get("category", ""),
        )
        grouped[key].append(row)

    q4: Dict[Tuple[str, str, str, str, str], Dict[str, float]] = {}
    for (host, ctx, model, config, suite, category), vals in grouped.items():
        if config == "q4_0/q4_0":
            q4[(host, ctx, model, suite, category)] = {
                "quality": stats(fnum(v["quality_total"]) for v in vals)["mean"],
                "wall": stats(fnum(v["wall_sec"]) for v in vals)["mean"],
            }

    out: List[Dict[str, Any]] = []
    for (host, ctx, model, config, suite, category), vals in sorted(grouped.items()):
        quality = stats(fnum(v["quality_total"]) for v in vals)
        wall = stats(fnum(v["wall_sec"]) for v in vals)
        json_valid = stats(1.0 if str(v.get("final_json_valid")).lower() == "true" else 0.0 for v in vals)
        tool = stats(fnum(v["tool_use_score"]) for v in vals)
        correct = stats(fnum(v["correctness_score"]) for v in vals)
        safety = stats(fnum(v["safety_score"]) for v in vals)
        base = q4.get((host, ctx, model, suite, category), {})
        base_wall = base.get("wall", 0.0)
        base_quality = base.get("quality", 0.0)
        out.append({
            "host_label": host,
            "ctx_size": int(float(ctx)),
            "model": model,
            "task_suite": suite,
            "category": category,
            "config": config,
            "tasks": int(quality["n"]),
            "quality_mean": quality["mean"],
            "quality_delta_vs_q4": quality["mean"] - base_quality if base_quality else 0.0,
            "wall_mean_sec": wall["mean"],
            "speedup_vs_q4_pct": 100.0 * (base_wall - wall["mean"]) / base_wall if base_wall else 0.0,
            "json_valid_mean": json_valid["mean"],
            "tool_use_mean": tool["mean"],
            "correctness_mean": correct["mean"],
            "safety_mean": safety["mean"],
        })
    return out


def fmt(value: Any, digits: int = 3) -> str:
    if isinstance(value, int):
        return str(value)
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return str(value)


def write_report(out_dir: Path, summary: List[Dict[str, Any]], categories: List[Dict[str, Any]], inputs: List[Path]) -> None:
    lines = [
        "# Agentic KV-Cache Quantization Impact Report",
        "",
        "## Scope",
        "",
        "- Measures tool calling, reasoning, JSON/schema stability, safety behavior, and end-to-end latency under different KV-cache formats.",
        "- Model weights remain 4-bit GGUF; the configs in this report change only the KV cache.",
        "- Q4 is the primary quantized baseline; F16 is the fit-in-memory speed baseline.",
        "",
        "## Inputs",
        "",
    ]
    lines.extend(f"- `{path}`" for path in inputs)
    lines.extend([
        "",
        "## Run-Level Summary",
        "",
        "| host | ctx | model | config | reps | wall s | vs Q4 | quality | delta Q4 | JSON | plan | tool | correct | RSS MB | therm C | energy J | W | throttle |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in summary:
        lines.append(
            f"| {row['host_label']} | {row['ctx_size']} | {row['model']} | {row['config']} | {row['repeats']} | "
            f"{fmt(row['wall_mean_sec'])} | {fmt(row['speedup_vs_q4_pct'], 1)}% | "
            f"{fmt(row['quality_mean'])} | {fmt(row['quality_delta_vs_q4'])} | "
            f"{fmt(row['json_valid_mean'])} | {fmt(row['plan_valid_mean'])} | "
            f"{fmt(row['tool_use_mean'])} | {fmt(row['correctness_mean'])} | {fmt(row['rss_max_mb'], 1)} | "
            f"{fmt(row['thermal_max_c'], 1)} | {fmt(row['energy_joules_mean'], 1)} | "
            f"{fmt(row['power_w_avg'], 1)} | {row['throttled_or']} |"
        )
    lines.extend([
        "",
        "## Category Impact",
        "",
        "| host | model | category | config | tasks | quality | delta Q4 | wall s | vs Q4 | JSON | tool | correct | safety |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in categories:
        lines.append(
            f"| {row['host_label']} | {row['model']} | {row['category']} | {row['config']} | {row['tasks']} | "
            f"{fmt(row['quality_mean'])} | {fmt(row['quality_delta_vs_q4'])} | "
            f"{fmt(row['wall_mean_sec'])} | {fmt(row['speedup_vs_q4_pct'], 1)}% | "
            f"{fmt(row['json_valid_mean'])} | {fmt(row['tool_use_mean'])} | "
            f"{fmt(row['correctness_mean'])} | {fmt(row['safety_mean'])} |"
        )
    lines.extend([
        "",
        "## Reading Guide",
        "",
        "- A useful KV quantization result should improve wall time or memory versus Q4 without reducing JSON, tool-use, reasoning/correctness, or safety scores.",
        "- A result that is faster than Q4 but materially below Q4 on quality should be treated as a deployment risk, not a win.",
        "- F16 can be faster when memory fits; KV quantization matters most when context length, concurrency, or memory pressure becomes the bottleneck.",
        "- Energy columns use RAPL package energy on x86 when available, otherwise battery discharge telemetry on macOS; Raspberry Pi rows currently expose thermal/throttle telemetry but not wall-power energy.",
    ])
    out_dir.joinpath("AGENTIC_KV_IMPACT_REPORT.md").write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries, tasks = load_runs(args.inputs)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    summary_rows = aggregate_summary(summaries)
    category_rows = aggregate_categories(tasks)
    write_csv(out / "run_summary.csv", summary_rows)
    write_csv(out / "category_impact.csv", category_rows)
    write_report(out, summary_rows, category_rows, args.inputs)
    print(out)


if __name__ == "__main__":
    main()
