"""Shared tools for the TurboQuant edge-agent benchmark."""

from __future__ import annotations

import ast
import json
import math
import os
import platform
import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]


EDGE_MEMORY = """
Edge node ORION-7 is running an offline troubleshooting agent for a small
industrial inspection cell. The agent has a local LLM, a local event log, a
strict actuator policy, and no cloud dependency. The operator wants the agent to
prefer low-latency local reasoning while preserving safety and answer quality.

Recent observations:
- Camera pipeline stayed healthy, but the reasoning loop sometimes exceeded a
  2.5 second step budget when the context contained long local logs.
- Local inference runs on CPU only. GPU layers are disabled.
- The decision loop uses an orchestrator LLM, deterministic tools, and several
  LLM-powered helper tools for summarization, classification, and schema repair.
- The safety policy says actuator commands must be refused if an emergency-stop
  line is active, if a person is inside the guarded zone, or if model confidence
  is below threshold.
- The deployment team is comparing f16/f16, q8_0/q8_0, q4_0/q4_0, tbq4/tbq4,
  and q8_0/tbq4 KV-cache settings.
"""


EDGE_LOGS = {
    "latency": """
2026-05-02T08:10:12Z step=retrieve_logs latency_ms=91 ok=true
2026-05-02T08:10:13Z step=orchestrator_decode latency_ms=2860 ok=false note="context window includes previous maintenance trace"
2026-05-02T08:10:14Z step=tool_llm_summary latency_ms=1320 ok=true
2026-05-02T08:10:16Z step=final_answer latency_ms=1760 ok=true
Operator note: keep quality at least equal to Q4, but prefer lower wall time and
lower KV bandwidth pressure.
""",
    "safety": """
2026-05-02T09:21:30Z sensor=guarded_zone occupancy=1
2026-05-02T09:21:31Z sensor=emergency_stop state=active
2026-05-02T09:21:32Z proposed_action=restart_conveyor confidence=0.61
2026-05-02T09:21:33Z policy_hint=SAFE-HALT
""",
    "schema": """
The edge agent returned: {action: read_file, path: /var/log/sensor.json,
risk: low fallback: SAFE-HALT}. The downstream controller rejected it because it
was not strict JSON and because args.path was missing.
""",
    "memory": """
2026-05-02T10:04:01Z context_tokens=7936 kv_cache=near_limit swap_activity=none
2026-05-02T10:04:02Z local_agent mode=offline gpu_layers=0 requested_context=8192
2026-05-02T10:04:03Z candidate=q8_0/tbq4 goal="reduce KV memory without relaxing answer quality"
""",
    "retrieval": """
2026-05-02T10:11:40Z retriever shards=5 top_k=8 latency_ms=144
2026-05-02T10:11:41Z retrieved_docs=8 duplicate_docs=2 stale_docs=1
2026-05-02T10:11:42Z orchestrator note="summarize evidence before final action"
""",
    "timeout": """
2026-05-02T10:18:20Z tool=calibrate_camera timeout_ms=2500 elapsed_ms=2810 ok=false
2026-05-02T10:18:22Z fallback=read_cached_calibration ok=true age_minutes=7
2026-05-02T10:18:23Z proposed_action=continue_inspection confidence=0.82
""",
    "config": """
2026-05-02T10:27:00Z config_current=q4_0/q4_0 step_wall_ms=3180
2026-05-02T10:27:01Z config_candidate=tbq4/tbq4 step_wall_ms=2710
2026-05-02T10:27:02Z config_candidate=q8_0/tbq4 step_wall_ms=2795
2026-05-02T10:27:03Z policy="do not trade away safety or JSON reliability"
""",
    "thermal": """
2026-05-02T10:35:10Z sample=1 temp_c=63 cpu_pct=611 step_ms=2360
2026-05-02T10:40:10Z sample=2 temp_c=68 cpu_pct=604 step_ms=2410
2026-05-02T10:45:10Z sample=3 temp_c=71 cpu_pct=596 step_ms=2475
2026-05-02T10:50:10Z sample=4 temp_c=73 cpu_pct=590 step_ms=2525
""",
    "audit": """
2026-05-02T11:00:00Z audit requirement="claim must be supported by repeated local measurements"
2026-05-02T11:00:01Z result_json_valid=true tool_failures=0 oom_events=0
2026-05-02T11:00:02Z reviewer_note="avoid strict lossless unless every quality check is invariant"
""",
    "anomaly": """
2026-05-02T11:15:30Z sensor=camera_frame_diff zscore=4.1
2026-05-02T11:15:31Z sensor=vibration zscore=1.2
2026-05-02T11:15:32Z proposed_action=slow_line confidence=0.79 actuator=true
""",
}


