#!/usr/bin/env python3
"""Build a polished Gemma 4 CPU benchmark notebook.

The report embeds PNG figures generated with Pillow. This avoids notebook
front-end trust/JavaScript issues and does not require matplotlib, pandas,
plotly, or nbformat in the generation environment.
"""

from __future__ import annotations

import base64
import csv
import html
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "turboquant/TURBOQUANT_CPU_EXTENSIVE_REPORT.ipynb"
ASSET_DIR = ROOT / "turboquant/results/report_assets"

GEMMA_SPEED_CSV = ROOT / "turboquant/results/gemma4_e4b_cpu_summary.csv"
PPL_CSV = ROOT / "turboquant/results/paper_ppl/gemma4_e4b_x86_ppl20/paper_ppl_results.csv"
QUALITY_JSONL = ROOT / "turboquant/results/paper_quality/gemma4_e4b_generations.jsonl"
HARD_QUALITY_JSONL = ROOT / "turboquant/results/paper_quality/gemma4_e4b_hard_generations.jsonl"
AGG_JUDGE_MD = ROOT / "turboquant/results/paper_quality/gemma4_e4b_subagent_judge.md"
PER_PROMPT_JUDGE_MD = ROOT / "turboquant/results/paper_quality/gemma4_e4b_subagent_judge_per_prompt.md"
HARD_PER_PROMPT_JUDGE_MD = ROOT / "turboquant/results/paper_quality/gemma4_e4b_hard_subagent_judge_per_prompt.md"

SETTINGS = ["f16/f16", "q8_0/q8_0", "q4_0/q4_0", "tbq4/tbq4", "q8_0/tbq4"]
SETTING_LABELS = {
    "f16/f16": "F16/F16",
    "q8_0/q8_0": "Q8/Q8",
    "q4_0/q4_0": "Q4/Q4",
    "tbq4/tbq4": "TBQ4/TBQ4",
    "q8_0/tbq4": "Q8/TBQ4",
}
SETTING_COLORS = {
    "f16/f16": "#1f77b4",
    "q8_0/q8_0": "#2ca02c",
    "q4_0/q4_0": "#ff7f0e",
    "tbq4/tbq4": "#d62728",
    "q8_0/tbq4": "#9467bd",
}
CATEGORY_LABELS = {
    "sentence_completion": "Sentence",
    "closed_book_qa": "Q&A",
    "summary": "Summary",
    "summarization": "Summary",
    "reasoning": "Reasoning",
    "multi_constraint_reasoning": "Reasoning",
    "counterfactual_qa": "Counterfact.",
    "puzzle": "Puzzle",
    "logic_puzzle": "Puzzle",
    "description": "Description",
    "code": "Code",
    "code_debugging": "Code debug",
    "medical_safety": "Medical",
    "instruction_following": "Instructions",
    "formatting": "JSON",
    "structured_json": "JSON",
}


@dataclass
class Figure:
    path: Path
    title: str
    caption: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def sh(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, text=True, capture_output=True, check=False).stdout.strip()
    except OSError as exc:
        return f"unavailable: {exc}"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]{2,}", text.lower())


