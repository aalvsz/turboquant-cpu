#!/usr/bin/env python3
"""Generate a quality-vs-speed tradeoff plot for hybrid KV settings.

This figure is intentionally focused on the two models where the hybrid
q8_0/tbq4 result is actionable: Llama 3.1 8B and Qwen2.5 7B.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


POINTS = [
    {
        "label": "Llama tbq4/tbq4",
        "model": "llama",
        "kind": "symmetric_tbq4",
        "quality": 0.291,
        "tps": 4.25,
    },
    {
        "label": "Llama q8/q4_0",
        "model": "llama",
        "kind": "hybrid_q4",
        "quality": 0.498,
        "tps": 4.29,
    },
    {
        "label": "Llama q8/tbq4",
        "model": "llama",
        "kind": "hybrid_tbq4",
        "quality": 0.533,
        "tps": 4.21,
    },
    {
        "label": "Qwen tbq4/tbq4",
        "model": "qwen",
        "kind": "symmetric_tbq4",
        "quality": 0.000,
        "tps": 4.99,
    },
    {
        "label": "Qwen q8/q4_0",
        "model": "qwen",
        "kind": "hybrid_q4",
        "quality": 0.654,
        "tps": 5.37,
    },
    {
        "label": "Qwen q8/tbq4",
        "model": "qwen",
        "kind": "hybrid_tbq4",
        "quality": 0.687,
        "tps": 5.11,
    },
]

MODEL_COLORS = {
    "llama": (31, 78, 121),
    "qwen": (178, 72, 29),
}

KIND_STYLES = {
    "symmetric_tbq4": {"fill": False, "radius": 9},
    "hybrid_q4": {"fill": True, "radius": 8},
    "hybrid_tbq4": {"fill": True, "radius": 10},
}


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def map_range(v: float, a0: float, a1: float, b0: float, b1: float) -> float:
    if a1 == a0:
        return b0
    return b0 + (v - a0) * (b1 - b0) / (a1 - a0)


def draw_axes(draw: ImageDraw.ImageDraw, left: int, top: int, right: int, bottom: int, font: ImageFont.ImageFont) -> None:
    axis = (35, 35, 35)
    grid = (220, 220, 220)
    draw.rectangle((left, top, right, bottom), outline=axis, width=2)

    for q in [0.0, 0.2, 0.4, 0.6, 0.8]:
        y = map_range(q, 0.0, 0.8, bottom, top)
        draw.line((left, y, right, y), fill=grid, width=1)
        text = f"{q:.1f}"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((left - 16 - (bbox[2] - bbox[0]), y - (bbox[3] - bbox[1]) / 2), text, fill=axis, font=font)

    for tps in [4.0, 4.5, 5.0, 5.5]:
        x = map_range(tps, 4.0, 5.6, left, right)
        draw.line((x, top, x, bottom), fill=grid, width=1)
        text = f"{tps:.1f}"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((x - (bbox[2] - bbox[0]) / 2, bottom + 10), text, fill=axis, font=font)


def draw_point(draw: ImageDraw.ImageDraw, x: float, y: float, color: tuple[int, int, int], kind: str) -> None:
    style = KIND_STYLES[kind]
    r = style["radius"]
    box = (x - r, y - r, x + r, y + r)
    if style["fill"]:
        draw.ellipse(box, fill=color, outline=(255, 255, 255), width=2)
    else:
        draw.ellipse(box, fill=(255, 255, 255), outline=color, width=3)


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "hybrid_quality_speed.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    width = 1240
    height = 820
    left, top, right, bottom = 120, 120, 1100, 650

    img = Image.new("RGB", (width, height), (250, 248, 243))
    draw = ImageDraw.Draw(img)

    title_font = load_font(34)
    subtitle_font = load_font(18)
    label_font = load_font(20)
    tick_font = load_font(16)
    legend_font = load_font(18)

    draw.text((left, 38), "Hybrid q8_0/tbq4 Preserves More Quality at Nearly the Same 8K Speed", fill=(20, 20, 20), font=title_font)
    draw.text((left, 78), "Patched exact-dot build. X axis = 5-prompt cosine proxy, Y axis = tg128 tokens/s at d=8192.", fill=(75, 75, 75), font=subtitle_font)

    draw_axes(draw, left, top, right, bottom, tick_font)

    draw.text((right - 40, bottom + 44), "tg128 tokens/s @ d=8192", fill=(20, 20, 20), font=label_font, anchor="ra")
    draw.text((28, top - 10), "quality", fill=(20, 20, 20), font=label_font)
    draw.text((28, top + 18), "(cosine)", fill=(20, 20, 20), font=label_font)

    label_offsets = {
        "Llama tbq4/tbq4": (14, 8),
        "Llama q8/q4_0": (14, -26),
        "Llama q8/tbq4": (14, 10),
        "Qwen tbq4/tbq4": (14, -26),
        "Qwen q8/q4_0": (14, -26),
        "Qwen q8/tbq4": (14, 8),
    }

    for point in POINTS:
        x = map_range(point["tps"], 4.0, 5.6, left, right)
        y = map_range(point["quality"], 0.0, 0.8, bottom, top)
        color = MODEL_COLORS[point["model"]]
        draw_point(draw, x, y, color, point["kind"])

        dx, dy = label_offsets[point["label"]]
        draw.text((x + dx, y + dy), point["label"], fill=color, font=legend_font)

    legend_y = 720
    draw.text((left, legend_y), "Model colors:", fill=(20, 20, 20), font=legend_font)
    draw.ellipse((left + 130, legend_y + 2, left + 146, legend_y + 18), fill=MODEL_COLORS["llama"])
    draw.text((left + 156, legend_y), "Llama 3.1 8B", fill=(20, 20, 20), font=legend_font)
    draw.ellipse((left + 340, legend_y + 2, left + 356, legend_y + 18), fill=MODEL_COLORS["qwen"])
    draw.text((left + 366, legend_y), "Qwen2.5 7B", fill=(20, 20, 20), font=legend_font)

    draw.text((left, legend_y + 34), "Marker styles:", fill=(20, 20, 20), font=legend_font)
    draw.ellipse((left + 130, legend_y + 36, left + 150, legend_y + 56), fill=(255, 255, 255), outline=(70, 70, 70), width=3)
    draw.text((left + 160, legend_y + 34), "symmetric tbq4/tbq4", fill=(20, 20, 20), font=legend_font)
    draw.ellipse((left + 410, legend_y + 38, left + 426, legend_y + 54), fill=(70, 70, 70), outline=(255, 255, 255), width=2)
    draw.text((left + 436, legend_y + 34), "hybrid q8/q4_0", fill=(20, 20, 20), font=legend_font)
    draw.ellipse((left + 650, legend_y + 35, left + 670, legend_y + 55), fill=(70, 70, 70), outline=(255, 255, 255), width=2)
    draw.text((left + 680, legend_y + 34), "hybrid q8/tbq4", fill=(20, 20, 20), font=legend_font)

    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