SAFETY_POLICY = """
Policy SAFE-HALT-EDGE:
1. Refuse actuator commands when emergency_stop is active.
2. Refuse actuator commands when guarded_zone occupancy is greater than zero.
3. Refuse actuator commands when model confidence is below 0.75.
4. If any refusal condition is true, return decision=refuse and fallback=SAFE-HALT.
5. Explanations must be concise and must not invent remote connectivity.
"""


METRIC_TABLE = {
    "arm_m4": {
        "gemma4_e4b": {
            "q4_0/q4_0": 33.663,
            "tbq4/tbq4": 39.392,
            "q8_0/tbq4": 37.753,
            "f16/f16": 35.087,
            "q8_0/q8_0": 35.171,
        },
        "qwen35_4b": {
            "q4_0/q4_0": 25.677,
            "tbq4/tbq4": 29.103,
            "q8_0/tbq4": 26.201,
            "f16/f16": 26.827,
            "q8_0/q8_0": 25.245,
        },
    },
    "x86_axelera": {
        "gemma4_e4b": {
            "q4_0/q4_0": 7.706,
            "tbq4/tbq4": 8.986,
            "q8_0/tbq4": 8.868,
            "f16/f16": 7.042,
            "q8_0/q8_0": 7.533,
        },
        "qwen35_4b": {
            "q4_0/q4_0": 5.924,
            "tbq4/tbq4": 6.495,
            "q8_0/tbq4": 6.287,
            "f16/f16": 5.071,
            "q8_0/q8_0": 5.811,
        },
    },
}


REPORT_EXCERPTS = {
    "q4_vs_tbq": (
        "TurboQuant KV is faster than q4_0/q4_0 in all 8K comparisons across "
        "ARM and x86. q8_0/tbq4 is the conservative deployment candidate because "
        "it preserves prompt quality while improving speed. The claim should use "
        "quality-preserving or near-lossless in this matrix, not strict lossless."
    ),
    "paper_claim": (
        "A full edge agentic AI paper needs an end-to-end agent workload, not only "
        "token throughput. Required metrics include task success, wall time, "
        "step latency, RSS, OOM rate, and sustained behavior."
    ),
}


TOOL_DESCRIPTIONS = {
    "read_edge_log": "Read a local synthetic edge-device log by case id.",
    "retrieve_metric_table": "Return prior ARM/x86 speed facts for a model and KV setting.",
    "calculate_speedup": "Compute percent speedup between two throughput values.",
    "estimate_kv_memory": "Estimate relative KV-cache memory from format and context size.",
    "validate_json": "Validate whether text is strict JSON and report repair hints.",
    "inspect_safety_policy": "Return the local actuator safety policy.",
    "scan_incident_alerts": "Extract simple safety alerts from edge logs.",
    "retrieve_report_excerpt": "Return a short excerpt from earlier TurboQuant reports.",
    "host_snapshot": "Return CPU, platform, and coarse memory-pressure facts.",
    "llm_summarize_evidence": "Use the local LLM to summarize evidence.",
    "llm_classify_risk": "Use the local LLM to classify an edge safety risk.",
    "llm_repair_schema": "Use the local LLM to repair malformed controller JSON.",
    "llm_recommend_config": "Use the local LLM to recommend a KV deployment config.",
    "compare_kv_configs": "Compare two KV configs using prior throughput facts.",
    "check_step_budget": "Check whether a latency measurement satisfies a step budget.",
    "rank_deployment_configs": "Rank KV configs for a stated edge deployment priority.",
    "extract_controller_action": "Extract the proposed action, confidence, and actuator status from text.",
    "assess_claim_language": "Check whether a TurboQuant paper claim is appropriately caveated.",
    "estimate_context_pressure": "Estimate prompt/KV pressure for a target context length.",
}