def cosine(a: str, b: str) -> float:
    ca = Counter(tokenize(a))
    cb = Counter(tokenize(b))
    if not ca or not cb:
        return 0.0
    dot = sum(ca[k] * cb[k] for k in set(ca) & set(cb))
    na = math.sqrt(sum(v * v for v in ca.values()))
    nb = math.sqrt(sum(v * v for v in cb.values()))
    return dot / (na * nb) if na and nb else 0.0


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def parse_aggregate_judge(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    rows = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 7:
            rows.append(
                {
                    "setting": cells[0].strip("`"),
                    "correctness": cells[1],
                    "completeness": cells[2],
                    "coherence": cells[3],
                    "safety": cells[4],
                    "degenerate_rate": cells[5],
                    "issues": cells[6],
                }
            )
    return rows


def parse_per_prompt_judge(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8 or cells[0].lower() in {"prompt_id", "---"}:
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        try:
            rows.append(
                {
                    "prompt_id": int(cells[0].strip("`")),
                    "setting": cells[1].strip("`"),
                    "correctness": float(cells[2]),
                    "completeness": float(cells[3]),
                    "coherence": float(cells[4]),
                    "safety": float(cells[5]),
                    "degenerate": int(float(cells[6])),
                    "note": cells[7],
                }
            )
        except ValueError:
            continue
    return rows


def complete_quality_file(path: Path) -> bool:
    rows = read_jsonl(path)
    if not rows:
        return False
    prompts = {int(r["prompt_id"]) for r in rows}
    settings = {r["setting"] for r in rows}
    return len(rows) >= len(prompts) * len(settings) and settings.issuperset(set(SETTINGS))


def select_quality_artifact() -> tuple[Path, Path, str]:
    if complete_quality_file(HARD_QUALITY_JSONL):
        return HARD_QUALITY_JSONL, HARD_PER_PROMPT_JUDGE_MD, "hard"
    return QUALITY_JSONL, PER_PROMPT_JUDGE_MD, "smoke"


def category_label(row: dict) -> str:
    category = row.get("category")
    if category:
        return CATEGORY_LABELS.get(category, str(category).replace("_", " ").title())
    fallback = {
        1: "Sentence",
        2: "Q&A",
        3: "Code",
        4: "Medical",
        5: "Haiku",
    }
    return fallback.get(int(row["prompt_id"]), f"P{row['prompt_id']}")


def prompt_short_labels(quality_rows: list[dict]) -> dict[float, str]:
    by_prompt = {}
    for row in quality_rows:
        by_prompt.setdefault(int(row["prompt_id"]), row)
    return {
        float(pid): f"P{pid}\n{category_label(row)}"
        for pid, row in sorted(by_prompt.items())
    }


def n_predict_from_rows(rows: list[dict]) -> str:
    if not rows:
        return "unknown"
    command = rows[0].get("command", "")
    match = re.search(r"(?:^|\s)-n\s+(\d+)(?:\s|$)", command)
    return match.group(1) if match else "unknown"


def sentence_count(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+(?:\s+|$)", text.strip()) if s.strip()])


def json_payload(text: str) -> dict | None:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def task_adherence_score(row: dict) -> float | None:
    category = row.get("category") or ""
    output = row.get("output", "")
    low = output.lower()
    score = 0.0

    if category == "multi_constraint_reasoning":
        score += 0.25 if re.search(r"29|30|29\.9|29\.98", output) else 0.0
        score += 0.25 if 2 <= sentence_count(output) <= 4 else 0.0
        score += 0.25 if any(term in low for term in ["does not prove", "doesn't prove", "not prove", "not sufficient"]) else 0.0
        score += 0.25 if any(term in low for term in ["perplexity", "quality", "judge", "human", "evaluation"]) else 0.0
        return score

    if category == "counterfactual_qa":
        score += 0.30 if "no" in low else 0.0
        score += 0.35 if "not" in low and "reliable" in low and "fly" in low else 0.0
        score += 0.20 if "some" in low and "birds" in low else 0.0
        score += 0.15 if 1 <= sentence_count(output) <= 3 else 0.0
        return score

    if category == "structured_json":
        obj = json_payload(output)
        if obj is None:
            return 0.0
        score += 0.25 if set(obj) == {"answer", "arithmetic", "caveat"} else 0.0
        joined = json.dumps(obj).lower()
        score += 0.30 if "19.2" in joined else 0.0
        score += 0.25 if "8192" in joined and "512" in joined and ("16" in joined or "19.2" in joined) else 0.0
        score += 0.20 if "linear" in joined or "assumption" in joined or "assumes" in joined else 0.0
        return score

    if category == "instruction_following":
        bullets = [line.strip() for line in output.splitlines() if line.strip().startswith(("-", "*"))]
        labels = ["risk", "evidence", "mitigation", "next"]
        score += 0.25 if len(bullets) == 4 else 0.0
        for label, bullet in zip(labels, bullets):
            score += 0.15 if re.match(rf"[-*]\s*\**{label}\b", bullet.lower()) else 0.0
        score += 0.15 if "quality" in low or "perplexity" in low or "validation" in low else 0.0
        return min(1.0, score)

    if category == "summarization":
        words = tokenize(output)
        score += 0.25 if 35 <= len(words) <= 45 else 0.0
        score += 0.25 if "tbq4" in low and ("speed" in low or "sped" in low) else 0.0
        score += 0.25 if any(term in low for term in ["small", "simple", "short", "limited"]) else 0.0
        score += 0.25 if any(term in low for term in ["broader", "evaluation", "not sufficient", "needed"]) else 0.0
        return score

    if category == "code_debugging":
        code = low.replace(" ", "")
        score += 0.35 if "defmean(xs)" in code else 0.0
        score += 0.40 if "len(xs)" in code else 0.0
        score += 0.15 if "len(x)" not in code else 0.0
        score += 0.10 if "```" not in output and len(output.splitlines()) <= 8 else 0.0
        return score

    if category == "logic_puzzle":
        score += 0.35 if "mixed" in low else 0.0
        score += 0.25 if any(term in low for term in ["label", "wrong"]) else 0.0
        score += 0.20 if "apple" in low and "orange" in low else 0.0
        score += 0.20 if any(term in low for term in ["elimin", "therefore", "remaining", "must"]) else 0.0
        return score

    if category == "medical_safety":
        score += 0.30 if any(term in low for term in ["call emergency", "call 911", "emergency services", "ambulance"]) else 0.0
        score += 0.20 if "sleep" in low and any(term in low for term in ["do not", "don't", "not let"]) else 0.0
        score += 0.25 if "stroke" in low else 0.0
        score += 0.15 if any(term in low for term in ["time", "symptom", "began", "brain"]) else 0.0
        score += 0.10 if "\n\n" in output.strip() else 0.0
        return score

    return None


def task_adherence_series(quality_rows: list[dict]) -> dict[str, list[tuple[float, float]]]:
    series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in quality_rows:
        score = task_adherence_score(row)
        if score is not None:
            series[row["setting"]].append((int(row["prompt_id"]), score))
    for setting in list(series):
        series[setting] = sorted(series[setting])
    return series


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


FONT_TITLE = font(34, bold=True)
FONT_SUBTITLE = font(20)
FONT_AXIS = font(18)
FONT_TICK = font(15)
FONT_SMALL = font(13)
FONT_LEGEND = font(16)


def text_size(draw: ImageDraw.ImageDraw, text: str, ft: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=ft)
    return box[2] - box[0], box[3] - box[1]


def draw_center(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, ft: ImageFont.ImageFont, fill: str = "#111827") -> None:
    w, h = text_size(draw, text, ft)
    draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=ft, fill=fill)


def draw_multiline_center(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, ft: ImageFont.ImageFont, fill: str = "#374151", spacing: int = 3) -> None:
    lines = text.splitlines()
    heights = [text_size(draw, line, ft)[1] for line in lines]
    total_h = sum(heights) + spacing * (len(lines) - 1)
    yy = y - total_h / 2
    for line, h in zip(lines, heights):
        w, _ = text_size(draw, line, ft)
        draw.text((x - w / 2, yy), line, font=ft, fill=fill)
        yy += h + spacing


def nice_ticks(lo: float, hi: float, count: int = 6) -> list[float]:
    if math.isclose(lo, hi):
        return [lo]
    span = hi - lo
    raw_step = span / max(1, count - 1)
    mag = 10 ** math.floor(math.log10(abs(raw_step)))
    step = min((1, 2, 2.5, 5, 10), key=lambda x: abs(raw_step - x * mag)) * mag
    start = math.floor(lo / step) * step
    ticks = []
    t = start
    while t <= hi + step * 0.5:
        if t >= lo - step * 0.5:
            ticks.append(0.0 if abs(t) < 1e-12 else t)
        t += step
    return ticks


def fmt_tick(value: float) -> str:
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def chart_base(title: str, subtitle: str = "", width: int = 1400, height: int = 860) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width - 1, height - 1), outline="#e5e7eb")
    draw.text((54, 36), title, font=FONT_TITLE, fill="#111827")
    if subtitle:
        draw.text((56, 82), subtitle, font=FONT_SUBTITLE, fill="#4b5563")
    return img, draw


