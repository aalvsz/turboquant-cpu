"""Google ADK entry point for the TurboQuant edge-agent benchmark.

The measured benchmark uses run_agent_benchmark.py so it can run without
optional packages. This module provides an ADK-compatible LlmAgent definition
over the same tool catalog for interactive inspection with `adk run` or
`adk web`.
"""

from __future__ import annotations

import os

from .tools import (
    estimate_kv_memory,
    host_snapshot,
    inspect_safety_policy,
    read_edge_log,
    retrieve_metric_table,
    retrieve_report_excerpt,
    scan_incident_alerts,
    validate_json,
)


ADK_IMPORT_ERROR = None
try:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
except Exception as exc:  # pragma: no cover - exercised only when ADK is installed.
    LlmAgent = None
    LiteLlm = None
    ADK_IMPORT_ERROR = exc


INSTRUCTION = """
You are TurboQuantEdgeEvaluator, an offline edge-agent orchestrator.

Your sole purpose is to compare KV-cache deployment options for local CPU LLM
agents. Use tools when they provide local evidence. Prefer concise, structured
answers with: decision, evidence, caveats, and next_action.

Do not claim TurboQuant is strictly lossless. Use "quality-preserving in this
matrix" or "near-lossless in this benchmark suite" when the evidence supports it.
"""


if LlmAgent is not None:
    root_agent = LlmAgent(
        name="turboquant_edge_evaluator",
        model=LiteLlm(model=os.environ.get("TQ_ADK_MODEL", "openai/gemma4_e4b")),
        description="Evaluates TurboQuant KV-cache options for edge agentic AI workloads.",
        instruction=INSTRUCTION,
        tools=[
            read_edge_log,
            retrieve_metric_table,
            estimate_kv_memory,
            validate_json,
            inspect_safety_policy,
            scan_incident_alerts,
            retrieve_report_excerpt,
            host_snapshot,
        ],
    )
else:
    root_agent = None

