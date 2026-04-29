#!/usr/bin/env python3
"""Aggregate benchmark results from one or more result directories.

Parses llama-bench output files and produces:
- Speed comparison tables (pp512, tg128 × depths × kv types × models)
- Speedup vs F16 baseline
- CSV export for plotting

Usage:
  aggregate_comprehensive.py <results_dir>
  aggregate_comprehensive.py <output_dir> <results_dir> [<results_dir> ...]

When multiple result directories are provided, later directories override earlier
records on a per-(model, kv, mode, depth) basis. Incomplete reruns are skipped.
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_bench_file(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or "---" in line or "model" in line.lower():
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) < 8:
                continue
            try:
                # When ctk/ctv are f16 (default), those cols are omitted -> 8 cols
                # When ctk/ctv differ from f16 -> 10 cols
                test_col = cols[-2]  # next-to-last is the test
                ts_col = cols[-1]   # last is the t/s value

                m = re.match(r"(pp|tg)(\d+)(?:\s*@\s*d(\d+))?", test_col)
                if not m:
                    continue
                mode = m.group(1)
                tokens = int(m.group(2))
                depth = int(m.group(3)) if m.group(3) else 0

                ts_match = re.match(r"([\d.]+)\s*±\s*([\d.]+)", ts_col)
                if not ts_match:
                    continue
                ts = float(ts_match.group(1))

                records.append({
                    "mode": mode, "tokens": tokens, "depth": depth, "ts": ts,
                })
            except (ValueError, IndexError):
                continue
    return records


def resolve_dirs(argv: list[str]) -> tuple[Path, list[Path]]:
    if len(argv) == 2:
        results_dir = Path(argv[1])
        return results_dir, [results_dir]

    if len(argv) >= 3:
        output_dir = Path(argv[1])
        input_dirs = [Path(arg) for arg in argv[2:]]
        return output_dir, input_dirs

    print(
        f"Usage:\n"
        f"  {argv[0]} <results_dir>\n"
        f"  {argv[0]} <output_dir> <results_dir> [<results_dir> ...]"
    )
    sys.exit(1)


def is_complete_bench_file(path: Path, records: list[dict]) -> bool:
    if not records:
        return False

    with open(path) as f:
        return any(line.startswith("build:") for line in f)


def main():
    output_dir, input_dirs = resolve_dirs(sys.argv)
    if not input_dirs:
        print("Error: no input directories provided")
        sys.exit(1)

    for results_dir in input_dirs:
        if not results_dir.is_dir():
            print(f"Error: {results_dir} is not a directory")
            sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse all files: format is "{model}_{kv}.txt"
    data = defaultdict(dict)  # data[model][(kv, mode, depth)] = ts
    for results_dir in input_dirs:
        for bench_file in sorted(results_dir.glob("*.txt")):
            name = bench_file.stem
            # Parse model_kv from filename
            # e.g., "gilda_llama_3.2b_tbq4" -> model="gilda_llama_3.2b", kv="tbq4"
            # Try matching known KV types at the end
            for kv in ["tbq4", "tbq3", "tbq2", "f16", "q8_0", "q4_0"]:
                if name.endswith("_" + kv):
                    model = name[:-len("_" + kv)]
                    break
            else:
                print(f"Skip unrecognized: {name}")
                continue

            records = parse_bench_file(bench_file)
            if not is_complete_bench_file(bench_file, records):
                print(f"Skip incomplete: {bench_file}")
                continue

            for r in records:
                data[model][(kv, r["mode"], r["depth"])] = r["ts"]

    models = sorted(data.keys())
    kv_types = ["f16", "q8_0", "q4_0", "tbq4", "tbq3", "tbq2"]
    depths = [0, 2048, 4096, 8192]

    # Generate speed comparison tables
    for mode in ["tg", "pp"]:
        n_tokens = 128 if mode == "tg" else 512
        print(f"\n## {mode.upper()}{n_tokens} (t/s)\n")
        for model in models:
            print(f"### {model}\n")
            header = "| KV Type |" + " | ".join(f"d={d}" for d in depths) + " |"
            sep = "|---|" + "|".join("---:" for _ in depths) + "|"
            print(header)
            print(sep)
            for kv in kv_types:
                cells = []
                for d in depths:
                    ts = data[model].get((kv, mode, d))
                    cells.append(f"{ts:.2f}" if ts is not None else "—")
                print(f"| {kv} | " + " | ".join(cells) + " |")
            print()

    # Speedup vs F16 baseline (tg)
    print("\n## Speedup vs F16 baseline (tg128)\n")
    for model in models:
        print(f"### {model}\n")
        header = "| KV Type |" + " | ".join(f"d={d}" for d in depths) + " |"
        sep = "|---|" + "|".join("---:" for _ in depths) + "|"
        print(header)
        print(sep)
        for kv in kv_types:
            cells = []
            for d in depths:
                ts = data[model].get((kv, "tg", d))
                f16_ts = data[model].get(("f16", "tg", d))
                if ts is not None and f16_ts is not None and f16_ts > 0:
                    sp = (ts / f16_ts - 1) * 100
                    mark = "**" if sp > 5 else ""
                    cells.append(f"{mark}{sp:+.1f}%{mark}")
                else:
                    cells.append("—")
            print(f"| {kv} | " + " | ".join(cells) + " |")
        print()

    # CSV export
    csv_path = output_dir / "all_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "kv_type", "mode", "depth", "t_per_s"])
        for model in models:
            for (kv, mode, depth), ts in sorted(data[model].items()):
                w.writerow([model, kv, mode, depth, f"{ts:.3f}"])
    print(f"\nCSV: {csv_path}")


if __name__ == "__main__":
    main()