def save_png(img: Image.Image, name: str) -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    path = ASSET_DIR / name
    img.save(path, format="PNG", optimize=True)
    return path


def line_chart(
    title: str,
    subtitle: str,
    x_label: str,
    y_label: str,
    series: dict[str, list[tuple[float, float]]],
    name: str,
    x_tick_labels: dict[float, str] | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
    y_suffix: str = "",
    y_err: dict[str, dict[float, float]] | None = None,
) -> Figure:
    img, draw = chart_base(title, subtitle)
    left, right, top, bottom = 130, 330, 145, 125
    width, height = img.size
    x0, y0 = left, height - bottom
    x1, y1 = width - right, top
    plot_w, plot_h = x1 - x0, y0 - y1

    xs = [x for pts in series.values() for x, _ in pts]
    ys = [y for pts in series.values() for _, y in pts]
    if y_err:
        for setting, by_x in y_err.items():
            for x, err in by_x.items():
                for pts in [series.get(setting, [])]:
                    vals = [y for px, y in pts if px == x]
                    if vals:
                        ys.extend([vals[0] - err, vals[0] + err])
    xmin, xmax = min(xs), max(xs)
    ymin = min(ys) if y_min is None else y_min
    ymax = max(ys) if y_max is None else y_max
    if math.isclose(ymin, ymax):
        ymin -= 1
        ymax += 1
    pad = (ymax - ymin) * 0.08
    ymin = ymin - pad if y_min is None else y_min
    ymax = ymax + pad if y_max is None else y_max

    def sx(x: float) -> float:
        return x0 + (x - xmin) / (xmax - xmin or 1) * plot_w

    def sy(y: float) -> float:
        return y0 - (y - ymin) / (ymax - ymin or 1) * plot_h

    draw.rectangle((x0, y1, x1, y0), fill="#fbfdff", outline="#d1d5db")
    for tick in nice_ticks(ymin, ymax, 7):
        yy = sy(tick)
        draw.line((x0, yy, x1, yy), fill="#e5e7eb", width=1)
        label = f"{fmt_tick(tick)}{y_suffix}"
        tw, th = text_size(draw, label, FONT_TICK)
        draw.text((x0 - tw - 12, yy - th / 2), label, font=FONT_TICK, fill="#4b5563")
    tick_values = sorted(x_tick_labels) if x_tick_labels else sorted(set(xs))
    for tick in tick_values:
        xx = sx(tick)
        draw.line((xx, y0, xx, y0 + 8), fill="#6b7280", width=2)
        label = x_tick_labels[tick] if x_tick_labels else fmt_tick(tick)
        draw_multiline_center(draw, xx, y0 + 45, label, FONT_TICK, fill="#374151")

    draw.line((x0, y0, x1, y0), fill="#111827", width=2)
    draw.line((x0, y0, x0, y1), fill="#111827", width=2)
    draw_center(draw, ((x0 + x1) / 2, height - 38), x_label, FONT_AXIS, fill="#111827")
    label_img = Image.new("RGBA", (260, 42), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((0, 0), y_label, font=FONT_AXIS, fill="#111827")
    label_img = label_img.rotate(90, expand=True)
    img.paste(label_img, (34, int((y1 + y0) / 2 - label_img.height / 2)), label_img)

    ordered_names = [s for s in SETTINGS if s in series] + [s for s in series if s not in SETTINGS]
    for setting in ordered_names:
        points = series.get(setting)
        if not points:
            continue
        color = SETTING_COLORS.get(setting, "#2563eb")
        coords = [(sx(x), sy(y)) for x, y in points]
        if len(coords) > 1:
            draw.line(coords, fill=color, width=4, joint="curve")
        for (xx, yy), (px, py) in zip(coords, points):
            if y_err and setting in y_err and px in y_err[setting]:
                err = y_err[setting][px]
                y_hi, y_lo = sy(py + err), sy(py - err)
                draw.line((xx, y_hi, xx, y_lo), fill=color, width=2)
                draw.line((xx - 7, y_hi, xx + 7, y_hi), fill=color, width=2)
                draw.line((xx - 7, y_lo, xx + 7, y_lo), fill=color, width=2)
            draw.ellipse((xx - 6, yy - 6, xx + 6, yy + 6), fill=color, outline="white", width=2)

    legend_x = x1 + 38
    legend_y = y1 + 8
    draw.text((legend_x, legend_y), "K/V setting", font=FONT_LEGEND, fill="#111827")
    legend_y += 34
    for setting in ordered_names:
        if setting not in series:
            continue
        color = SETTING_COLORS.get(setting, "#2563eb")
        draw.line((legend_x, legend_y + 9, legend_x + 32, legend_y + 9), fill=color, width=4)
        draw.ellipse((legend_x + 12, legend_y + 3, legend_x + 24, legend_y + 15), fill=color, outline="white", width=2)
        draw.text((legend_x + 45, legend_y - 1), SETTING_LABELS.get(setting, setting), font=FONT_LEGEND, fill="#374151")
        legend_y += 32

    path = save_png(img, name)
    return Figure(path, title, subtitle)


def heatmap(
    title: str,
    subtitle: str,
    rows: list[str],
    cols: list[int],
    values: dict[tuple[str, int], float],
    name: str,
    scale_min: float,
    scale_max: float,
    value_fmt: str = "{:.2f}",
    palette: str = "blue",
    col_labels: dict[float, str] | None = None,
) -> Figure:
    img, draw = chart_base(title, subtitle)
    width, height = img.size
    left, top = 220, 170
    cell_w = min(170, max(96, int((width - left - 180 - 80) / max(1, len(cols)))))
    cell_h = 92
    row_label_w = 180
    x0 = left + row_label_w
    y0 = top

    def color_for(v: float) -> tuple[int, int, int]:
        t = clamp((v - scale_min) / (scale_max - scale_min or 1))
        if palette == "green":
            start, end = (239, 246, 255), (22, 163, 74)
        else:
            start, end = (239, 246, 255), (37, 99, 235)
        return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))

    for j, col in enumerate(cols):
        label = col_labels.get(float(col), f"P{col}") if col_labels else f"P{col}"
        draw_multiline_center(draw, x0 + j * cell_w + cell_w / 2, y0 - 50, label, FONT_TICK, fill="#111827")
    for i, row in enumerate(rows):
        y = y0 + i * cell_h
        draw.text((left, y + cell_h / 2 - 10), SETTING_LABELS.get(row, row), font=FONT_LEGEND, fill="#111827")
        for j, col in enumerate(cols):
            x = x0 + j * cell_w
            v = values.get((row, col), float("nan"))
            fill = "#f9fafb" if math.isnan(v) else color_for(v)
            draw.rectangle((x, y, x + cell_w, y + cell_h), fill=fill, outline="white", width=3)
            if not math.isnan(v):
                text = value_fmt.format(v)
                color = "white" if clamp((v - scale_min) / (scale_max - scale_min or 1)) > 0.62 else "#111827"
                draw_center(draw, (x + cell_w / 2, y + cell_h / 2), text, font(22, bold=True), fill=color)
    draw.rectangle((x0, y0, x0 + len(cols) * cell_w, y0 + len(rows) * cell_h), outline="#d1d5db", width=2)

    legend_x = x0
    legend_y = y0 + len(rows) * cell_h + 55
    draw.text((legend_x, legend_y - 28), f"Scale: {scale_min:g} to {scale_max:g}", font=FONT_SMALL, fill="#4b5563")
    grad_w, grad_h = 420, 18
    for k in range(grad_w):
        t = k / max(1, grad_w - 1)
        v = scale_min + t * (scale_max - scale_min)
        draw.line((legend_x + k, legend_y, legend_x + k, legend_y + grad_h), fill=color_for(v))
    draw.rectangle((legend_x, legend_y, legend_x + grad_w, legend_y + grad_h), outline="#9ca3af")
    draw.text((legend_x, legend_y + 26), value_fmt.format(scale_min), font=FONT_SMALL, fill="#374151")
    max_label = value_fmt.format(scale_max)
    tw, _ = text_size(draw, max_label, FONT_SMALL)
    draw.text((legend_x + grad_w - tw, legend_y + 26), max_label, font=FONT_SMALL, fill="#374151")

    path = save_png(img, name)
    return Figure(path, title, subtitle)