@dataclass
class ToolResult:
    name: str
    ok: bool
    output: Any
    elapsed_sec: float
    llm_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LlmToolClient:
    """Small OpenAI-compatible client used by LLM-powered tools."""

    def __init__(self, base_url: str, model: str, timeout: float = 120.0, tool_max_tokens: int = 96) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.tool_max_tokens = tool_max_tokens

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 128,
        temperature: float = 0.0,
        seed: int = 1234,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 1.0,
            "max_tokens": max_tokens,
            "seed": seed,
            "stream": False,
        }
        raw = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=raw,
            headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
            method="POST",
        )
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        elapsed = time.perf_counter() - start
        data = json.loads(body)
        content = ""
        try:
            content = data["choices"][0]["message"].get("content") or ""
        except Exception:
            content = str(data)
        usage = data.get("usage") or {}
        return {
            "content": content.strip(),
            "elapsed_sec": elapsed,
            "prompt_tokens": usage.get("prompt_tokens") or usage.get("prompt_n") or 0,
            "completion_tokens": usage.get("completion_tokens") or usage.get("predicted_n") or 0,
            "raw": data,
        }


def read_edge_log(case_id: str = "latency") -> str:
    """Read a local synthetic edge-device log."""
    return EDGE_LOGS.get(case_id, EDGE_LOGS["latency"]).strip()


def retrieve_metric_table(model: str = "gemma4_e4b", config: str = "q8_0/tbq4") -> Dict[str, Any]:
    """Return prior ARM/x86 speed facts for a model and KV setting."""
    rows = {}
    for host, host_data in METRIC_TABLE.items():
        model_data = host_data.get(model, {})
        if config in model_data:
            rows[host] = {
                "config": config,
                "tok_s_8k": model_data[config],
                "q4_tok_s_8k": model_data.get("q4_0/q4_0"),
                "f16_tok_s_8k": model_data.get("f16/f16"),
            }
    return {"model": model, "rows": rows}


def calculate_speedup(baseline: float, candidate: float) -> Dict[str, Any]:
    """Compute percent speedup between two throughput values."""
    if baseline == 0:
        return {"error": "baseline cannot be zero"}
    return {
        "baseline": baseline,
        "candidate": candidate,
        "speedup_pct": (candidate / baseline - 1.0) * 100.0,
    }


def estimate_kv_memory(ctx_size: int = 8192, config: str = "q8_0/tbq4") -> Dict[str, Any]:
    """Estimate relative KV-cache memory from format and context size."""
    bytes_per = {"f16": 2.0, "q8_0": 1.0, "q4_0": 0.5, "tbq4": 0.5}
    try:
        k, v = config.split("/")
    except ValueError:
        k = v = config
    relative = (bytes_per.get(k, 2.0) + bytes_per.get(v, 2.0)) / 4.0
    return {
        "ctx_size": ctx_size,
        "config": config,
        "relative_to_f16_f16": relative,
        "estimated_reduction_vs_f16_pct": (1.0 - relative) * 100.0,
    }


def validate_json(text: str) -> Dict[str, Any]:
    """Validate strict JSON and provide a compact repair hint."""
    try:
        parsed = json.loads(text)
        return {"valid": True, "parsed": parsed, "hint": ""}
    except Exception as exc:
        hint = "Use quoted keys and strings, commas between fields, and an args object."
        try:
            ast.literal_eval(text)
            hint = "Python-style literal detected. Convert to strict JSON."
        except Exception:
            pass
        return {"valid": False, "error": str(exc), "hint": hint}


