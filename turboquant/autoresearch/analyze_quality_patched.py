#!/usr/bin/env python3
"""Cosine-similarity aggregator for the patched-amax quality eval.

Differs from analyze_quality_v2.py only in filename parsing: the patched
sweep emits files like `<model>_<TAG>.txt` where TAG is one of:
    f16, q8_0, q4_0, tbq4, q8_0_tbq4 (hybrid)

Usage: python analyze_quality_patched.py <quality_dir>
"""

import sys
import re
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))
from claude_references import REFERENCES


def parse_eval_file(path: Path) -> dict:
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    parts = re.split(r"^### Prompt (\d+): (.+)$", content, flags=re.MULTILINE)
    outputs = {}
    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break
        prompt_text = parts[i + 1].strip()
        block = parts[i + 2]
        m = re.search(r"\n> [^\n]+\n\n(.+?)\n+\[ Prompt:", block, flags=re.DOTALL)
        if m:
            outputs[prompt_text] = m.group(1).strip()
        else:
            m2 = re.search(r"> [^\n]+\n+(.+?)(?:\[ Prompt:|Exiting)", block, flags=re.DOTALL)
            outputs[prompt_text] = m2.group(1).strip() if m2 else ""
    return outputs


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]{2,}", text.lower())


def tf_vec(tokens: list[str]) -> dict:
    return dict(Counter(tokens))


def cosine_similarity(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[k] * b[k] for k in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


# Longest-tag-first so q8_0_tbq4 is tested before q8_0
TAGS = ["q8_0_tbq4", "f16", "q8_0", "q4_0", "tbq4"]
TAG_LABEL = {
    "f16": "F16",
    "q8_0": "Q8_0",
    "q4_0": "Q4_0",
    "tbq4": "TBQ4 (sym)",
    "q8_0_tbq4": "q8_0/tbq4",
}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <quality_dir>")
        sys.exit(1)
    results_dir = Path(sys.argv[1])
    ref_vecs = {p: tf_vec(tokenize(t)) for p, t in REFERENCES.items()}
    outputs = defaultdict(dict)

    for f in sorted(results_dir.glob("*.txt")):
        name = f.stem
        for tag in TAGS:
            if name.endswith("_" + tag):
                model = name[: -(len(tag) + 1)]
                outputs[model][tag] = parse_eval_file(f)
                break
        else:
            print(f"# UNMATCHED: {f.name}", file=sys.stderr)

    models = sorted(outputs.keys())
    cols = TAGS  # display all tags as columns
    headers = [TAG_LABEL[t] for t in cols]

    print("\n## Patched-amax Quality (cosine vs Claude refs, mean over 5 prompts)\n")
    print("| Model | " + " | ".join(headers) + " |")
    print("|---|" + "|".join("---:" for _ in cols) + "|")

    means_per_tag = defaultdict(list)
    for model in models:
        row = [model]
        for tag in cols:
            if tag not in outputs[model]:
                row.append("—")
                continue
            scores = []
            for p in REFERENCES:
                gen = outputs[model][tag].get(p, "")
                scores.append(cosine_similarity(ref_vecs[p], tf_vec(tokenize(gen))))
            avg = sum(scores) / len(scores) if scores else 0.0
            means_per_tag[tag].append(avg)
            row.append(f"{avg:.3f}")
        print("| " + " | ".join(row) + " |")

    print("\n## Mean across models\n")
    print("| KV config | Mean cosine |")
    print("|---|---:|")
    for tag in cols:
        if not means_per_tag[tag]:
            continue
        print(f"| {TAG_LABEL[tag]} | {sum(means_per_tag[tag])/len(means_per_tag[tag]):.3f} |")

    # Show one example output per (model, tag) so we can spot degeneracy
    print("\n## Spot-check: first-prompt outputs (truncated to 120 chars)\n")
    first_prompt = next(iter(REFERENCES))
    print(f"Prompt: {first_prompt!r}\n")
    print("| Model | KV config | Output |")
    print("|---|---|---|")
    for model in models:
        for tag in cols:
            if tag not in outputs[model]:
                continue
            gen = outputs[model][tag].get(first_prompt, "")[:120].replace("\n", " ↵ ")
            print(f"| {model} | {TAG_LABEL[tag]} | {gen} |")


if __name__ == "__main__":
    main()
