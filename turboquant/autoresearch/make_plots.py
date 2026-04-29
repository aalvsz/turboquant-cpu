#!/usr/bin/env python3
"""Generate plots from one or more benchmark result directories.

Usage:
  python make_plots.py <results_dir>
  python make_plots.py <output_dir> <results_dir> [<results_dir> ...]

Produces:
  - speedup_vs_depth.png — curves of speedup vs context depth per KV type
  - throughput_vs_depth.png — absolute t/s curves
  - memory_footprint.png — bar chart of memory savings

When multiple result directories are provided, later directories override earlier
records on a per-(model, kv, mode, depth) basis. Incomplete reruns are skipped.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = None
        ImageDraw = None
        ImageFont = None
        print("matplotlib and PIL not available; skipping plot generation")
    else:
        print("matplotlib not available; using PIL fallback")


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
                test_col = cols[-2]
                ts_col = cols[-1]

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
                records.append({"mode": mode, "depth": depth, "ts": ts})
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


def load_font(size: int):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def color_rgb(name: str) -> tuple[int, int, int]:
    palette = {
        "black": (28, 32, 37),
        "blue": (38, 70, 83),
        "cyan": (42, 157, 143),
        "red": (231, 111, 81),
        "orange": (244, 162, 97),
        "magenta": (161, 103, 173),
    }
    return palette[name]


def draw_line_plot_pil(output_path: Path, data: dict, models: list[str], kv_types: list[str], depths: list[int], colors: dict[str, str], ylabel: str, speedup: bool = False) -> None:
    if not Image:
        return

    panel_w = 520
    panel_h = 420
    outer_pad = 28
    top_pad = 54
    left_pad = 54
    bottom_pad = 48
    right_pad = 16
    legend_w = 112
    width = outer_pad * 2 + len(models) * panel_w
    height = outer_pad * 2 + panel_h

    image = Image.new("RGB", (width, height), (248, 246, 241))
    draw = ImageDraw.Draw(image)
    title_font = load_font(18)
    label_font = load_font(14)
    tick_font = load_font(12)

    for panel_idx, model in enumerate(models):
        panel_x0 = outer_pad + panel_idx * panel_w
        plot_x0 = panel_x0 + left_pad
        plot_y0 = outer_pad + top_pad
        plot_x1 = panel_x0 + panel_w - right_pad - legend_w
        plot_y1 = outer_pad + panel_h - bottom_pad

        panel_values = []
        for kv in kv_types:
            for d in depths:
                if speedup:
                    ts = data[model].get((kv, "tg", d))
                    f16_ts = data[model].get(("f16", "tg", d))
                    if kv != "f16" and ts is not None and f16_ts is not None and f16_ts > 0:
                        panel_values.append((ts / f16_ts - 1) * 100.0)
                else:
                    ts = data[model].get((kv, "tg", d))
                    if ts is not None:
                        panel_values.append(ts)

        if not panel_values:
            continue

        y_min = min(panel_values)
        y_max = max(panel_values)
        if speedup:
            y_min = min(y_min, 0.0)
            y_max = max(y_max, 0.0)
        else:
            y_min = 0.0

        if y_max <= y_min:
            y_max = y_min + 1.0
        else:
            span = y_max - y_min
            y_min -= span * (0.08 if speedup else 0.0)
            y_max += span * 0.10

        def x_to_px(depth: int) -> int:
            frac = 0.0 if len(depths) == 1 else depths.index(depth) / (len(depths) - 1)
            return int(plot_x0 + frac * (plot_x1 - plot_x0))

        def y_to_px(value: float) -> int:
            frac = (value - y_min) / (y_max - y_min)
            return int(plot_y1 - frac * (plot_y1 - plot_y0))

        draw.text((panel_x0 + left_pad, outer_pad + 8), model, font=title_font, fill=(28, 32, 37))
        draw.text((panel_x0 + left_pad, outer_pad + 28), ylabel, font=label_font, fill=(89, 96, 105))

        for step in range(5):
            frac = step / 4
            y_val = y_min + (y_max - y_min) * frac
            y_px = int(plot_y1 - frac * (plot_y1 - plot_y0))
            draw.line((plot_x0, y_px, plot_x1, y_px), fill=(224, 221, 214), width=1)
            label = f"{y_val:.1f}" if abs(y_val) < 100 else f"{y_val:.0f}"
            bbox = draw.textbbox((0, 0), label, font=tick_font)
            draw.text((plot_x0 - (bbox[2] - bbox[0]) - 8, y_px - 7), label, font=tick_font, fill=(89, 96, 105))

        if speedup and y_min < 0.0 < y_max:
            zero_y = y_to_px(0.0)
            draw.line((plot_x0, zero_y, plot_x1, zero_y), fill=(110, 110, 110), width=2)

        draw.line((plot_x0, plot_y0, plot_x0, plot_y1), fill=(60, 65, 72), width=2)
        draw.line((plot_x0, plot_y1, plot_x1, plot_y1), fill=(60, 65, 72), width=2)

        for depth in depths:
            x_px = x_to_px(depth)
            draw.line((x_px, plot_y1, x_px, plot_y1 + 5), fill=(60, 65, 72), width=1)
            label = str(depth)
            bbox = draw.textbbox((0, 0), label, font=tick_font)
            draw.text((x_px - (bbox[2] - bbox[0]) / 2, plot_y1 + 8), label, font=tick_font, fill=(89, 96, 105))

        legend_x = plot_x1 + 16
        legend_y = plot_y0 + 8

        for kv in kv_types:
            if speedup and kv == "f16":
                continue
            points = []
            for d in depths:
                if speedup:
                    ts = data[model].get((kv, "tg", d))
                    f16_ts = data[model].get(("f16", "tg", d))
                    if ts is None or f16_ts is None or f16_ts <= 0:
                        continue
                    value = (ts / f16_ts - 1) * 100.0
                else:
                    value = data[model].get((kv, "tg", d))
                    if value is None:
                        continue
                points.append((x_to_px(d), y_to_px(value)))

            if len(points) >= 2:
                draw.line(points, fill=color_rgb(colors[kv]), width=3 if kv.startswith("tbq") else 2)
            for x_px, y_px in points:
                draw.ellipse((x_px - 3, y_px - 3, x_px + 3, y_px + 3), fill=color_rgb(colors[kv]))

            draw.line((legend_x, legend_y + 7, legend_x + 16, legend_y + 7), fill=color_rgb(colors[kv]), width=3 if kv.startswith("tbq") else 2)
            draw.text((legend_x + 22, legend_y), kv, font=label_font, fill=(28, 32, 37))
            legend_y += 22

    image.save(output_path)
    print(f"Saved: {output_path}")


def draw_memory_plot_pil(output_path: Path, mem_per_val: dict[str, float], colors: dict[str, str]) -> None:
    if not Image:
        return

    width, height = 860, 420
    image = Image.new("RGB", (width, height), (248, 246, 241))
    draw = ImageDraw.Draw(image)
    title_font = load_font(20)
    label_font = load_font(14)
    tick_font = load_font(12)

    plot_x0, plot_y0 = 72, 76
    plot_x1, plot_y1 = width - 32, height - 60
    max_y = max(mem_per_val.values()) * 1.15

    draw.text((plot_x0, 24), "Memory footprint of KV cache quantization schemes", font=title_font, fill=(28, 32, 37))
    draw.text((plot_x0, 48), "Bytes per KV value", font=label_font, fill=(89, 96, 105))

    for step in range(5):
        frac = step / 4
        y_val = max_y * frac
        y_px = int(plot_y1 - frac * (plot_y1 - plot_y0))
        draw.line((plot_x0, y_px, plot_x1, y_px), fill=(224, 221, 214), width=1)
        label = f"{y_val:.2f}"
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((plot_x0 - (bbox[2] - bbox[0]) - 8, y_px - 7), label, font=tick_font, fill=(89, 96, 105))

    draw.line((plot_x0, plot_y0, plot_x0, plot_y1), fill=(60, 65, 72), width=2)
    draw.line((plot_x0, plot_y1, plot_x1, plot_y1), fill=(60, 65, 72), width=2)

    keys = list(mem_per_val.keys())
    bar_gap = 18
    slot_w = (plot_x1 - plot_x0 - bar_gap * (len(keys) - 1)) / len(keys)
    for idx, key in enumerate(keys):
        x0 = int(plot_x0 + idx * (slot_w + bar_gap))
        x1 = int(x0 + slot_w)
        bar_h = (mem_per_val[key] / max_y) * (plot_y1 - plot_y0)
        y0 = int(plot_y1 - bar_h)
        draw.rectangle((x0, y0, x1, plot_y1), fill=color_rgb(colors[key]))
        label = f"{mem_per_val[key]:.3f}"
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((x0 + (slot_w - (bbox[2] - bbox[0])) / 2, y0 - 18), label, font=tick_font, fill=(28, 32, 37))
        kbbox = draw.textbbox((0, 0), key, font=label_font)
        draw.text((x0 + (slot_w - (kbbox[2] - kbbox[0])) / 2, plot_y1 + 10), key, font=label_font, fill=(28, 32, 37))

    image.save(output_path)
    print(f"Saved: {output_path}")


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

    data = defaultdict(dict)  # data[model][(kv, mode, depth)] = ts
    for results_dir in input_dirs:
        for bench_file in sorted(results_dir.glob("*.txt")):
            name = bench_file.stem
            for kv in ["tbq4", "tbq3", "tbq2", "f16", "q8_0", "q4_0"]:
                if name.endswith("_" + kv):
                    model = name[:-len("_" + kv)]
                    break
            else:
                continue
            records = parse_bench_file(bench_file)
            if not is_complete_bench_file(bench_file, records):
                print(f"Skip incomplete: {bench_file}")
                continue
            for r in records:
                data[model][(kv, r["mode"], r["depth"])] = r["ts"]

    if not plt and not Image:
        return

    models = sorted(data.keys())
    kv_types = ["f16", "q8_0", "q4_0", "tbq4", "tbq3", "tbq2"]
    depths = [0, 2048, 4096, 8192]
    colors = {"f16": "black", "q8_0": "blue", "q4_0": "cyan",
              "tbq4": "red", "tbq3": "orange", "tbq2": "magenta"}

    mem_per_val = {"f16": 2.0, "q8_0": 1.0625, "q4_0": 0.5625,
                   "tbq4": 0.5625, "tbq3": 0.4375, "tbq2": 0.3125}

    if plt:
        # Plot 1: tg throughput vs depth per model
        fig, axes = plt.subplots(1, len(models), figsize=(6*len(models), 5))
        if len(models) == 1:
            axes = [axes]
        for ax, model in zip(axes, models):
            for kv in kv_types:
                xs, ys = [], []
                for d in depths:
                    if (kv, "tg", d) in data[model]:
                        xs.append(d)
                        ys.append(data[model][(kv, "tg", d)])
                if xs:
                    ax.plot(xs, ys, marker="o", label=kv, color=colors[kv],
                            linewidth=2 if kv.startswith("tbq") else 1.5)
            ax.set_xlabel("Context depth")
            ax.set_ylabel("Throughput (tg128, t/s)")
            ax.set_title(model)
            ax.legend()
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "throughput_vs_depth.png", dpi=120)
        print(f"Saved: {output_dir / 'throughput_vs_depth.png'}")

        # Plot 2: speedup vs F16 (tg)
        fig, axes = plt.subplots(1, len(models), figsize=(6*len(models), 5))
        if len(models) == 1:
            axes = [axes]
        for ax, model in zip(axes, models):
            for kv in kv_types:
                if kv == "f16":
                    continue
                xs, ys = [], []
                for d in depths:
                    ts = data[model].get((kv, "tg", d))
                    f16_ts = data[model].get(("f16", "tg", d))
                    if ts is not None and f16_ts is not None and f16_ts > 0:
                        xs.append(d)
                        ys.append((ts / f16_ts - 1) * 100)
                if xs:
                    ax.plot(xs, ys, marker="o", label=kv, color=colors[kv],
                            linewidth=2 if kv.startswith("tbq") else 1.5)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xlabel("Context depth")
            ax.set_ylabel("Speedup vs F16 (%)")
            ax.set_title(model)
            ax.legend()
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "speedup_vs_depth.png", dpi=120)
        print(f"Saved: {output_dir / 'speedup_vs_depth.png'}")

        fig, ax = plt.subplots(figsize=(8, 4))
        xs = list(mem_per_val.keys())
        ys = list(mem_per_val.values())
        bars = ax.bar(xs, ys, color=[colors[k] for k in xs])
        ax.set_ylabel("Bytes per KV value")
        ax.set_title("Memory footprint of KV cache quantization schemes")
        ax.grid(True, axis="y", alpha=0.3)
        for bar, y in zip(bars, ys):
            ax.text(bar.get_x() + bar.get_width()/2, y, f"{y:.3f}", ha="center", va="bottom")
        plt.tight_layout()
        plt.savefig(output_dir / "memory_footprint.png", dpi=120)
        print(f"Saved: {output_dir / 'memory_footprint.png'}")
    else:
        draw_line_plot_pil(output_dir / "throughput_vs_depth.png", data, models, kv_types, depths, colors, "Throughput (tg128, t/s)")
        draw_line_plot_pil(output_dir / "speedup_vs_depth.png", data, models, kv_types, depths, colors, "Speedup vs F16 (%)", speedup=True)
        draw_memory_plot_pil(output_dir / "memory_footprint.png", mem_per_val, colors)


if __name__ == "__main__":
    main()