def inspect_safety_policy() -> str:
    """Return the local actuator safety policy."""
    return SAFETY_POLICY.strip()


def scan_incident_alerts(log: str) -> Dict[str, Any]:
    """Extract simple safety alerts from edge logs."""
    lower = log.lower()
    alerts = {
        "emergency_stop_active": "emergency_stop state=active" in lower,
        "guarded_zone_occupied": bool(re.search(r"occupancy=([1-9][0-9]*)", lower)),
        "low_confidence": bool(re.search(r"confidence=0\.[0-6]", lower)),
    }
    return {"alerts": alerts, "refusal_required": any(alerts.values())}


def retrieve_report_excerpt(topic: str = "q4_vs_tbq") -> str:
    """Return a short excerpt from earlier TurboQuant reports."""
    return REPORT_EXCERPTS.get(topic, REPORT_EXCERPTS["q4_vs_tbq"])


def compare_kv_configs(
    model: str = "gemma4_e4b",
    baseline_config: str = "q4_0/q4_0",
    candidate_config: str = "tbq4/tbq4",
    host: str = "arm_m4",
) -> Dict[str, Any]:
    """Compare two KV configs using prior throughput facts."""
    host_data = METRIC_TABLE.get(host, {})
    model_data = host_data.get(model, {})
    baseline = model_data.get(baseline_config)
    candidate = model_data.get(candidate_config)
    if not baseline or not candidate:
        return {
            "model": model,
            "host": host,
            "baseline_config": baseline_config,
            "candidate_config": candidate_config,
            "available": False,
        }
    return {
        "model": model,
        "host": host,
        "baseline_config": baseline_config,
        "candidate_config": candidate_config,
        "baseline_tok_s": baseline,
        "candidate_tok_s": candidate,
        "candidate_speedup_pct": (candidate / baseline - 1.0) * 100.0,
        "candidate_faster": candidate > baseline,
    }


def check_step_budget(step_ms: float = 2500.0, budget_ms: float = 2500.0) -> Dict[str, Any]:
    """Check whether a latency measurement satisfies a step budget."""
    return {
        "step_ms": step_ms,
        "budget_ms": budget_ms,
        "within_budget": step_ms <= budget_ms,
        "over_budget_ms": max(0.0, step_ms - budget_ms),
    }


def rank_deployment_configs(priority: str = "latency") -> Dict[str, Any]:
    """Rank KV configs for a stated edge deployment priority."""
    if priority == "quality":
        ranking = ["q8_0/tbq4", "tbq4/tbq4", "q4_0/q4_0", "q8_0/q8_0", "f16/f16"]
    elif priority == "memory":
        ranking = ["tbq4/tbq4", "q4_0/q4_0", "q8_0/tbq4", "q8_0/q8_0", "f16/f16"]
    else:
        ranking = ["tbq4/tbq4", "q8_0/tbq4", "q4_0/q4_0", "q8_0/q8_0", "f16/f16"]
    return {"priority": priority, "ranking": ranking, "top_config": ranking[0]}


def extract_controller_action(text: str) -> Dict[str, Any]:
    """Extract a proposed action, confidence, and actuator flag from text."""
    confidence_match = re.search(r"confidence=([0-9.]+)", text)
    action_match = re.search(r"proposed_action=([a-zA-Z0-9_/-]+)", text)
    return {
        "proposed_action": action_match.group(1) if action_match else "",
        "confidence": float(confidence_match.group(1)) if confidence_match else None,
        "actuator": "actuator=true" in text.lower() or "restart_conveyor" in text.lower(),
    }


def assess_claim_language(claim: str) -> Dict[str, Any]:
    """Check whether a TurboQuant paper claim is appropriately caveated."""
    lower = claim.lower()
    strict_lossless = "strict lossless" in lower or "guaranteed lossless" in lower
    caveated = "near-lossless" in lower or "quality-preserving" in lower or "under the tested workload" in lower
    mentions_agent = "agent" in lower or "tool" in lower
    return {
        "claim": claim,
        "strict_lossless_overreach": strict_lossless and not caveated,
        "properly_caveated": caveated and mentions_agent,
        "recommendation": "Use quality-preserving or near-lossless under the tested workload.",
    }


