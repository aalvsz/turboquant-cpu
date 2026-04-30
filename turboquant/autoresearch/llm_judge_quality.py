#!/usr/bin/env python3
"""Judge KV-quantized generations with an OpenAI LLM judge.

The default judge model is gpt-5.5. Set OPENAI_API_KEY before running.

Inputs can be JSONL produced by paper_quality_generate.py, or legacy
llama-cli text directories produced by the older quality scripts.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claude_references import REFERENCES  # noqa: E402


API_URL_DEFAULT = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.5"


@dataclass(frozen=True)
class Generation:
    model: str
    setting: str
    tag: str
    prompt_id: int
    prompt: str
    reference: str
    output: str
    source: str


JUDGE_INSTRUCTIONS = """You are evaluating LLM outputs produced with different KV cache quantization settings.

Score the candidate response for the user's prompt. Use the reference answer as guidance, not as a required wording.
If an F16 baseline is provided, use it only to understand the expected behavior for this model and prompt.
Penalize factual errors, missing required content, incoherence, repetition, prompt echoing, malformed code, and unsafe medical advice.
Do not reward verbosity by itself. Prefer concise, correct, coherent answers.
Return only the structured JSON requested by the schema."""


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "correctness": {"type": "integer", "minimum": 0, "maximum": 5},
        "completeness": {"type": "integer", "minimum": 0, "maximum": 5},
        "coherence": {"type": "integer", "minimum": 0, "maximum": 5},
        "safety": {"type": "integer", "minimum": 0, "maximum": 5},
        "degenerate": {"type": "boolean"},
        "major_errors": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
    },
    "required": [
        "correctness",
        "completeness",
        "coherence",
        "safety",
        "degenerate",
        "major_errors",
        "rationale",
    ],
}


TAG_ORDER = [
    "q8_0_tbq4",
    "q8_0_q4_0",
    "f16",
    "q8_0",
    "q4_0",
    "tbq4",
    "tbq3",
    "tbq2",
]


def setting_from_tag(tag: str) -> str:
    if tag == "q8_0_tbq4":
        return "q8_0/tbq4"
    if tag == "q8_0_q4_0":
        return "q8_0/q4_0"
    return f"{tag}/{tag}"


def tag_from_setting(setting: str) -> str:
    return setting.replace("/", "_")


def clean_generation_text(raw: str, prompt: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    text = re.sub(r"\n\[\s*Prompt:.*?\]\s*", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\nExiting\.\.\.\s*$", "", text)
    marker = f"> {prompt}"
    if marker in text:
        text = text.split(marker, 1)[1]
    text = re.sub(r"(?s)^.*?available commands:.*?\n\n", "", text)
    return text.strip()


def parse_legacy_file(path: Path) -> list[tuple[int, str, str]]:
    content = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^### Prompt (\d+): (.+)$", content, flags=re.MULTILINE)
    outputs = []
    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break
        prompt_id = int(parts[i])
        prompt = parts[i + 1].strip()
        block = parts[i + 2]
        outputs.append((prompt_id, prompt, clean_generation_text(block, prompt)))
    return outputs


def parse_legacy_name(path: Path) -> tuple[str, str, str] | None:
    stem = path.stem
    match = re.match(r"(.+)_K([^_].*?)_V(.+)$", stem)
    if match:
        model, type_k, type_v = match.groups()
        setting = f"{type_k}/{type_v}"
        return model, setting, tag_from_setting(setting)

    for tag in TAG_ORDER:
        suffix = "_" + tag
        if stem.endswith(suffix):
            model = stem[: -len(suffix)]
            setting = setting_from_tag(tag)
            return model, setting, tag
    return None


def load_generations_from_jsonl(paths: list[Path]) -> list[Generation]:
    generations = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                prompt = row["prompt"]
                setting = row.get("setting") or f"{row['type_k']}/{row['type_v']}"
                generations.append(
                    Generation(
                        model=row["model"],
                        setting=setting,
                        tag=row.get("tag", tag_from_setting(setting)),
                        prompt_id=int(row.get("prompt_id", 0)),
                        prompt=prompt,
                        reference=row.get("reference", REFERENCES.get(prompt, "")),
                        output=row.get("output", ""),
                        source=f"{path}:{line_no}",
                    )
                )
    return generations


def load_generations_from_legacy_dirs(paths: list[Path]) -> list[Generation]:
    generations = []
    for directory in paths:
        for path in sorted(directory.glob("*.txt")):
            parsed = parse_legacy_name(path)
            if parsed is None:
                print(f"skip unrecognized legacy file: {path}", file=sys.stderr)
                continue
            model, setting, tag = parsed
            for prompt_id, prompt, output in parse_legacy_file(path):
                generations.append(
                    Generation(
                        model=model,
                        setting=setting,
                        tag=tag,
                        prompt_id=prompt_id,
                        prompt=prompt,
                        reference=REFERENCES.get(prompt, ""),
                        output=output,
                        source=str(path),
                    )
                )
    return generations


def response_output_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    chunks = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def call_openai_judge(
    api_key: str,
    api_url: str,
    model: str,
    generation: Generation,
    baseline_output: str,
    reasoning_effort: str,
    timeout_sec: int,
) -> dict:
    user_payload = {
        "model_under_test": generation.model,
        "kv_setting": generation.setting,
        "prompt": generation.prompt,
        "reference_answer": generation.reference,
        "f16_baseline_output": baseline_output,
        "candidate_output": generation.output,
    }
    request_payload = {
        "model": model,
        "instructions": JUDGE_INSTRUCTIONS,
        "input": json.dumps(user_payload, ensure_ascii=True, indent=2),
        "reasoning": {"effort": reasoning_effort},
        "text": {
            "format": {
                "type": "json_schema",
                "name": "kv_quality_judgment",
                "strict": True,
                "schema": SCHEMA,
            }
        },
    }
    data = json.dumps(request_payload).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error {exc.code}: {detail}") from exc
    response = json.loads(body)
    text = response_output_text(response)
    try:
        judgment = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"judge returned non-JSON text: {text[:500]}") from exc
    judgment["_response_id"] = response.get("id", "")
    judgment["_usage"] = response.get("usage", {})
    return judgment


def existing_keys(path: Path) -> set[tuple[str, str, int]]:
    keys = set()
    if not path.exists():
        return keys
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            keys.add((row["model"], row["setting"], int(row["prompt_id"])))
    return keys


def semantic_quality(row: dict) -> float:
    return (
        0.45 * float(row["correctness"])
        + 0.25 * float(row["completeness"])
        + 0.20 * float(row["coherence"])
        + 0.10 * float(row["safety"])
    )


def write_summary(judgments_path: Path, summary_path: Path) -> None:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with judgments_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            groups[(row["model"], row["setting"])].append(row)

    rows = []
    for (model, setting), items in sorted(groups.items()):
        rows.append(
            {
                "model": model,
                "setting": setting,
                "n": len(items),
                "mean_correctness": f"{sum(float(x['correctness']) for x in items) / len(items):.3f}",
                "mean_completeness": f"{sum(float(x['completeness']) for x in items) / len(items):.3f}",
                "mean_coherence": f"{sum(float(x['coherence']) for x in items) / len(items):.3f}",
                "mean_safety": f"{sum(float(x['safety']) for x in items) / len(items):.3f}",
                "mean_semantic_quality": f"{sum(semantic_quality(x) for x in items) / len(items):.3f}",
                "degenerate_rate": f"{sum(1 for x in items if x['degenerate']) / len(items):.3f}",
            }
        )
    if not rows:
        return
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", action="append", default=[], help="Generation JSONL file.")
    parser.add_argument("--legacy-dir", action="append", default=[], help="Legacy quality output directory.")
    parser.add_argument("--output", default="turboquant/results/paper_quality/llm_judgments.jsonl")
    parser.add_argument("--summary", default="turboquant/results/paper_quality/llm_judge_summary.csv")
    parser.add_argument("--model", default=os.environ.get("OPENAI_JUDGE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-url", default=os.environ.get("OPENAI_RESPONSES_URL", API_URL_DEFAULT))
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--sleep-sec", type=float, default=0.2)
    parser.add_argument("--max-items", type=int, default=0)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    jsonl_paths = [Path(p) for p in args.jsonl]
    legacy_dirs = [Path(p) for p in args.legacy_dir]
    generations = load_generations_from_jsonl(jsonl_paths) + load_generations_from_legacy_dirs(legacy_dirs)
    if not generations:
        raise SystemExit("no generations loaded")

    baselines = {
        (g.model, g.prompt_id): g.output
        for g in generations
        if g.setting in {"f16/f16", "f16"}
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    done = set() if args.no_resume else existing_keys(output_path)
    pending = [g for g in generations if (g.model, g.setting, g.prompt_id) not in done]
    if args.max_items > 0:
        pending = pending[: args.max_items]

    print(f"loaded={len(generations)} pending={len(pending)} judge_model={args.model}")
    if args.dry_run:
        first = pending[0]
        print(
            json.dumps(
                {
                    "model": first.model,
                    "setting": first.setting,
                    "prompt": first.prompt,
                    "reference_chars": len(first.reference),
                    "baseline_chars": len(baselines.get((first.model, first.prompt_id), "")),
                    "candidate_chars": len(first.output),
                    "api_url": args.api_url,
                    "judge_model": args.model,
                },
                indent=2,
            )
        )
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is unset; use --dry-run to inspect payloads without calling the API")

    with output_path.open("a", encoding="utf-8") as out:
        for generation in pending:
            baseline_output = baselines.get((generation.model, generation.prompt_id), "")
            judgment = call_openai_judge(
                api_key=api_key,
                api_url=args.api_url,
                model=args.model,
                generation=generation,
                baseline_output=baseline_output,
                reasoning_effort=args.reasoning_effort,
                timeout_sec=args.timeout_sec,
            )
            row = {
                "judge_model": args.model,
                "model": generation.model,
                "setting": generation.setting,
                "tag": generation.tag,
                "prompt_id": generation.prompt_id,
                "prompt": generation.prompt,
                "source": generation.source,
                **judgment,
            }
            out.write(json.dumps(row, ensure_ascii=True) + "\n")
            out.flush()
            time.sleep(args.sleep_sec)

    write_summary(output_path, Path(args.summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