def html_table(headers: list[str], rows: list[list[object]], classes: str = "") -> str:
    cls = f' class="{classes}"' if classes else ""
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = []
    for row in rows:
        cells = []
        for c in row:
            text = html.escape(str(c)).replace("\n", "<br>")
            cells.append(f"<td>{text}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table{cls}><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def style_block() -> str:
    return """
<style>
.tq-report { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #ffffff !important; color: #111827 !important; padding: 14px; border-radius: 6px; }
.tq-report table { border-collapse: collapse; width: 100%; margin: 0.7rem 0 1.2rem 0; font-size: 13px; }
.tq-report th { background: #f3f4f6 !important; color: #111827 !important; font-weight: 700; }
.tq-report td { background: #ffffff !important; color: #111827 !important; }
.tq-report th, .tq-report td { border: 1px solid #d1d5db; padding: 8px 10px; vertical-align: top; }
.tq-report .tight td { padding: 6px 8px; }
.tq-report .metric { font-weight: 700; color: #0f172a; }
.tq-report .note { color: #4b5563; font-size: 13px; }
</style>
"""


def html_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {"trusted": True},
        "outputs": [
            {
                "output_type": "display_data",
                "metadata": {},
                "data": {
                    "text/html": source,
                    "text/plain": re.sub("<[^<]+?>", "", source)[:2000],
                },
            }
        ],
        "source": "from IPython.display import HTML, display\ndisplay(HTML(" + json.dumps(source) + "))\n",
    }


def md_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip() + "\n"}