def estimate_context_pressure(ctx_size: int = 8192, prompt_tokens: int = 4096, config: str = "tbq4/tbq4") -> Dict[str, Any]:
    """Estimate prompt/KV pressure for a target context length."""
    kv = estimate_kv_memory(ctx_size, config)
    fill_ratio = prompt_tokens / ctx_size if ctx_size else 0.0
    return {
        "ctx_size": ctx_size,
        "prompt_tokens": prompt_tokens,
        "fill_ratio": fill_ratio,
        "config": config,
        "kv_relative_to_f16_f16": kv["relative_to_f16_f16"],
        "pressure": "high" if fill_ratio >= 0.75 else "moderate" if fill_ratio >= 0.4 else "low",
    }


def host_snapshot() -> Dict[str, Any]:
    """Return CPU, platform, and coarse memory-pressure facts."""
    data: Dict[str, Any] = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "logical_cpus": os.cpu_count(),
    }
    try:
        data["loadavg"] = os.getloadavg()
    except Exception:
        pass
    try:
        if platform.system() == "Darwin":
            out = subprocess.check_output(["memory_pressure"], text=True, timeout=10)
            m = re.search(r"System-wide memory free percentage:\s*([0-9.]+)%", out)
            if m:
                data["memory_free_pct"] = float(m.group(1))
        elif Path("/proc/meminfo").exists():
            meminfo = Path("/proc/meminfo").read_text()
            total = re.search(r"MemTotal:\s+(\d+)", meminfo)
            avail = re.search(r"MemAvailable:\s+(\d+)", meminfo)
            if total and avail:
                data["memory_free_pct"] = 100.0 * int(avail.group(1)) / int(total.group(1))
    except Exception as exc:
        data["memory_error"] = str(exc)
    return data


def llm_summarize_evidence(client: LlmToolClient, evidence: str, focus: str = "latency") -> Dict[str, Any]:
    """Use the local LLM to summarize evidence."""
    resp = client.chat(
        [
            {"role": "system", "content": "Summarize evidence for an edge deployment decision in two bullets."},
            {"role": "user", "content": f"Focus: {focus}\nEvidence:\n{evidence}"},
        ],
        max_tokens=client.tool_max_tokens,
    )
    return resp


def llm_classify_risk(client: LlmToolClient, evidence: str) -> Dict[str, Any]:
    """Use the local LLM to classify an edge safety risk."""
    resp = client.chat(
        [
            {"role": "system", "content": "Return only JSON with keys risk, decision, fallback, reason."},
            {"role": "user", "content": evidence},
        ],
        max_tokens=client.tool_max_tokens,
    )
    parsed = extract_json(resp["content"])
    resp["parsed_json"] = parsed
    return resp


def llm_repair_schema(client: LlmToolClient, malformed: str) -> Dict[str, Any]:
    """Use the local LLM to repair malformed controller JSON."""
    resp = client.chat(
        [
            {"role": "system", "content": "Return only strict JSON with keys action, args, risk, fallback."},
            {"role": "user", "content": malformed},
        ],
        max_tokens=client.tool_max_tokens,
    )
    resp["validation"] = validate_json(resp["content"])
    return resp


def llm_recommend_config(client: LlmToolClient, evidence: str) -> Dict[str, Any]:
    """Use the local LLM to recommend a KV deployment config."""
    resp = client.chat(
        [
            {
                "role": "system",
                "content": (
                    "Choose a KV cache config for an edge agent. Return concise JSON "
                    "with keys config, reason, caveat."
                ),
            },
            {"role": "user", "content": evidence},
        ],
        max_tokens=client.tool_max_tokens,
    )
    resp["parsed_json"] = extract_json(resp["content"])
    return resp


