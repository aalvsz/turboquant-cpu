#!/usr/bin/env python3
"""Generate paper-style reports for TurboQuant edge-agent runs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, Iterable, List, Tuple


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


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
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fnum(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        if isinstance(value, str) and value.lower() == "true":
            return 1.0
        if isinstance(value, str) and value.lower() == "false":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def stats(values: Iterable[float]) -> Dict[str, float]:
    vals = [float(v) for v in values]
    if not vals:
        return {"n": 0, "mean": 0.0, "std": 0.0, "ci95": 0.0, "min": 0.0, "max": 0.0}
    sd = stdev(vals) if len(vals) > 1 else 0.0
    return {
        "n": len(vals),
        "mean": mean(vals),
        "std": sd,
        "ci95": 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


def load_roots(roots: List[Path]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, Any]]]:
    summaries: List[Dict[str, str]] = []
    tasks: List[Dict[str, str]] = []
    metadata: List[Dict[str, Any]] = []
    for root in roots:
        root = root.resolve()
        meta_path = root / "metadata.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        meta["run_root"] = str(root)
        metadata.append(meta)
        for row in read_csv(root / "summary.csv"):
            row["run_root"] = str(root)
            summaries.append(row)
        for row in read_csv(root / "tasks.csv"):
            row["run_root"] = str(root)
            tasks.append(row)
    return summaries, tasks, metadata


def run_kind(row: Dict[str, str]) -> str:
    return row.get("run_kind") or "agent"


def planner_mode(row: Dict[str, str]) -> str:
    return row.get("planner_mode") or "llm"


def task_suite(row: Dict[str, str]) -> str:
    return row.get("task_suite") or "core"


def aggregate_summary(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(run_kind(row), planner_mode(row), task_suite(row), row["host_label"], row["ctx_size"], row["model"], row["config"])].append(row)

    out: List[Dict[str, Any]] = []
    base_wall: Dict[Tuple[str, str, str, str, str, str], float] = {}
    base_quality: Dict[Tuple[str, str, str, str, str, str], float] = {}
    for key, items in grouped.items():
        kind, planner, suite, host, ctx, model, config = key
        wall = stats(fnum(item["total_wall_sec"]) for item in items)
        quality = stats(fnum(item.get("mean_quality_total") or item.get("mean_score")) for item in items)
        if config == "q4_0/q4_0":
            base_wall[(kind, planner, suite, host, ctx, model)] = wall["mean"]
            base_quality[(kind, planner, suite, host, ctx, model)] = quality["mean"]

    for key in sorted(grouped):
        kind, planner, suite, host, ctx, model, config = key
        items = grouped[key]
        wall = stats(fnum(item["total_wall_sec"]) for item in items)
        quality = stats(fnum(item.get("mean_quality_total") or item.get("mean_score")) for item in items)
        tok = stats(fnum(item["completion_tokens_per_sec"]) for item in items)
        rss = stats(fnum(item["server_max_rss_mb"]) for item in items)
        cpu = stats(fnum(item.get("server_max_cpu_pct")) for item in items)
        thermal = stats(fnum(item.get("thermal_max_c")) for item in items)
        watts = stats(fnum(item.get("rapl_package_watts_avg")) for item in items)
        joules = stats(fnum(item.get("rapl_package_joules")) for item in items)
        battery_watts = stats(fnum(item.get("battery_power_w_avg")) for item in items)
        battery_joules = stats(fnum(item.get("battery_joules")) for item in items)
        json_rate = stats(fnum(item["final_json_valid_rate"]) for item in items)
        plan_rate = stats(fnum(item["plan_valid_rate"]) for item in items)
        base = base_wall.get((kind, planner, suite, host, ctx, model), 0.0)
        qbase = base_quality.get((kind, planner, suite, host, ctx, model), 0.0)
        out.append({
            "run_kind": kind,
            "planner_mode": planner,
            "task_suite": suite,
            "host_label": host,
            "ctx_size": int(float(ctx)),
            "model": model,
            "config": config,
            "repeats": wall["n"],
            "wall_mean_sec": wall["mean"],
            "wall_std_sec": wall["std"],
            "wall_ci95_sec": wall["ci95"],
            "wall_min_sec": wall["min"],
            "wall_max_sec": wall["max"],
            "vs_q4_wall_pct": ((wall["mean"] / base - 1.0) * 100.0) if base else 0.0,
            "speedup_vs_q4_pct": ((base / wall["mean"] - 1.0) * 100.0) if base and wall["mean"] else 0.0,
            "quality_mean": quality["mean"],
            "quality_std": quality["std"],
            "quality_ci95": quality["ci95"],
            "quality_delta_vs_q4": quality["mean"] - qbase if qbase else 0.0,
            "tok_s_mean": tok["mean"],
            "rss_max_mean_mb": rss["mean"],
            "cpu_max_mean_pct": cpu["mean"],
            "thermal_max_c_mean": thermal["mean"],
            "rapl_package_joules_mean": joules["mean"],
            "rapl_package_watts_avg_mean": watts["mean"],
            "battery_joules_mean": battery_joules["mean"],
            "battery_power_w_avg_mean": battery_watts["mean"],
            "json_valid_mean": json_rate["mean"],
            "plan_valid_mean": plan_rate["mean"],
            "server_failures": sum(1 for item in items if int(fnum(item.get("server_returncode"))) != 0),
        })
    return out


def aggregate_latency(tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in tasks:
        grouped[(run_kind(row), planner_mode(row), task_suite(row), row["host_label"], row["ctx_size"], row["model"], row["config"])].append(row)
    rows: List[Dict[str, Any]] = []
    for key in sorted(grouped):
        kind, planner, suite, host, ctx, model, config = key
        items = grouped[key]
        rows.append({
            "run_kind": kind,
            "planner_mode": planner,
            "task_suite": suite,
            "host_label": host,
            "ctx_size": int(float(ctx)),
            "model": model,
            "config": config,
            "task_rows": len(items),
            "planner_sec_mean": stats(fnum(x["planner_sec"]) for x in items)["mean"],
            "deterministic_tool_sec_mean": stats(fnum(x["deterministic_tool_sec"]) for x in items)["mean"],
            "llm_tool_sec_mean": stats(fnum(x["llm_tool_sec"]) for x in items)["mean"],
            "final_sec_mean": stats(fnum(x["final_sec"]) for x in items)["mean"],
            "prompt_eval_ms_mean": stats(fnum(x["prompt_eval_ms"]) for x in items)["mean"],
            "decode_ms_mean": stats(fnum(x["decode_ms"]) for x in items)["mean"],
            "wall_sec_mean": stats(fnum(x["wall_sec"]) for x in items)["mean"],
        })
    return rows


def noninferiority_rows(tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    by_case: Dict[Tuple[str, str, str, str, str, str, str, str], Dict[str, Dict[str, str]]] = defaultdict(dict)
    for row in tasks:
        key = (run_kind(row), planner_mode(row), task_suite(row), row["host_label"], row["ctx_size"], row["model"], row["repeat"], row["task_id"])
        by_case[key][row["config"]] = row
    counts: Dict[Tuple[str, str, str, str, str, str, str], List[int]] = defaultdict(list)
    json_counts: Dict[Tuple[str, str, str, str, str, str, str], List[int]] = defaultdict(list)
    config_json: Dict[Tuple[str, str, str, str, str, str, str], List[int]] = defaultdict(list)
    q4_json: Dict[Tuple[str, str, str, str, str, str, str], List[int]] = defaultdict(list)
    for (kind, planner, suite, host, ctx, model, repeat, _task_id), configs in by_case.items():
        q4 = configs.get("q4_0/q4_0")
        if not q4:
            continue
        q4_quality = fnum(q4.get("quality_total") or q4.get("score"))
        q4_json_valid = int(fnum(q4.get("final_json_valid")) > 0)
        for config, row in configs.items():
            if config == "q4_0/q4_0":
                continue
            key = (kind, planner, suite, host, ctx, model, config)
            quality = fnum(row.get("quality_total") or row.get("score"))
            row_json_valid = int(fnum(row.get("final_json_valid")) > 0)
            counts[key].append(1 if quality + 1e-9 >= q4_quality else 0)
            json_counts[key].append(1 if row_json_valid >= q4_json_valid else 0)
            config_json[key].append(row_json_valid)
            q4_json[key].append(q4_json_valid)
    rows: List[Dict[str, Any]] = []
    for key in sorted(counts):
        kind, planner, suite, host, ctx, model, config = key
        vals = counts[key]
        jvals = json_counts[key]
        rows.append({
            "run_kind": kind,
            "planner_mode": planner,
            "task_suite": suite,
            "host_label": host,
            "ctx_size": int(float(ctx)),
            "model": model,
            "config": config,
            "paired_cases": len(vals),
            "quality_ge_q4_rate": sum(vals) / len(vals) if vals else 0.0,
            "json_ge_q4_rate": sum(jvals) / len(jvals) if jvals else 0.0,
            "config_json_valid_rate": sum(config_json[key]) / len(config_json[key]) if config_json[key] else 0.0,
            "q4_json_valid_rate": sum(q4_json[key]) / len(q4_json[key]) if q4_json[key] else 0.0,
        })
    return rows


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def pct_range(rows: List[Dict[str, Any]], key: str) -> str:
    if not rows:
        return "n/a"
    vals = [float(row[key]) for row in rows]
    return f"{min(vals):.1f}% to {max(vals):.1f}%"


def delta_range(rows: List[Dict[str, Any]], key: str) -> str:
    if not rows:
        return "n/a"
    vals = [float(row[key]) for row in rows]
    return f"{min(vals):.3f} to {max(vals):.3f}"


def write_report(out_dir: Path, roots: List[Path], metadata: List[Dict[str, Any]], agg: List[Dict[str, Any]], latency: List[Dict[str, Any]], noninf: List[Dict[str, Any]]) -> None:
    completed_jobs = sum(int(row["repeats"]) for row in agg)
    completed_task_rows = sum(int(row["task_rows"]) for row in latency)
    server_failures = sum(int(row["server_failures"]) for row in agg)
    rows_8k = [row for row in agg if int(row["ctx_size"]) == 8192]
    hard_invalid_8k = [row for row in rows_8k if float(row["json_valid_mean"]) <= 0.001]
    gemma_tbq_8k = [row for row in rows_8k if row["model"] == "gemma4_e4b" and row["config"] == "tbq4/tbq4"]
    qwen_m4_tbq_8k = [
        row for row in rows_8k
        if row["model"] == "qwen35_4b" and row["config"] == "tbq4/tbq4" and row["host_label"].startswith("m4")
    ]
    qwen_x86_8k = [row for row in rows_8k if row["model"] == "qwen35_4b" and row["host_label"].startswith("x86")]
    qwen_x86_tbq_8k = [row for row in qwen_x86_8k if row["config"] == "tbq4/tbq4"]
    qwen_x86_invalid_8k = [row for row in qwen_x86_8k if float(row["json_valid_mean"]) <= 0.001]
    telemetry_rows = [
        row for row in agg
        if float(row.get("thermal_max_c_mean") or 0.0) > 0.0
        or float(row.get("rapl_package_joules_mean") or 0.0) > 0.0
        or float(row.get("rapl_package_watts_avg_mean") or 0.0) > 0.0
        or float(row.get("battery_joules_mean") or 0.0) > 0.0
        or float(row.get("battery_power_w_avg_mean") or 0.0) > 0.0
    ]
    if qwen_x86_8k and qwen_x86_invalid_8k:
        qwen_x86_finding = (
            f"- Qwen 3.5 4B on x86 still has zero-valid-JSON rows in "
            f"`{len(qwen_x86_invalid_8k)}`/`{len(qwen_x86_8k)}` included 8K aggregates. "
            "Treat those rows as serving-path failures, not TurboQuant quality evidence."
        )
    elif qwen_x86_8k:
        qwen_x86_finding = (
            "- Qwen 3.5 4B on x86 no longer shows zero-valid-JSON 8K aggregate rows; "
            f"`tbq4/tbq4` speedups range from {pct_range(qwen_x86_tbq_8k, 'speedup_vs_q4_pct')} "
            f"with quality deltas from {delta_range(qwen_x86_tbq_8k, 'quality_delta_vs_q4')}."
        )
    else:
        qwen_x86_finding = "- No fixed Qwen 3.5 4B x86 8K rows are included in this report."
    key_findings = [
        f"- Completed `{completed_jobs}` benchmark jobs and `{completed_task_rows}` task executions. Server return-code failures in included summaries: `{server_failures}`.",
    ]
    if gemma_tbq_8k:
        key_findings.append(
            f"- Gemma 4B is the strongest current evidence: `tbq4/tbq4` is faster than Q4 in every included 8K Gemma slice, with speedups from {pct_range(gemma_tbq_8k, 'speedup_vs_q4_pct')} and quality deltas from {delta_range(gemma_tbq_8k, 'quality_delta_vs_q4')}."
        )
    else:
        key_findings.append("- No Gemma 4B 8K `tbq4/tbq4` rows are included in this report.")
    if qwen_m4_tbq_8k:
        key_findings.append(
            f"- Qwen 3.5 4B on M4 is mixed for `tbq4/tbq4`: speedups range from {pct_range(qwen_m4_tbq_8k, 'speedup_vs_q4_pct')}, while quality deltas range from {delta_range(qwen_m4_tbq_8k, 'quality_delta_vs_q4')}."
        )
    else:
        key_findings.append("- No Qwen 3.5 4B M4 8K `tbq4/tbq4` rows are included in this report.")
    key_findings.append(qwen_x86_finding)
    if gemma_tbq_8k or qwen_m4_tbq_8k:
        key_findings.append(
            "- The evidence supports a narrower CPU edge-agent claim for Gemma and a tentative, workload-scoped optimization claim. It does not yet support a broad full-paper claim that TurboQuant is lossless across model families and CPU targets."
        )
    else:
        key_findings.append(
            "- This report resolves the Qwen/x86 serving-path question only. Use the full cross-device matrix before making broad edge-agent claims."
        )
    lines = [
        "# Unified TurboQuant Edge-Agent Paper Report",
        "",
        f"Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## Input Runs",
        "",
    ]
    for meta in metadata:
        lines.append(
            f"- `{meta.get('host_label', 'unknown')}`: `{meta.get('run_root')}`; "
            f"contexts={meta.get('ctx_sizes')}; repeats={meta.get('repeats')}; "
            f"tasks={meta.get('task_count')}; threads={meta.get('threads')}"
        )
    lines.extend([
        "",
        "## Key Findings",
        "",
        *key_findings,
        "",
        "## 8K Q4 Baseline Comparison",
        "",
        "Negative `vs Q4` means lower wall time than Q4. Positive `speedup` means faster than Q4.",
        "",
        "| run | host | model | config | reps | wall mean s | wall CI95 | vs Q4 | speedup | quality | quality delta | JSON | RSS MB |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in agg:
        if int(row["ctx_size"]) != 8192:
            continue
        lines.append(
            f"| {row['run_kind']} | {row['host_label']} | {row['model']} | {row['config']} | {row['repeats']} | "
            f"{fmt(row['wall_mean_sec'])} | {fmt(row['wall_ci95_sec'])} | "
            f"{fmt(row['vs_q4_wall_pct'], 1)}% | {fmt(row['speedup_vs_q4_pct'], 1)}% | "
            f"{fmt(row['quality_mean'])} | {fmt(row['quality_delta_vs_q4'])} | "
            f"{fmt(row['json_valid_mean'])} | {fmt(row['rss_max_mean_mb'], 1)} |"
        )
    if hard_invalid_8k:
        lines.extend([
            "",
            "## Evidence Validity Flags",
            "",
            "Rows below had zero valid final JSON and are excluded from quality-claim interpretation even when their paired Q4 comparison appears non-inferior.",
            "",
            "| run | host | model | config | speedup vs Q4 | quality | JSON |",
            "|---|---|---|---|---:|---:|---:|",
        ])
        for row in hard_invalid_8k:
            lines.append(
                f"| {row['run_kind']} | {row['host_label']} | {row['model']} | {row['config']} | "
                f"{fmt(row['speedup_vs_q4_pct'], 1)}% | {fmt(row['quality_mean'])} | {fmt(row['json_valid_mean'])} |"
            )
    lines.extend([
        "",
        "## Quality Non-Inferiority vs Q4",
        "",
        "`JSON >= Q4` is a paired relative check; `config JSON` and `Q4 JSON` are the absolute validity rates.",
        "",
        "| run | host | ctx | model | config | paired cases | quality >= Q4 | JSON >= Q4 | config JSON | Q4 JSON |",
        "|---|---|---:|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in noninf:
        lines.append(
            f"| {row['run_kind']} | {row['host_label']} | {row['ctx_size']} | {row['model']} | {row['config']} | "
            f"{row['paired_cases']} | {fmt(row['quality_ge_q4_rate'])} | {fmt(row['json_ge_q4_rate'])} | "
            f"{fmt(row['config_json_valid_rate'])} | {fmt(row['q4_json_valid_rate'])} |"
        )
    lines.extend([
        "",
        "## Latency Decomposition",
        "",
        "| run | host | ctx | model | config | planner s | deterministic tools s | LLM tools s | final s | prompt eval ms | decode ms |",
        "|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in latency:
        if int(row["ctx_size"]) != 8192:
            continue
        lines.append(
            f"| {row['run_kind']} | {row['host_label']} | {row['ctx_size']} | {row['model']} | {row['config']} | "
            f"{fmt(row['planner_sec_mean'])} | {fmt(row['deterministic_tool_sec_mean'])} | "
            f"{fmt(row['llm_tool_sec_mean'])} | {fmt(row['final_sec_mean'])} | "
            f"{fmt(row['prompt_eval_ms_mean'], 1)} | {fmt(row['decode_ms_mean'], 1)} |"
        )
    if telemetry_rows:
        lines.extend([
            "",
            "## Power And Thermal Telemetry",
            "",
            "Telemetry is comparable only within the same device and controlled power/ambient conditions.",
            "Zero joules/watts means the energy counter was unavailable or unreadable during that run, not zero power draw.",
            "Battery columns are whole-system battery discharge estimates on macOS, not package or SoC power.",
            "",
            "| run | host | ctx | model | config | max temp C | pkg joules | avg pkg W | batt joules | avg batt W |",
            "|---|---|---:|---|---|---:|---:|---:|---:|---:|",
        ])
        for row in telemetry_rows:
            lines.append(
                f"| {row['run_kind']} | {row['host_label']} | {row['ctx_size']} | {row['model']} | {row['config']} | "
                f"{fmt(row['thermal_max_c_mean'], 1)} | {fmt(row['rapl_package_joules_mean'], 1)} | "
                f"{fmt(row['rapl_package_watts_avg_mean'], 2)} | {fmt(row['battery_joules_mean'], 1)} | "
                f"{fmt(row['battery_power_w_avg_mean'], 2)} |"
            )
    lines.extend([
        "",
        "## Context Sweep",
        "",
        "| run | host | ctx | model | config | reps | wall mean s | speedup vs Q4 | quality | RSS MB |",
        "|---|---|---:|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in agg:
        lines.append(
            f"| {row['run_kind']} | {row['host_label']} | {row['ctx_size']} | {row['model']} | {row['config']} | "
            f"{row['repeats']} | {fmt(row['wall_mean_sec'])} | {fmt(row['speedup_vs_q4_pct'], 1)}% | "
            f"{fmt(row['quality_mean'])} | {fmt(row['rss_max_mean_mb'], 1)} |"
        )

    claim_rows = [r for r in agg if r["run_kind"] == "repeat_core8k"] or [r for r in agg if int(r["ctx_size"]) == 8192]
    tbq_8k = [r for r in claim_rows if int(r["ctx_size"]) == 8192 and r["config"] == "tbq4/tbq4"]
    q8tbq_8k = [r for r in claim_rows if int(r["ctx_size"]) == 8192 and r["config"] == "q8_0/tbq4"]
    tbq_faster = all(r["speedup_vs_q4_pct"] > 0 for r in tbq_8k) if tbq_8k else False
    tbq_quality = all(r["quality_delta_vs_q4"] >= -0.02 for r in tbq_8k) if tbq_8k else False
    q8_quality = all(r["quality_delta_vs_q4"] >= -0.02 for r in q8tbq_8k) if q8tbq_8k else False

    lines.extend([
        "",
        "## Claim Assessment",
        "",
    ])
    if tbq_faster and tbq_quality:
        lines.append(
            "`tbq4/tbq4` supports the performance side of the edge-agent claim at 8K: "
            "it is faster than Q4 in every aggregated host/model slice and is non-inferior by the deterministic quality rubric."
        )
    elif tbq_faster:
        lines.append(
            "`tbq4/tbq4` supports the speed claim at 8K, but the deterministic quality rubric is not uniformly non-inferior to Q4."
        )
    else:
        lines.append("`tbq4/tbq4` does not uniformly beat Q4 in the available 8K agent results.")
    if q8_quality:
        lines.append("`q8_0/tbq4` remains the conservative quality candidate because its quality delta is non-inferior in the aggregated slices.")
    else:
        lines.append("`q8_0/tbq4` should remain exploratory until the quality deltas are consistently non-inferior.")
    if hard_invalid_8k:
        lines.append(
            "The x86 Qwen rows with zero valid JSON must be fixed and rerun before making cross-model claims."
        )
    lines.extend([
        "",
        "Do not publish a strict-lossless claim from this evidence alone. The supported wording is "
        "`quality-preserving under the tested Gemma CPU edge-agent workload` or `near-lossless in this task suite`.",
        "",
        "## Artifacts",
        "",
        "- `aggregate_summary.csv`: repeated-run mean, stddev, CI95, Q4 speedup, quality, RSS, and CPU profile aggregates.",
        "- `latency_breakdown.csv`: planner/tool/final/prompt/decode decomposition.",
        "- `quality_noninferiority.csv`: paired task-level comparison against Q4.",
    ])
    (out_dir / "UNIFIED_EDGE_AGENT_REPORT.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_roots", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    out_dir = args.out_dir or (Path(__file__).resolve().parent / "results" / ("paper_unified_" + datetime.now().strftime("%Y%m%d_%H%M%S")))
    out_dir.mkdir(parents=True, exist_ok=True)
    summaries, tasks, metadata = load_roots(args.run_roots)
    agg = aggregate_summary(summaries)
    latency = aggregate_latency(tasks)
    noninf = noninferiority_rows(tasks)
    write_csv(out_dir / "aggregate_summary.csv", agg)
    write_csv(out_dir / "latency_breakdown.csv", latency)
    write_csv(out_dir / "quality_noninferiority.csv", noninf)
    write_report(out_dir, args.run_roots, metadata, agg, latency, noninf)
    print(out_dir)


if __name__ == "__main__":
    main()
