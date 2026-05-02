#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def pct(a, b):
    if a is None or b in (None, 0):
        return None
    return (a / b - 1.0) * 100.0


def summarize_host(root):
    root = Path(root)
    speed = read_csv(root / "speed" / "speed_results.csv")
    sustained = read_csv(root / "sustained" / "sustained_results.csv")
    ppl = read_csv(root / "ppl" / "ppl_results.csv")
    judge = read_csv(root / "quality" / "heuristic_judge.csv")

    lines = [f"# Fresh Findings: {root.name}", ""]
    lines.append("## 8K Decode Speed")
    lines.append("")
    lines.append("| model | threads | config | tok/s | vs f16 | vs q8 | vs q4 |")
    lines.append("|---|---:|---|---:|---:|---:|---:|")
    speed_8k = [r for r in speed if str(r.get("n_depth")) == "8192" and r.get("returncode") == "0"]
    by_mt = {}
    for r in speed_8k:
        by_mt.setdefault((r["model"], r["threads"]), {})[r["config"]] = fnum(r.get("avg_ts"))
    for (model, threads), configs in sorted(by_mt.items()):
        for cfg in ["f16/f16", "q8_0/q8_0", "q4_0/q4_0", "tbq4/tbq4", "q8_0/tbq4"]:
            val = configs.get(cfg)
            if val is None:
                continue
            lines.append(
                f"| {model} | {threads} | {cfg} | {val:.3f} | "
                f"{fmt_pct(pct(val, configs.get('f16/f16')))} | "
                f"{fmt_pct(pct(val, configs.get('q8_0/q8_0')))} | "
                f"{fmt_pct(pct(val, configs.get('q4_0/q4_0')))} |"
            )

    lines.append("")
    lines.append("## Perplexity")
    lines.append("")
    lines.append("| model | config | ppl | delta vs f16 | returncode |")
    lines.append("|---|---|---:|---:|---:|")
    by_model_ppl = {}
    for r in ppl:
        by_model_ppl.setdefault(r["model"], {})[r["config"]] = fnum(r.get("ppl"))
    for r in sorted(ppl, key=lambda x: (x["model"], x["config"])):
        p = fnum(r.get("ppl"))
        base = by_model_ppl.get(r["model"], {}).get("f16/f16")
        lines.append(f"| {r['model']} | {r['config']} | {fmt_num(p)} | {fmt_pct(pct(p, base))} | {r.get('returncode')} |")

    lines.append("")
    lines.append("## Deterministic Prompt Judge")
    lines.append("")
    lines.append("| model | setting | n | mean score | degenerate rate |")
    lines.append("|---|---|---:|---:|---:|")
    groups = {}
    for r in judge:
        groups.setdefault((r["model"], r["setting"]), []).append(r)
    for key in sorted(groups):
        vals = groups[key]
        scores = [fnum(v.get("heuristic_score_0_5")) for v in vals]
        deg = [fnum(v.get("degenerate")) for v in vals]
        lines.append(f"| {key[0]} | {key[1]} | {len(vals)} | {mean(scores):.3f} | {mean(deg):.3f} |")

    lines.append("")
    lines.append("## Sustained 8K Decode")
    lines.append("")
    lines.append("| model | threads | config | tok/s | max RSS MB | energy J |")
    lines.append("|---|---:|---|---:|---:|---:|")
    for r in sustained:
        rss = fnum(r.get("max_rss_kb"))
        e = fnum(r.get("energy_uj_delta"))
        lines.append(
            f"| {r['model']} | {r['threads']} | {r['config']} | "
            f"{fmt_num(fnum(r.get('avg_ts')))} | {fmt_num(rss / 1024 if rss else None)} | "
            f"{fmt_num(e / 1_000_000 if e else None)} |"
        )

    (root / "FINDINGS.md").write_text("\n".join(lines) + "\n")


def fmt_num(v):
    return "n/a" if v is None else f"{v:.3f}"


def fmt_pct(v):
    return "n/a" if v is None else f"{v:+.1f}%"


def merge_roots(out_root, host_roots):
    out_root = Path(out_root)
    lines = ["# Cross-Host Fresh TurboQuant Findings", ""]
    for hr in host_roots:
        summarize_host(hr)
        findings = Path(hr) / "FINDINGS.md"
        if findings.exists():
            lines.append(findings.read_text())
            lines.append("")
    lines.append("## Interpretation Scaffold")
    lines.append("")
    lines.append("- Treat `q8_0/tbq4` as the primary deployment candidate if it preserves PPL and prompt scores while improving or staying close to F16/Q8 sustained speed.")
    lines.append("- Treat `tbq4/tbq4` as model-dependent unless it clears speed, PPL, and prompt quality on both Gemma and Qwen.")
    lines.append("- Do not call the technique lossless unless outputs and PPL are indistinguishable within noise across the full prompt set and both model families.")
    (out_root / "CROSS_HOST_FINDINGS.md").write_text("\n".join(lines) + "\n")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out-root", required=True)
    p.add_argument("--host-root", action="append", required=True)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    merge_roots(args.out_root, args.host_root)
