#!/usr/bin/env python3
"""Prompt sets for TurboQuant quality evaluation."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from claude_references import REFERENCES
except ModuleNotFoundError:
    from .claude_references import REFERENCES


@dataclass(frozen=True)
class PromptRecord:
    category: str
    prompt: str
    reference: str


SMOKE_PROMPTS = [
    PromptRecord(category="sentence_completion", prompt=prompt, reference=reference)
    for prompt, reference in REFERENCES.items()
]


PAPER_PROMPTS = [
    PromptRecord(
        category="sentence_completion",
        prompt="Complete the sentence with one factual sentence: The capital of France is",
        reference="The capital of France is Paris, the country's political and cultural center.",
    ),
    PromptRecord(
        category="closed_book_qa",
        prompt="Question: What process do plants use to convert sunlight, water, and carbon dioxide into sugar and oxygen? Answer in two sentences.",
        reference="Plants use photosynthesis. Chlorophyll captures light energy, which helps convert water and carbon dioxide into glucose while releasing oxygen.",
    ),
    PromptRecord(
        category="summary",
        prompt=(
            "Summarize the following passage in exactly two bullet points:\n\n"
            "A team tested several KV cache formats for CPU inference. F16 was stable but used the most memory. "
            "Q8 reduced memory and improved long-context speed. Q4 saved more memory but sometimes hurt quality. "
            "TBQ4 used non-uniform centroids and was fastest on Gemma 4 at 8K context, but still required quality validation."
        ),
        reference=(
            "- The passage compares F16, Q8, Q4, and TBQ4 KV cache formats for CPU inference.\n"
            "- TBQ4 was fastest on Gemma 4 at 8K context, but quality validation remains necessary."
        ),
    ),
    PromptRecord(
        category="reasoning",
        prompt="If a model generates 9.2 tokens/s and another generates 7.1 tokens/s, approximately what percent faster is the first? Show the calculation briefly.",
        reference="The speedup is (9.2 / 7.1 - 1) * 100, which is about 29.6%. The first model is roughly 30% faster.",
    ),
    PromptRecord(
        category="puzzle",
        prompt="A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost? Answer with the reasoning.",
        reference="The ball costs $0.05. If the ball costs x, the bat costs x + $1.00, so 2x + $1.00 = $1.10 and x = $0.05.",
    ),
    PromptRecord(
        category="description",
        prompt="Describe a quiet library reading room in three vivid but concise sentences.",
        reference="A quiet reading room has rows of desks, warm lamps, and shelves lining the walls. The air feels still except for soft page turns and pencil marks. Muted light and orderly books create a focused, calm atmosphere.",
    ),
    PromptRecord(
        category="code",
        prompt="Write a Python function named is_palindrome that returns True if a string is a palindrome after ignoring case and non-alphanumeric characters.",
        reference=(
            "def is_palindrome(text):\n"
            "    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())\n"
            "    return cleaned == cleaned[::-1]"
        ),
    ),
    PromptRecord(
        category="medical_safety",
        prompt="What are the main warning signs of a stroke, and what should someone do if they appear?",
        reference="Warning signs include face drooping, arm weakness, speech trouble, sudden confusion, vision problems, dizziness, loss of coordination, or a severe sudden headache. Call emergency services immediately because stroke treatment is time-sensitive.",
    ),
    PromptRecord(
        category="instruction_following",
        prompt="Give exactly three comma-separated colors that appear in a traffic light, with no extra words.",
        reference="red, yellow, green",
    ),
    PromptRecord(
        category="formatting",
        prompt="Return a JSON object with keys model, kv_cache, and recommendation for this statement: Gemma 4 E4B works well with TBQ4 at long context.",
        reference='{"model":"Gemma 4 E4B","kv_cache":"TBQ4","recommendation":"validate quality at long context"}',
    ),
]


HARD_PROMPTS = [
    PromptRecord(
        category="multi_constraint_reasoning",
        prompt=(
            "A CPU benchmark reports 7.07 tokens/s for F16 KV and 9.19 tokens/s for TBQ4 KV at 8K context. "
            "In exactly three sentences, compute the percent speedup, state whether the result alone proves quality is preserved, "
            "and name one additional evaluation needed."
        ),
        reference=(
            "The speedup is (9.19 / 7.07 - 1) * 100, which is about 30%. "
            "This speed result alone does not prove quality is preserved. "
            "A quality check such as perplexity, task accuracy, or human/LLM judging is still needed."
        ),
    ),
    PromptRecord(
        category="counterfactual_qa",
        prompt=(
            "Answer carefully: If all birds could swim but only some birds could fly, would 'can fly' be a reliable test for being a bird? "
            "Give a two-sentence answer and include the word 'No'."
        ),
        reference=(
            "No, flying would not be a reliable test for being a bird because only some birds can fly in this scenario. "
            "Swimming would be shared by all birds, but it would still not necessarily distinguish birds from other animals unless no other animals could swim."
        ),
    ),
    PromptRecord(
        category="structured_json",
        prompt=(
            "Return only valid JSON with keys answer, arithmetic, and caveat. "
            "Question: a 512-token cache uses 1.2 GB and an 8192-token cache scales linearly; how much memory is needed at 8192 tokens?"
        ),
        reference='{"answer":"19.2 GB","arithmetic":"1.2 * (8192 / 512) = 19.2","caveat":"linear scaling is an assumption"}',
    ),
    PromptRecord(
        category="instruction_following",
        prompt=(
            "Write exactly four bullet points. Each bullet must start with one of these labels in this order: Risk, Evidence, Mitigation, Next. "
            "Topic: using a fast K/V quantization result in a paper."
        ),
        reference=(
            "- Risk: A speed-only result can overstate the reliability of the quantization method.\n"
            "- Evidence: Report throughput together with perplexity and task-level quality metrics.\n"
            "- Mitigation: Use conservative claims and disclose model, hardware, context, and generation settings.\n"
            "- Next: Replicate on additional prompts, longer generations, and another CPU architecture."
        ),
    ),
    PromptRecord(
        category="summarization",
        prompt=(
            "Summarize this paragraph in exactly 35 to 45 words:\n"
            "TBQ4 improved long-context decode speed for Gemma 4 E4B on one Intel desktop CPU. "
            "However, the initial quality set used only five simple prompts and a short generation budget, making it hard to detect subtle degradation. "
            "The result is encouraging but not sufficient for a broad paper claim."
        ),
        reference=(
            "TBQ4 sped up long-context Gemma 4 E4B decoding on one Intel CPU, but the first quality test was too small and short to expose subtle regressions. "
            "The result is promising, yet broader evaluation is needed."
        ),
    ),
    PromptRecord(
        category="code_debugging",
        prompt=(
            "Fix this Python function and return only the corrected code:\n\n"
            "def mean(xs):\n"
            "    total = 0\n"
            "    for x in xs:\n"
            "        total += x\n"
            "    return total / len(x)\n"
        ),
        reference=(
            "def mean(xs):\n"
            "    total = 0\n"
            "    for x in xs:\n"
            "        total += x\n"
            "    return total / len(xs)"
        ),
    ),
    PromptRecord(
        category="logic_puzzle",
        prompt=(
            "Three boxes are labeled Apples, Oranges, and Mixed. Every label is wrong. "
            "You may draw one fruit from one box. Which box should you draw from to identify all boxes, and why?"
        ),
        reference=(
            "Draw from the box labeled Mixed. Since every label is wrong, that box contains only apples or only oranges; the fruit drawn reveals which. "
            "Then the remaining two boxes can be assigned by eliminating the labels that must be wrong."
        ),
    ),
    PromptRecord(
        category="medical_safety",
        prompt=(
            "A friend suddenly has one-sided arm weakness and slurred speech but says they want to sleep it off. "
            "Respond in two short paragraphs: first explain what to do now, then explain why."
        ),
        reference=(
            "Call emergency services immediately and do not let them sleep it off. Note the time symptoms began and keep them safe while waiting for help.\n\n"
            "One-sided weakness and slurred speech can be stroke symptoms, and stroke treatment is time-sensitive. Fast medical care can reduce brain injury and improve outcomes."
        ),
    ),
]


PROMPT_SETS = {
    "smoke": SMOKE_PROMPTS,
    "paper": PAPER_PROMPTS,
    "hard": HARD_PROMPTS,
}


def get_prompt_records(name: str) -> list[PromptRecord]:
    try:
        return PROMPT_SETS[name]
    except KeyError as exc:
        valid = ", ".join(sorted(PROMPT_SETS))
        raise ValueError(f"unknown prompt set {name!r}; valid options: {valid}") from exc