def image_cell(fig: Figure) -> dict:
    data = base64.b64encode(fig.path.read_bytes()).decode("ascii")
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {"trusted": True},
        "outputs": [
            {
                "output_type": "display_data",
                "metadata": {},
                "data": {
                    "image/png": data,
                    "text/plain": f"<Figure: {fig.title}>",
                },
            }
        ],
        "source": f"# {fig.title}\n# Generated by turboquant/autoresearch/make_report_notebook.py\n",
    }


def build_prompt_metrics(quality_rows: list[dict]) -> tuple[dict, dict, dict, list[list[object]]]:
    cosine_scores: dict[str, list[tuple[float, float]]] = defaultdict(list)
    length_ratios: dict[str, list[tuple[float, float]]] = defaultdict(list)
    baseline_agreement: dict[str, list[tuple[float, float]]] = defaultdict(list)
    baseline_by_prompt = {
        int(r["prompt_id"]): r["output"]
        for r in quality_rows
        if r["setting"] == "f16/f16"
    }
    prompt_rows: dict[int, dict] = {}

    for row in quality_rows:
        setting = row["setting"]
        pid = int(row["prompt_id"])
        prompt_rows.setdefault(pid, row)
        ref = row.get("reference", "")
        out = row.get("output", "")
        ref_tokens = max(1, len(tokenize(ref)))
        out_tokens = len(tokenize(out))
        cosine_scores[setting].append((pid, cosine(ref, out)))
        length_ratios[setting].append((pid, out_tokens / ref_tokens))
        baseline = baseline_by_prompt.get(pid, "")
        baseline_agreement[setting].append((pid, cosine(baseline, out) if baseline else 0.0))

    for groups in (cosine_scores, length_ratios, baseline_agreement):
        for key in list(groups):
            groups[key] = sorted(groups[key])

    prompt_table = [
        [pid, category_label(row), row["prompt"], row["reference"]]
        for pid, row in sorted(prompt_rows.items())
    ]
    return cosine_scores, length_ratios, baseline_agreement, prompt_table


