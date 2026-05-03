#!/usr/bin/env python3
"""Repair Linux RAPL energy summaries when energy_uj wraps during long runs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_MAX_RANGE_UJ = 262_143_328_850


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: Iterable[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fnum(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def energy_joules(samples: List[Tuple[float, float]], max_range_uj: float) -> float:
    if len(samples) < 2:
        return 0.0
    total_uj = 0.0
    prev = samples[0][1]
    for _elapsed, cur in samples[1:]:
        delta = cur - prev
        if delta < 0 and max_range_uj > 0:
            delta += max_range_uj
        if delta > 0:
            total_uj += delta
        prev = cur
    return total_uj / 1_000_000.0


def resolve_raw_dir(run_root: Path, raw_dir_value: str) -> Optional[Path]:
    if not raw_dir_value:
        return None
    raw = Path(raw_dir_value)
    if raw.exists():
        return raw
    candidate = run_root / raw.name
    if candidate.exists():
        return candidate
    candidate = run_root / "raw" / raw.name
    if candidate.exists():
        return candidate
    return None


def repair_raw_dir(raw_dir: Path, max_range_uj: float) -> Tuple[float, float, int]:
    samples_path = raw_dir / "profiler_samples.csv"
    rows = read_csv(samples_path)
    samples = [
        (fnum(row.get("elapsed_sec")), fnum(row.get("rapl_package_energy_uj")))
        for row in rows
        if row.get("rapl_package_energy_uj") not in (None, "")
    ]
    joules = energy_joules(samples, max_range_uj)
    watts = 0.0
    if len(samples) >= 2:
        duration = max(samples[-1][0] - samples[0][0], 0.0)
        watts = joules / duration if duration else 0.0

    profile_path = raw_dir / "profile_summary.json"
    profile: Dict[str, Any] = {}
    if profile_path.exists():
        profile = json.loads(profile_path.read_text())
    profile["rapl_package_joules"] = joules
    profile["rapl_package_watts_avg"] = watts
    profile_path.write_text(json.dumps(profile, indent=2) + "\n")
    return joules, watts, len(samples)


def repair_run_root(run_root: Path, max_range_uj: float) -> int:
    summary_path = run_root / "summary.csv"
    rows = read_csv(summary_path)
    if not rows:
        return 0
    with summary_path.open(newline="") as f:
        fieldnames = list(csv.DictReader(f).fieldnames or [])

    changed = 0
    for row in rows:
        raw_dir = resolve_raw_dir(run_root, row.get("raw_dir", ""))
        if not raw_dir:
            continue
        joules, watts, sample_count = repair_raw_dir(raw_dir, max_range_uj)
        if sample_count < 2:
            continue
        old_joules = fnum(row.get("rapl_package_joules"))
        old_watts = fnum(row.get("rapl_package_watts_avg"))
        row["rapl_package_joules"] = f"{joules:.6f}"
        row["rapl_package_watts_avg"] = f"{watts:.6f}"
        if abs(old_joules - joules) > 1e-6 or abs(old_watts - watts) > 1e-6:
            changed += 1

    write_csv(summary_path, rows, fieldnames)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--max-range-uj", type=float, default=DEFAULT_MAX_RANGE_UJ)
    args = parser.parse_args()
    changed = repair_run_root(args.run_root, args.max_range_uj)
    print(f"repaired_rows={changed}")


if __name__ == "__main__":
    main()
