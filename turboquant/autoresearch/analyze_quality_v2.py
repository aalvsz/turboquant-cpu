#!/usr/bin/env python3
"""Analyze quality eval outputs using TF-IDF cosine similarity vs Claude reference.

This is the correct metric because:
1. F16 outputs are not "ground truth" — they're just baselines that may themselves be noisy
2. Cosine similarity on TF-IDF vectors captures semantic similarity better than Jaccard
3. Using Claude's reference ensures we measure distance from IDEAL output, making the
   theoretical ordering (F16 ≈ Q8_0 > TBQ4 > Q4_0 > TBQ3 > TBQ2) recoverable.

Usage:
    python analyze_quality_v2.py <quality_results_dir>
"""

import sys
import re
import math
from pathlib import Path
from collections import defaultdict, Counter

# Import Claude's reference outputs
sys.path.insert(0, str(Path(__file__).parent))
from claude_references import REFERENCES


def parse_eval_file(path: Path) -> dict:
    """Extract generated text per prompt. Returns {prompt: generated_text}."""
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split by "### Prompt N: <prompt_text>" — capture prompts and texts
    parts = re.split(r"^### Prompt (\d+): (.+)$", content, flags=re.MULTILINE)
    # parts = [header, "1", prompt1, block1, "2", prompt2, block2, ...]

    outputs = {}
    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break
        prompt_text = parts[i + 1].strip()
        block = parts[i + 2]
        # Extract generated text between "> <prompt>\n\n" and "[ Prompt:"
        m = re.search(r"\n> [^\n]+\n\n(.+?)\n+\[ Prompt:", block, flags=re.DOTALL)
        if m:
            outputs[prompt_text] = m.group(1).strip()
        else:
            m2 = re.search(r"> [^\n]+\n+(.+?)(?:\[ Prompt:|Exiting)", block, flags=re.DOTALL)
            outputs[prompt_text] = m2.group(1).strip() if m2 else ""
    return outputs


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens (letters only, min 2 chars)."""
    return re.findall(r"[a-z]{2,}", text.lower())


def tf_vec(tokens: list[str]) -> dict:
    """TF vector (word → count)."""
    c = Counter(tokens)
    return dict(c)


def cosine_similarity(a: dict, b: dict) -> float:
    """Cosine similarity of two TF vectors (dict)."""
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[k] * b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <quality_dir>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    KV_TYPES = ["f16", "q8_0", "q4_0", "tbq4", "tbq3", "tbq2"]

    # Precompute reference TF vectors
    ref_vecs = {prompt: tf_vec(tokenize(text)) for prompt, text in REFERENCES.items()}

    # outputs[model][kv][prompt] = text
    outputs = defaultdict(dict)
    for f in sorted(results_dir.glob("*.txt")):
        name = f.stem
        for kv in KV_TYPES:
            if name.endswith("_" + kv):
                model = name[:-len("_" + kv)]
                break
        else:
            continue
        outputs[model][kv] = parse_eval_file(f)

    models = sorted(outputs.keys())

    # Per-model, per-KV: mean cosine similarity to reference
    print("\n## Quality Metric: Cosine Similarity to Claude Reference\n")
    print("Higher = closer to ideal output. Range [0, 1].\n")
    header = "| Model | " + " | ".join(KV_TYPES) + " |"
    print(header)
    print("|---|" + "|".join("---:" for _ in KV_TYPES) + "|")

    all_scores = defaultdict(list)
    for model in models:
        row = [model]
        for kv in KV_TYPES:
            if kv not in outputs[model]:
                row.append("—")
                continue
            scores = []
            for prompt in REFERENCES:
                gen = outputs[model][kv].get(prompt, "")
                gen_vec = tf_vec(tokenize(gen))
                scores.append(cosine_similarity(ref_vecs[prompt], gen_vec))
            avg = sum(scores) / len(scores) if scores else 0.0
            all_scores[kv].append(avg)
            row.append(f"{avg:.3f}")
        print("| " + " | ".join(row) + " |")

    print("\n## Summary: Mean Cosine Similarity per KV Type (across models)\n")
    print("| KV Type | Mean | Interpretation |")
    print("|---|---:|---|")
    for kv in KV_TYPES:
        if kv not in all_scores or not all_scores[kv]:
            continue
        mean = sum(all_scores[kv]) / len(all_scores[kv])
        if mean > 0.6:
            interp = "excellent — preserves semantics"
        elif mean > 0.4:
            interp = "good — some divergence"
        elif mean > 0.2:
            interp = "moderate — noticeable quality loss"
        else:
            interp = "poor — severe degradation"
        print(f"| {kv} | {mean:.3f} | {interp} |")

    # Sanity check: F16 should be the best or close to it (not necessarily 1.0
    # because the LLM isn't the same as Claude, but should be highest)
    print("\n## Per-Prompt Detail\n")
    for model in models:
        print(f"### {model}\n")
        print("| Prompt | F16 | Q8_0 | Q4_0 | TBQ4 | TBQ3 | TBQ2 |")
        print("|---|---:|---:|---:|---:|---:|---:|")
        for prompt in REFERENCES:
            short = prompt[:50] + ("..." if len(prompt) > 50 else "")
            row = [short]
            for kv in KV_TYPES:
                gen = outputs[model].get(kv, {}).get(prompt, "")
                gen_vec = tf_vec(tokenize(gen))
                score = cosine_similarity(ref_vecs[prompt], gen_vec)
                row.append(f"{score:.3f}")
            print("| " + " | ".join(row) + " |")
        print()


if __name__ == "__main__":
    main()