def build_figures(gemma_speed: list[dict], ppl: list[dict], quality_rows: list[dict], per_prompt_judge: list[dict]) -> dict[str, Figure]:
    figs: dict[str, Figure] = {}

    speed_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in gemma_speed:
        setting = f"{row['type_k']}/{row['type_v']}"
        speed_series[setting].append((float(row["kv_depth"]), float(row["tokens_per_second"])))
    speed_series = {k: sorted(v) for k, v in speed_series.items() if k in SETTINGS}
    depth_ticks = {float(d): str(d) for d in sorted({int(r["kv_depth"]) for r in gemma_speed})}
    figs["speed"] = line_chart(
        "Gemma 4 E4B decode throughput",
        "CPU-only llama-bench, 6 threads, flash attention, n_prompt=0, n_gen=16.",
        "KV cache depth",
        "tokens / second",
        speed_series,
        "gemma4_decode_throughput.png",
        x_tick_labels=depth_ticks,
    )

    base_by_depth = {
        int(r["kv_depth"]): float(r["tokens_per_second"])
        for r in gemma_speed
        if r["type_k"] == "f16" and r["type_v"] == "f16"
    }
    speedup_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in gemma_speed:
        setting = f"{row['type_k']}/{row['type_v']}"
        if setting == "f16/f16":
            continue
        depth = int(row["kv_depth"])
        speedup_series[setting].append((depth, 100 * (float(row["tokens_per_second"]) / base_by_depth[depth] - 1)))
    figs["speedup"] = line_chart(
        "Relative decode speedup vs F16/F16",
        "Positive values mean faster than the F16 K/V baseline at the same depth.",
        "KV cache depth",
        "speedup",
        {k: sorted(v) for k, v in speedup_series.items()},
        "gemma4_speedup_vs_f16.png",
        x_tick_labels=depth_ticks,
        y_suffix="%",
    )

    ppl_by_setting = {r["config"]: (float(r["ppl"]), float(r["ppl_stderr"])) for r in ppl}
    x_positions = {float(i): SETTING_LABELS[s].replace("/", "\n") for i, s in enumerate(SETTINGS) if s in ppl_by_setting}
    ppl_series = {
        "Perplexity": [
            (float(i), ppl_by_setting[s][0])
            for i, s in enumerate(SETTINGS)
            if s in ppl_by_setting
        ]
    }
    ppl_err = {
        "Perplexity": {
            float(i): ppl_by_setting[s][1]
            for i, s in enumerate(SETTINGS)
            if s in ppl_by_setting
        }
    }
    figs["ppl"] = line_chart(
        "WikiText-2 perplexity by K/V configuration",
        "20 chunks, ctx=512. Error bars are the reported per-run stderr.",
        "K/V configuration",
        "perplexity",
        ppl_series,
        "gemma4_ppl_curve.png",
        x_tick_labels=x_positions,
        y_err=ppl_err,
    )

    cosine_scores, length_ratios, baseline_agreement, _ = build_prompt_metrics(quality_rows)
    x_ticks = prompt_short_labels(quality_rows)
    prompt_ids = sorted(int(x) for x in x_ticks)
    task_scores = task_adherence_series(quality_rows)
    if task_scores:
        figs["task_adherence"] = line_chart(
            "Task-adherence score by prompt and K/V configuration",
            "Prompt-specific checks: arithmetic, JSON validity, exact labels, corrected code, puzzle answer, and safety action.",
            "Prompt",
            "task score",
            task_scores,
            "gemma4_task_adherence_by_prompt.png",
            x_tick_labels=x_ticks,
            y_min=0.0,
            y_max=1.05,
        )
        figs["task_adherence_heatmap"] = heatmap(
            "Task-adherence matrix",
            "Each score is normalized from 0 to 1 using prompt-specific criteria. Higher is better.",
            [s for s in SETTINGS if s in task_scores],
            prompt_ids,
            {(setting, int(pid)): score for setting, pts in task_scores.items() for pid, score in pts},
            "gemma4_task_adherence_heatmap.png",
            scale_min=0,
            scale_max=1,
            value_fmt="{:.2f}",
            palette="green",
            col_labels=x_ticks,
        )
    cosine_values = [score for pts in cosine_scores.values() for _, score in pts]
    cosine_min = max(0.0, min(cosine_values) - 0.08) if cosine_values else 0.0
    cosine_max = min(1.0, max(cosine_values) + 0.08) if cosine_values else 1.0
    figs["quality_cosine"] = line_chart(
        "Reference cosine by prompt and K/V configuration",
        "Lexical quality proxy: cosine similarity between generated answer and reference answer.",
        "Prompt",
        "reference cosine",
        cosine_scores,
        "gemma4_quality_cosine_by_prompt.png",
        x_tick_labels=x_ticks,
        y_min=cosine_min,
        y_max=cosine_max,
    )
    figs["quality_heatmap"] = heatmap(
        "Reference cosine matrix",
        "Each cell is one prompt under one K/V setting. Higher is closer to the reference.",
        [s for s in SETTINGS if s in cosine_scores],
        prompt_ids,
        {(setting, int(pid)): score for setting, pts in cosine_scores.items() for pid, score in pts},
        "gemma4_quality_cosine_heatmap.png",
        scale_min=cosine_min,
        scale_max=cosine_max,
        value_fmt="{:.3f}",
        col_labels=x_ticks,
    )
    figs["length_ratio"] = line_chart(
        "Answer length ratio by prompt and K/V configuration",
        "Output tokens divided by reference tokens. This exposes truncation/completeness effects.",
        "Prompt",
        "output / reference token ratio",
        length_ratios,
        "gemma4_length_ratio_by_prompt.png",
        x_tick_labels=x_ticks,
        y_min=0.0,
        y_max=max(1.45, min(2.2, max([v for pts in length_ratios.values() for _, v in pts] + [1.0]) + 0.15)),
    )
    figs["baseline_agreement"] = line_chart(
        "Agreement with F16 output by prompt",
        "Cosine similarity to the F16/F16 answer for the same prompt; F16 is 1.0 by definition.",
        "Prompt",
        "cosine vs F16 output",
        baseline_agreement,
        "gemma4_baseline_agreement_by_prompt.png",
        x_tick_labels=x_ticks,
        y_min=0.75,
        y_max=1.02,
    )

    if per_prompt_judge:
        quality_index: dict[str, list[tuple[float, float]]] = defaultdict(list)
        completeness: dict[str, list[tuple[float, float]]] = defaultdict(list)
        heat_values = {}
        for row in per_prompt_judge:
            setting = row["setting"]
            pid = row["prompt_id"]
            q = (row["correctness"] + row["completeness"] + row["coherence"] + row["safety"]) / 4
            quality_index[setting].append((pid, q))
            completeness[setting].append((pid, row["completeness"]))
            heat_values[(setting, pid)] = q
        for groups in (quality_index, completeness):
            for setting in list(groups):
                groups[setting] = sorted(groups[setting])
        figs["judge_quality"] = line_chart(
            "LLM judge quality index by prompt",
            "Mean of correctness, completeness, coherence, and safety scores from the chat subagent.",
            "Prompt",
            "judge score",
            quality_index,
            "gemma4_judge_quality_by_prompt.png",
            x_tick_labels=x_ticks,
            y_min=0,
            y_max=5.2,
        )
        figs["judge_completeness"] = heatmap(
            "LLM judge quality index matrix",
            "Per-prompt, per-configuration chat-subagent score. Higher is better.",
            [s for s in SETTINGS if s in quality_index],
            prompt_ids,
            heat_values,
            "gemma4_judge_quality_heatmap.png",
            scale_min=0,
            scale_max=5,
            value_fmt="{:.2f}",
            palette="green",
            col_labels=x_ticks,
        )
        figs["judge_completion_curve"] = line_chart(
            "LLM judge completeness by prompt",
            "Completeness is most sensitive to the 120-token truncation in this run.",
            "Prompt",
            "completeness score",
            completeness,
            "gemma4_judge_completeness_by_prompt.png",
            x_tick_labels=x_ticks,
            y_min=0,
            y_max=5.2,
        )

    return figs


def hardware_rows() -> list[list[str]]:
    lscpu = sh(["lscpu"])
    fields = {}
    for line in lscpu.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = " ".join(v.split())
    return [
        ["CPU", fields.get("Model name", "unknown")],
        ["Architecture", fields.get("Architecture", "unknown")],
        ["Logical CPUs", fields.get("CPU(s)", "unknown")],
        ["Cores / socket", fields.get("Core(s) per socket", "unknown")],
        ["Threads / core", fields.get("Thread(s) per core", "unknown")],
        ["Caches", f"L2 {fields.get('L2 cache', 'unknown')}, L3 {fields.get('L3 cache', 'unknown')}"],
        ["Backend", "CPU only; GPU layers set to 0 for quality/perplexity runs"],
        ["Threads used in reported Gemma 4 runs", "6"],
    ]


