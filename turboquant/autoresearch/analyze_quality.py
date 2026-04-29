#!/usr/bin/env python3
"""Analyze quality eval outputs: Jaccard similarity vs F16 baseline per prompt.

Usage:
    python analyze_quality.py <quality_results_dir>
"""

import sys
import re
from pathlib import Path
from collections import defaultdict


def parse_eval_file(path: Path) -> list[str]:
    """Extract generated text per prompt from eval file.

    Each prompt section has a llama-cli banner then "> <prompt>" then the
    generated text then "[ Prompt: ... | Generation: ... ]".
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split by "### Prompt N:" markers
    parts = re.split(r"^### Prompt \d+:.*$", content, flags=re.MULTILINE)
    # parts[0] is header, parts[1..] are generations

    outputs = []
    for p in parts[1:]:
        # Find the generated text: everything between "> " (the prompt echo)
        # and the "[ Prompt:" performance footer.
        # Actually llama-cli prints the user's prompt line, then a blank line,
        # then the response, then "[ Prompt:" stats.
        # Find everything after the LAST "> " line before "[ Prompt:".
        m = re.search(r"\n> [^\n]+\n\n(.+?)\n+\[ Prompt:", p, flags=re.DOTALL)
        if m:
            outputs.append(m.group(1).strip())
        else:
            # Fallback: just grab content after any "> "
            m2 = re.search(r"> [^\n]+\n+(.+?)(?:\[ Prompt:|\n\nExiting)", p, flags=re.DOTALL)
            outputs.append(m2.group(1).strip() if m2 else p.strip())
    return outputs


def tokenize(text: str) -> set:
    """Lowercase word tokens (4+ chars to filter stopwords)."""
    return {w for w in re.findall(r"[a-z]{3,}", text.lower())}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <quality_dir>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    KV_TYPES = ["f16", "q8_0", "q4_0", "tbq4", "tbq3", "tbq2"]

    # outputs[model][kv] = [text1, text2, ..., text5]
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

    # Compute Jaccard similarity vs F16 baseline
    print("\n## Output Quality: Jaccard Similarity vs F16 Baseline\n")
    print("| Model | " + " | ".join(k for k in KV_TYPES if k != "f16") + " |")
    print("|---|" + "|".join("---:" for _ in range(len(KV_TYPES) - 1)) + "|")

    all_scores = defaultdict(list)
    for model in sorted(outputs.keys()):
        if "f16" not in outputs[model]:
            continue
        baseline = outputs[model]["f16"]
        baseline_tokens = [tokenize(t) for t in baseline]
        row = [model]
        for kv in KV_TYPES:
            if kv == "f16":
                continue
            if kv not in outputs[model]:
                row.append("—")
                continue
            test = outputs[model][kv]
            test_tokens = [tokenize(t) for t in test]
            # Compute per-prompt Jaccard, then average
            n = min(len(baseline_tokens), len(test_tokens))
            scores = [jaccard(baseline_tokens[i], test_tokens[i]) for i in range(n)]
            avg = sum(scores) / len(scores) if scores else 0.0
            all_scores[kv].append(avg)
            row.append(f"{avg:.3f}")
        print("| " + " | ".join(row) + " |")

    print("\n## Summary: Mean Jaccard vs F16 per KV type\n")
    print("| KV Type | Mean Jaccard | Interpretation |")
    print("|---|---:|---|")
    for kv in KV_TYPES:
        if kv == "f16":
            continue
        if kv in all_scores and all_scores[kv]:
            mean = sum(all_scores[kv]) / len(all_scores[kv])
            if mean > 0.5:
                interp = "high similarity — good"
            elif mean > 0.2:
                interp = "moderate — noticeable differences"
            else:
                interp = "low — severe quality degradation"
            print(f"| {kv} | {mean:.3f} | {interp} |")

    # Sample outputs (F16 vs TBQ4 vs TBQ3 for first prompt)
    print("\n## Sample Outputs (Prompt 1: 'The capital of France is')\n")
    for model in sorted(outputs.keys()):
        print(f"### {model}\n")
        for kv in ["f16", "tbq4", "tbq3", "tbq2"]:
            if kv in outputs[model] and outputs[model][kv]:
                text = outputs[model][kv][0][:200].replace("\n", " ")
                print(f"**{kv}**: `{text}...`\n")


if __name__ == "__main__":
    main()