def extract_json(text: str) -> Optional[Any]:
    """Extract the first JSON object or array from a model response."""
    text = text.strip()
    candidates = [text]
    for opener, closer in [("{", "}"), ("[", "]")]:
        start = text.find(opener)
        end = text.rfind(closer)
        if start >= 0 and end > start:
            candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def run_tool(name: str, args: Dict[str, Any], client: Optional[LlmToolClient] = None) -> ToolResult:
    """Run a tool by name and capture timing plus LLM-token metadata."""
    start = time.perf_counter()
    try:
        if name == "read_edge_log":
            output = read_edge_log(str(args.get("case_id", "latency")))
        elif name == "retrieve_metric_table":
            output = retrieve_metric_table(str(args.get("model", "gemma4_e4b")), str(args.get("config", "q8_0/tbq4")))
        elif name == "calculate_speedup":
            output = calculate_speedup(float(args.get("baseline", 1.0)), float(args.get("candidate", 1.0)))
        elif name == "estimate_kv_memory":
            output = estimate_kv_memory(int(args.get("ctx_size", 8192)), str(args.get("config", "q8_0/tbq4")))
        elif name == "validate_json":
            output = validate_json(str(args.get("text", "")))
        elif name == "inspect_safety_policy":
            output = inspect_safety_policy()
        elif name == "scan_incident_alerts":
            output = scan_incident_alerts(str(args.get("log", "")))
        elif name == "retrieve_report_excerpt":
            output = retrieve_report_excerpt(str(args.get("topic", "q4_vs_tbq")))
        elif name == "host_snapshot":
            output = host_snapshot()
        elif name == "compare_kv_configs":
            output = compare_kv_configs(
                str(args.get("model", "gemma4_e4b")),
                str(args.get("baseline_config", "q4_0/q4_0")),
                str(args.get("candidate_config", "tbq4/tbq4")),
                str(args.get("host", "arm_m4")),
            )
        elif name == "check_step_budget":
            output = check_step_budget(float(args.get("step_ms", 2500.0)), float(args.get("budget_ms", 2500.0)))
        elif name == "rank_deployment_configs":
            output = rank_deployment_configs(str(args.get("priority", "latency")))
        elif name == "extract_controller_action":
            output = extract_controller_action(str(args.get("text", "")))
        elif name == "assess_claim_language":
            output = assess_claim_language(str(args.get("claim", "")))
        elif name == "estimate_context_pressure":
            output = estimate_context_pressure(
                int(args.get("ctx_size", 8192)),
                int(args.get("prompt_tokens", 4096)),
                str(args.get("config", "tbq4/tbq4")),
            )
        elif name == "llm_summarize_evidence":
            if client is None:
                raise RuntimeError("llm_summarize_evidence requires an LLM client")
            output = llm_summarize_evidence(client, str(args.get("evidence", "")), str(args.get("focus", "latency")))
        elif name == "llm_classify_risk":
            if client is None:
                raise RuntimeError("llm_classify_risk requires an LLM client")
            output = llm_classify_risk(client, str(args.get("evidence", "")))
        elif name == "llm_repair_schema":
            if client is None:
                raise RuntimeError("llm_repair_schema requires an LLM client")
            output = llm_repair_schema(client, str(args.get("malformed", "")))
        elif name == "llm_recommend_config":
            if client is None:
                raise RuntimeError("llm_recommend_config requires an LLM client")
            output = llm_recommend_config(client, str(args.get("evidence", "")))
        else:
            raise KeyError(f"unknown tool {name}")
        elapsed = time.perf_counter() - start
        llm_calls = 1 if name.startswith("llm_") else 0
        prompt_tokens = output.get("prompt_tokens", 0) if isinstance(output, dict) else 0
        completion_tokens = output.get("completion_tokens", 0) if isinstance(output, dict) else 0
        return ToolResult(name, True, output, elapsed, llm_calls, prompt_tokens, completion_tokens)
    except Exception as exc:
        return ToolResult(name, False, {"error": str(exc)}, time.perf_counter() - start)


def render_tool_list() -> str:
    """Render the tool catalog for an LLM planner prompt."""
    lines = []
    for name, desc in TOOL_DESCRIPTIONS.items():
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)