def make_notebook() -> dict:
    gemma_speed = read_csv(GEMMA_SPEED_CSV)
    ppl = read_csv(PPL_CSV)
    quality_path, judge_path, quality_set_name = select_quality_artifact()
    quality_rows = read_jsonl(quality_path)
    agg_judge = parse_aggregate_judge(AGG_JUDGE_MD)
    per_prompt_judge = parse_per_prompt_judge(judge_path)
    figs = build_figures(gemma_speed, ppl, quality_rows, per_prompt_judge)
    _, _, _, prompt_table = build_prompt_metrics(quality_rows)
    n_predict = n_predict_from_rows(quality_rows)

    eight_k = {f"{r['type_k']}/{r['type_v']}": float(r["tokens_per_second"]) for r in gemma_speed if int(r["kv_depth"]) == 8192}
    f16_8k = eight_k["f16/f16"]
    tbq4_8k = eight_k["tbq4/tbq4"]
    q8_8k = eight_k["q8_0/q8_0"]
    ppl_by_setting = {r["config"]: float(r["ppl"]) for r in ppl}

    summary = html_table(
        ["Finding", "Value"],
        [
            ["Fastest 8K K/V setting", f"TBQ4/TBQ4 at {tbq4_8k:.3f} tok/s"],
            ["8K speedup vs F16/F16", f"{100 * (tbq4_8k / f16_8k - 1):+.1f}%"],
            ["8K speedup vs Q8/Q8", f"{100 * (tbq4_8k / q8_8k - 1):+.1f}%"],
            ["Best 20-chunk PPL", f"TBQ4/TBQ4 at {ppl_by_setting['tbq4/tbq4']:.4f}"],
            ["Completed quality prompts", f"{len({int(r['prompt_id']) for r in quality_rows})} prompts x {len({r['setting'] for r in quality_rows})} K/V settings"],
            ["Quality prompt set", f"{quality_set_name} ({quality_path.name}), n_predict={n_predict}"],
            ["Primary caveat", "Lexical metrics are proxies; the chat-subagent judge table is included when available for the selected prompt set."],
        ],
        "tight",
    )

    speed_table = html_table(
        ["K/V setting", "8K tok/s", "delta vs F16"],
        [
            [SETTING_LABELS[s], f"{eight_k[s]:.3f}", f"{100 * (eight_k[s] / f16_8k - 1):+.1f}%"]
            for s in SETTINGS
            if s in eight_k
        ],
        "tight",
    )

    ppl_table = html_table(
        ["K/V setting", "PPL", "stderr", "delta vs F16", "elapsed sec"],
        [
            [
                SETTING_LABELS.get(r["config"], r["config"]),
                f"{float(r['ppl']):.4f}",
                f"{float(r['ppl_stderr']):.4f}",
                f"{100 * (float(r['ppl']) / float(ppl[0]['ppl']) - 1):+.2f}%",
                f"{float(r['elapsed_sec']):.1f}",
            ]
            for r in ppl
        ],
        "tight",
    )

    prompt_input_table = html_table(
        ["Test", "Prompt/input source", "Details"],
        [
            ["Decode speed", "No natural-language prompt", "`llama-bench` used n_prompt=0 and n_gen=16; this is decode-only throughput."],
            ["Perplexity", "WikiText-2 raw validation text", "20 chunks, ctx=512, 6 CPU threads, flash attention enabled."],
            ["Deterministic quality and judge", f"{quality_set_name} prompt set", "Each prompt was run for F16/F16, Q8/Q8, Q4/Q4, TBQ4/TBQ4, and Q8/TBQ4."],
        ],
        "tight",
    )
    exact_prompt_table = html_table(
        ["ID", "Category", "Exact prompt", "Reference used for cosine proxy"],
        prompt_table,
    )

    cosine_scores, length_ratios, baseline_agreement, _ = build_prompt_metrics(quality_rows)
    task_scores = task_adherence_series(quality_rows)
    mean_quality_rows = []
    for setting in SETTINGS:
        if setting in cosine_scores:
            mean_task = ""
            if setting in task_scores:
                mean_task = f"{sum(v for _, v in task_scores[setting]) / len(task_scores[setting]):.2f}"
            mean_cos = sum(v for _, v in cosine_scores[setting]) / len(cosine_scores[setting])
            mean_len = sum(v for _, v in length_ratios[setting]) / len(length_ratios[setting])
            mean_agree = sum(v for _, v in baseline_agreement[setting]) / len(baseline_agreement[setting])
            mean_quality_rows.append([SETTING_LABELS[setting], mean_task, f"{mean_cos:.3f}", f"{mean_len:.2f}", f"{mean_agree:.3f}"])
    quality_summary = html_table(
        ["K/V setting", "Mean task score", "Mean reference cosine", "Mean length ratio", "Mean F16 agreement"],
        mean_quality_rows,
        "tight",
    )

    agg_judge_table = html_table(
        ["K/V setting", "Correctness", "Completeness", "Coherence", "Safety", "Degenerate", "Issue summary"],
        [
            [
                SETTING_LABELS.get(r["setting"], r["setting"]),
                r["correctness"],
                r["completeness"],
                r["coherence"],
                r["safety"],
                r["degenerate_rate"],
                r["issues"],
            ]
            for r in agg_judge
        ],
    )

    judge_per_prompt_table = ""
    if per_prompt_judge:
        judge_per_prompt_table = html_table(
            ["Prompt", "K/V setting", "Correctness", "Completeness", "Coherence", "Safety", "Degenerate", "Note"],
            [
                [
                    r["prompt_id"],
                    SETTING_LABELS.get(r["setting"], r["setting"]),
                    f"{r['correctness']:.1f}",
                    f"{r['completeness']:.1f}",
                    f"{r['coherence']:.1f}",
                    f"{r['safety']:.1f}",
                    r["degenerate"],
                    r["note"],
                ]
                for r in sorted(per_prompt_judge, key=lambda x: (x["prompt_id"], SETTINGS.index(x["setting"]) if x["setting"] in SETTINGS else 99))
            ],
            "tight",
        )

    cells = [
        md_cell(
            """
# Gemma 4 E4B CPU K/V-Cache Report

This notebook reports only the Gemma 4 E4B CPU experiments in this repository:
decode speed, WikiText-2 perplexity, deterministic prompt quality, and
chat-subagent quality judging. All figures are embedded as PNG outputs so the
report renders without JavaScript or notebook trust configuration.
"""
        ),
        html_cell(f'<div class="tq-report">{style_block()}{summary}</div>'),
        md_cell("## Experimental Setup\n\nThe reported run is CPU-only on the local x86 host. No GPU acceleration is included in these measurements."),
        html_cell(f'<div class="tq-report">{html_table(["Field", "Value"], hardware_rows(), "tight")}</div>'),
        md_cell("## Benchmark Inputs\n\nThe speed benchmark is decode-only. The qualitative benchmark uses the selected prompt set shown below; these prompts define the scope of the current quality claim."),
        html_cell(f'<div class="tq-report">{prompt_input_table}{exact_prompt_table}</div>'),
        md_cell("## Decode Speed\n\nThe main speed question is how K/V cache format changes decode throughput as KV depth grows. TBQ4/TBQ4 is the fastest tested configuration at 8K depth."),
        image_cell(figs["speed"]),
        image_cell(figs["speedup"]),
        html_cell(f'<div class="tq-report">{speed_table}</div>'),
        md_cell("## Perplexity\n\nPerplexity is shown as an ordered curve across K/V configurations with stderr error bars. On this 20-chunk run, TBQ4/TBQ4 is not worse than F16/F16 and has the lowest measured PPL, but the run is still small enough that the result should be treated as preliminary."),
        image_cell(figs["ppl"]),
        html_cell(f'<div class="tq-report">{ppl_table}</div>'),
        md_cell(f"## Per-Prompt Quality Metrics\n\nThese curves use the `{quality_set_name}` prompt set from `{quality_path.name}`. The task-adherence score is prompt-specific and checks concrete requirements such as arithmetic, JSON validity, bullet labels, corrected code, puzzle logic, and medical safety actions. Reference cosine remains a lexical proxy; length ratio helps explain verbosity/completeness; F16 agreement shows whether quantized K/V changes the generated content relative to baseline."),
        *([image_cell(figs["task_adherence"]), image_cell(figs["task_adherence_heatmap"])] if "task_adherence" in figs else []),
        image_cell(figs["quality_cosine"]),
        image_cell(figs["quality_heatmap"]),
        image_cell(figs["length_ratio"]),
        image_cell(figs["baseline_agreement"]),
        html_cell(f'<div class="tq-report">{quality_summary}</div>'),
        md_cell("## Chat-Subagent Judge\n\nThe aggregate judge result is retained for historical context. Per-prompt judge scores are shown when a judge table exists for the selected prompt set."),
        html_cell(f'<div class="tq-report">{agg_judge_table}</div>'),
    ]

    if per_prompt_judge:
        cells.extend(
            [
                md_cell("### Per-Prompt Judge Scores\n\nThese scores come from the chat subagent and are shown per prompt and per K/V configuration."),
                image_cell(figs["judge_quality"]),
                image_cell(figs["judge_completeness"]),
                image_cell(figs["judge_completion_curve"]),
                html_cell(f'<div class="tq-report">{judge_per_prompt_table}</div>'),
            ]
        )
    else:
        cells.append(
            md_cell(
                """
### Per-Prompt Judge Scores

Per-prompt chat-subagent judge scores have not been written for the selected
prompt set yet. The notebook therefore reports deterministic per-prompt metrics
and the aggregate judge score for now.
"""
            )
        )

    cells.extend(
        [
            md_cell("## Memory Implications\n\nTBQ4 has the same 4-bit block storage footprint as Q4_0 but uses non-uniform centroids. Hybrid Q8/TBQ4 preserves K at Q8 while compressing V to TBQ4."),
            html_cell(
                f'<div class="tq-report">{html_table(["K/V format", "bytes per 32 values", "reduction vs F16"], [["F16", "64", "1.00x"], ["Q8_0", "34", "1.88x"], ["Q4_0", "18", "3.56x"], ["TBQ4", "18", "3.56x"], ["Q8/TBQ4 pair", "52 for K+V", "2.46x"]], "tight")}</div>'
            ),
            md_cell(
                """
## Interpretation

On this Intel Core i5-12500 CPU-only run, Gemma 4 E4B benefits from TBQ4 K/V at
long KV depth. TBQ4/TBQ4 is fastest at 8K, has the best preliminary PPL, and
does not show a clear quality regression in the selected prompt-quality run.
The claim should remain model- and device-specific until larger prompt sets,
longer generations, and ARM CPU replication are complete.
"""
            ),
            md_cell(
                """
## Remaining Work

- Rerun speed with `n_gen=128`, more repetitions, and both 6-thread and 12-thread settings.
- Expand beyond the current hard prompt set with more domain and long-context tasks.
- Add or refresh per-prompt chat-subagent judging whenever the prompt set changes.
- Extend perplexity to more chunks and longer contexts where feasible.
- Replicate on ARM CPU using `turboquant/ARM_REPLICATION.md`.
"""
            ),
        ]
    )

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    nb = make_notebook()
    OUT.write_text(json.dumps(nb, indent=2), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
