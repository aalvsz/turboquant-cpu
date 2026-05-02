#!/usr/bin/env python3
"""Run a local edge-agent workload across TurboQuant KV configurations."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from turboquant_agent.tools import (
    EDGE_LOGS,
    EDGE_MEMORY,
    LlmToolClient,
    ToolResult,
    extract_json,
    render_tool_list,
    run_tool,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVER_BIN = (
    REPO_ROOT
    / "benchmark_results/fresh_edge_agentic_20260501/src/llama.cpp/"
    / "build-arm-qwen35-tbq4-qualityfix/bin/llama-server"
)
DEFAULT_MODEL_PATHS = {
    "gemma4_e4b": "/Users/ander.alvarez/Downloads/gemma-4-E4B-it-Q4_0.gguf",
    "qwen35_4b": "/Users/ander.alvarez/Downloads/Qwen3.5-4B-Q4_0.gguf",
}

KV_CONFIGS = [
    ("f16", "f16", "f16/f16"),
    ("q8_0", "q8_0", "q8_0/q8_0"),
    ("q4_0", "q4_0", "q4_0/q4_0"),
    ("tbq4", "tbq4", "tbq4/tbq4"),
    ("q8_0", "tbq4", "q8_0/tbq4"),
]


TASKS = [
    {
        "id": "latency_triage",
        "goal": (
            "Investigate why ORION-7 exceeded the edge-agent step budget and "
            "recommend whether TurboQuant should replace Q4 for the KV cache."
        ),
        "default_tools": [
            {"name": "read_edge_log", "args": {"case_id": "latency"}},
            {"name": "retrieve_metric_table", "args": {"model": "{model}", "config": "q8_0/tbq4"}},
            {"name": "retrieve_report_excerpt", "args": {"topic": "q4_vs_tbq"}},
            {"name": "llm_summarize_evidence", "args": {"evidence": "{context}", "focus": "latency and Q4 comparison"}},
            {"name": "llm_recommend_config", "args": {"evidence": "{context}"}},
        ],
    },
    {
        "id": "safety_gate",
        "goal": (
            "Decide whether the agent may restart the conveyor after the local "
            "safety log reports an emergency-stop and guarded-zone event."
        ),
        "default_tools": [
            {"name": "read_edge_log", "args": {"case_id": "safety"}},
            {"name": "inspect_safety_policy", "args": {}},
            {"name": "scan_incident_alerts", "args": {"log": "{context}"}},
            {"name": "llm_classify_risk", "args": {"evidence": "{context}"}},
        ],
    },
    {
        "id": "schema_repair",
        "goal": (
            "Repair the malformed controller JSON from the edge agent and explain "
            "whether the repaired action should be allowed."
        ),
        "default_tools": [
            {"name": "read_edge_log", "args": {"case_id": "schema"}},
            {"name": "validate_json", "args": {"text": "{context}"}},
            {"name": "llm_repair_schema", "args": {"malformed": "{context}"}},
            {"name": "inspect_safety_policy", "args": {}},
        ],
    },
    {
        "id": "memory_deploy",
        "goal": (
            "Estimate whether q8_0/tbq4 reduces KV memory pressure enough for an "
            "8K context edge agent while preserving a conservative quality posture."
        ),
        "default_tools": [
            {"name": "estimate_kv_memory", "args": {"ctx_size": 8192, "config": "q8_0/tbq4"}},
            {"name": "estimate_kv_memory", "args": {"ctx_size": 8192, "config": "q4_0/q4_0"}},
            {"name": "host_snapshot", "args": {}},
            {"name": "retrieve_report_excerpt", "args": {"topic": "paper_claim"}},
            {"name": "llm_recommend_config", "args": {"evidence": "{context}"}},
        ],
    },
    {
        "id": "paper_claim",
        "goal": (
            "Draft the strongest publishable claim supported by the CPU and agent "
            "evidence, including one caveat that prevents overstating losslessness."
        ),
        "default_tools": [
            {"name": "retrieve_report_excerpt", "args": {"topic": "q4_vs_tbq"}},
            {"name": "retrieve_report_excerpt", "args": {"topic": "paper_claim"}},
            {"name": "retrieve_metric_table", "args": {"model": "{model}", "config": "tbq4/tbq4"}},
            {"name": "llm_summarize_evidence", "args": {"evidence": "{context}", "focus": "paper claim"}},
        ],
    },
]

TASK_LOG_CASE = {
    "latency_triage": "latency",
    "safety_gate": "safety",
    "schema_repair": "schema",
}


@dataclass
class ServerRun:
    proc: subprocess.Popen
    stdout_path: Path
    stderr_path: Path
    max_rss_kb: int = 0
    stop_monitor: bool = False
    monitor_thread: Optional[threading.Thread] = None


def run_quiet(cmd: List[str], timeout: float = 20.0) -> str:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def memory_free_pct() -> Optional[float]:
    if platform.system() == "Darwin":
        out = run_quiet(["memory_pressure"], timeout=10)
        m = re.search(r"System-wide memory free percentage:\s*([0-9.]+)%", out)
        return float(m.group(1)) if m else None
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        data = meminfo.read_text()
        total = re.search(r"MemTotal:\s+(\d+)", data)
        avail = re.search(r"MemAvailable:\s+(\d+)", data)
        if total and avail:
            return 100.0 * int(avail.group(1)) / int(total.group(1))
    return None


def preflight_memory(min_free_pct: float, label: str) -> Dict[str, Any]:
    pct = memory_free_pct()
    snap = {
        "label": label,
        "free_pct": pct,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if pct is not None and pct < min_free_pct:
        raise SystemExit(f"Refusing to start {label}: free memory {pct:.1f}% < {min_free_pct:.1f}%")
    return snap


def find_free_port(start: int) -> int:
    for port in range(start, start + 200):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("no free local port found")


def sample_rss_kb(pid: int) -> int:
    try:
        out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True, timeout=5)
        return int((out.strip() or "0").split()[0])
    except Exception:
        return 0


def monitor_rss(server: ServerRun) -> None:
    while not server.stop_monitor and server.proc.poll() is None:
        server.max_rss_kb = max(server.max_rss_kb, sample_rss_kb(server.proc.pid))
        time.sleep(0.5)


def http_get_json(url: str, timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body) if body else {}
    except Exception:
        return None


def wait_for_server(base_url: str, proc: subprocess.Popen, timeout: float = 120.0) -> None:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server exited early with code {proc.returncode}: {last_error}")
        data = http_get_json(base_url + "/health")
        if data is not None:
            status = str(data.get("status", "")).lower()
            if status in ("ok", "ready", "idle") or not status:
                return
        models = http_get_json(base_url + "/v1/models")
        if models is not None:
            return
        time.sleep(0.5)
    raise RuntimeError(f"server did not become ready at {base_url}")


def start_server(
    args: argparse.Namespace,
    out_dir: Path,
    model_name: str,
    model_path: str,
    type_k: str,
    type_v: str,
    label: str,
    port: int,
) -> ServerRun:
    preflight_memory(args.min_memory_free_pct, f"{model_name} {label}")
    stdout_path = out_dir / "server.stdout.log"
    stderr_path = out_dir / "server.stderr.log"
    stdout = stdout_path.open("w")
    stderr = stderr_path.open("w")
    cmd = [
        str(args.server_bin),
        "-m",
        model_path,
        "-t",
        str(args.threads),
        "-tb",
        str(args.threads_batch),
        "-c",
        str(args.ctx_size),
        "-ctk",
        type_k,
        "-ctv",
        type_v,
        "-fa",
        "on",
        "-ngl",
        "0",
        "-np",
        "1",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--no-webui",
        "--log-disable",
        "-a",
        model_name,
    ]
    if model_name.startswith("qwen"):
        cmd.extend(["--reasoning-budget", "0"])
    (out_dir / "server_command.json").write_text(json.dumps(cmd, indent=2))
    proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, text=True)
    server = ServerRun(proc=proc, stdout_path=stdout_path, stderr_path=stderr_path)
    server.monitor_thread = threading.Thread(target=monitor_rss, args=(server,), daemon=True)
    server.monitor_thread.start()
    try:
        wait_for_server(f"http://127.0.0.1:{port}", proc, timeout=args.server_timeout)
    except Exception:
        stop_server(server)
        raise
    return server


def stop_server(server: ServerRun) -> None:
    server.stop_monitor = True
    if server.proc.poll() is None:
        server.proc.terminate()
        try:
            server.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.proc.kill()
            server.proc.wait(timeout=10)
    server.max_rss_kb = max(server.max_rss_kb, sample_rss_kb(server.proc.pid))
    if server.monitor_thread:
        server.monitor_thread.join(timeout=2)


def substitute(value: Any, model: str, context: str) -> Any:
    if isinstance(value, str):
        return value.replace("{model}", model).replace("{context}", context)
    if isinstance(value, dict):
        return {k: substitute(v, model, context) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute(v, model, context) for v in value]
    return value


def plan_tools(
    client: LlmToolClient,
    task: Dict[str, Any],
    model_name: str,
    context: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    default_plan = substitute(task["default_tools"], model_name, context)
    prompt = (
        f"{EDGE_MEMORY}\n\n"
        f"Task id: {task['id']}\nGoal: {task['goal']}\n\n"
        "Available tools:\n"
        f"{render_tool_list()}\n\n"
        "Choose 2 to 5 tools. Return only strict JSON in this schema:\n"
        "{\"tools\":[{\"name\":\"tool_name\",\"args\":{}}],\"rationale\":\"short\"}."
    )
    resp = client.chat(
        [
            {
                "role": "system",
                "content": "You are an edge LLM agent orchestrator. Select tools, do not answer the task yet.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=220,
    )
    parsed = extract_json(resp["content"])
    if isinstance(parsed, dict) and isinstance(parsed.get("tools"), list):
        tools = []
        for item in parsed["tools"][:5]:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                tools.append({"name": item["name"], "args": item.get("args") or {}})
        if tools:
            return tools, {"plan_valid": True, "planner_response": resp, "parsed": parsed}
    return default_plan, {"plan_valid": False, "planner_response": resp, "parsed": parsed, "fallback_plan": default_plan}


def compact_tool_output(result: ToolResult) -> str:
    data = {
        "tool": result.name,
        "ok": result.ok,
        "output": result.output,
        "elapsed_sec": round(result.elapsed_sec, 4),
    }
    text = json.dumps(data, ensure_ascii=True)
    return text[:1200]


def final_answer(client: LlmToolClient, task: Dict[str, Any], tool_results: List[ToolResult]) -> Dict[str, Any]:
    evidence = "\n".join(compact_tool_output(r) for r in tool_results)
    prompt = (
        f"{EDGE_MEMORY}\n\nTask id: {task['id']}\nGoal: {task['goal']}\n\n"
        f"Tool evidence:\n{evidence}\n\n"
        "Return only strict minified JSON with keys decision, evidence, caveats, next_action. "
        "Each value must be a short string. Do not use markdown fences."
    )
    return client.chat(
        [
            {
                "role": "system",
                "content": (
                    "You are the final response stage of an edge agent. Use only tool evidence. "
                    "Do not claim strict losslessness."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=240,
    )


def score_task(task_id: str, text: str) -> Dict[str, Any]:
    lower = text.lower()
    checks = []
    if task_id == "latency_triage":
        checks = ["tbq" in lower, "q4" in lower, "speed" in lower or "latency" in lower]
    elif task_id == "safety_gate":
        checks = ["refuse" in lower or "safe-halt" in lower, "emergency" in lower, "guard" in lower]
    elif task_id == "schema_repair":
        parsed = extract_json(text)
        checks = [parsed is not None, "args" in lower, "safe-halt" in lower or "refuse" in lower]
    elif task_id == "memory_deploy":
        checks = ["q8_0/tbq4" in lower or "tbq" in lower, "memory" in lower or "kv" in lower, "8k" in lower or "8192" in lower]
    elif task_id == "paper_claim":
        checks = ["quality" in lower, "lossless" in lower, "agent" in lower or "edge" in lower]
    score = sum(1 for item in checks if item) / len(checks) if checks else 0.0
    return {"score": score, "checks": checks, "final_json_valid": extract_json(text) is not None}


def run_task(
    client: LlmToolClient,
    task: Dict[str, Any],
    model_name: str,
    events,
) -> Dict[str, Any]:
    task_start = time.perf_counter()
    context_parts = [EDGE_MEMORY]
    log_case = TASK_LOG_CASE.get(task["id"])
    if log_case:
        context_parts.append(EDGE_LOGS[log_case])
    context = "\n".join(context_parts)
    planned_tools, plan_meta = plan_tools(client, task, model_name, context)
    if not any(str(item.get("name", "")).startswith("llm_") for item in planned_tools):
        default_llm_tools = [
            item for item in substitute(task["default_tools"], model_name, context)
            if str(item.get("name", "")).startswith("llm_")
        ]
        if default_llm_tools:
            if len(planned_tools) >= 5:
                planned_tools[-1] = default_llm_tools[0]
            else:
                planned_tools.append(default_llm_tools[0])
            plan_meta["policy_added_llm_tool"] = True
    else:
        plan_meta["policy_added_llm_tool"] = False
    llm_calls = 1
    prompt_tokens = int(plan_meta["planner_response"].get("prompt_tokens") or 0)
    completion_tokens = int(plan_meta["planner_response"].get("completion_tokens") or 0)
    tool_results: List[ToolResult] = []
    for planned in planned_tools:
        name = planned.get("name")
        args = substitute(planned.get("args") or {}, model_name, context)
        if name == "read_edge_log" and not args.get("case_id"):
            args["case_id"] = log_case or "latency"
        if name == "retrieve_metric_table":
            args.setdefault("model", model_name)
            args.setdefault("config", "q8_0/tbq4")
        if name == "scan_incident_alerts" and not args.get("log"):
            args["log"] = context
        if name == "validate_json" and not args.get("text"):
            args["text"] = context
        if name == "llm_repair_schema" and not args.get("malformed"):
            args["malformed"] = context
        if name in ("llm_summarize_evidence", "llm_classify_risk", "llm_recommend_config") and not args.get("evidence"):
            args["evidence"] = context
        result = run_tool(str(name), args, client)
        tool_results.append(result)
        llm_calls += result.llm_calls
        prompt_tokens += result.prompt_tokens
        completion_tokens += result.completion_tokens
        events.write(json.dumps({"event": "tool", "task_id": task["id"], "tool": result.__dict__}, default=str) + "\n")
    final = final_answer(client, task, tool_results)
    llm_calls += 1
    prompt_tokens += int(final.get("prompt_tokens") or 0)
    completion_tokens += int(final.get("completion_tokens") or 0)
    final_text = final["content"]
    score = score_task(task["id"], final_text)
    elapsed = time.perf_counter() - task_start
    row = {
        "task_id": task["id"],
        "wall_sec": elapsed,
        "plan_valid": plan_meta["plan_valid"],
        "policy_added_llm_tool": plan_meta.get("policy_added_llm_tool", False),
        "planned_tool_count": len(planned_tools),
        "executed_tool_count": len(tool_results),
        "tool_success_count": sum(1 for r in tool_results if r.ok),
        "llm_calls": llm_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "score": score["score"],
        "final_json_valid": score["final_json_valid"],
        "final_text": final_text,
        "planned_tools": json.dumps(planned_tools, ensure_ascii=True),
    }
    events.write(json.dumps({"event": "task", "row": row}, ensure_ascii=True) + "\n")
    events.flush()
    return row


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    def avg(key: str) -> float:
        vals = [float(r[key]) for r in rows if r.get(key) not in (None, "")]
        return sum(vals) / len(vals) if vals else 0.0

    total_wall = sum(float(r["wall_sec"]) for r in rows)
    total_completion = sum(int(r["completion_tokens"]) for r in rows)
    return {
        "tasks": len(rows),
        "total_wall_sec": total_wall,
        "mean_wall_sec": avg("wall_sec"),
        "mean_score": avg("score"),
        "plan_valid_rate": avg("plan_valid"),
        "final_json_valid_rate": avg("final_json_valid"),
        "total_llm_calls": sum(int(r["llm_calls"]) for r in rows),
        "total_prompt_tokens": sum(int(r["prompt_tokens"]) for r in rows),
        "total_completion_tokens": total_completion,
        "completion_tokens_per_sec": total_completion / total_wall if total_wall else 0.0,
    }


def parse_model_args(items: List[str]) -> Dict[str, str]:
    models = dict(DEFAULT_MODEL_PATHS)
    for item in items:
        name, sep, path = item.partition("=")
        if not sep:
            raise SystemExit(f"bad --model {item!r}; expected name=/path/model.gguf")
        models[name] = path
    return models


def selected_configs(spec: str) -> List[Tuple[str, str, str]]:
    wanted = {x.strip() for x in spec.split(",") if x.strip()}
    if not wanted or "all" in wanted:
        return KV_CONFIGS
    aliases = {
        "f16": "f16/f16",
        "q8": "q8_0/q8_0",
        "q8_0": "q8_0/q8_0",
        "q4": "q4_0/q4_0",
        "q4_0": "q4_0/q4_0",
        "tbq4": "tbq4/tbq4",
        "q8_0_tbq4": "q8_0/tbq4",
    }
    normalized = {aliases.get(x, x) for x in wanted}
    return [cfg for cfg in KV_CONFIGS if cfg[2] in normalized]


def write_run_report(out_root: Path, summary_rows: List[Dict[str, Any]], task_rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# TurboQuant Edge-Agent Benchmark Report",
        "",
        f"Run folder: `{out_root}`",
        "",
        "## Summary",
        "",
        "| model | config | tasks | mean score | total wall s | completion tok/s | plan valid | final JSON valid | max RSS MB |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['config']} | {row['tasks']} | "
            f"{float(row['mean_score']):.3f} | {float(row['total_wall_sec']):.3f} | "
            f"{float(row['completion_tokens_per_sec']):.3f} | "
            f"{float(row['plan_valid_rate']):.3f} | {float(row['final_json_valid_rate']):.3f} | "
            f"{float(row['server_max_rss_mb']):.1f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- This is an end-to-end local agent workload: an orchestrator LLM selects tools, deterministic tools run locally, LLM-powered tools call the same local model, and a final LLM step synthesizes the answer.",
        "- Lower wall time is better. Mean score is a lightweight task-success proxy, not a substitute for human or benchmark-grade judging.",
        "- A config is a good edge-agent candidate only if it improves latency without reducing task score or JSON/tool discipline.",
        "",
        "## Task Suite",
        "",
        "| task | purpose |",
        "|---|---|",
    ])
    for task in TASKS:
        lines.append(f"| {task['id']} | {task['goal']} |")
    out_root.joinpath("AGENT_REPORT.md").write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-bin", type=Path, default=DEFAULT_SERVER_BIN)
    parser.add_argument("--model", action="append", default=[], help="name=/path/model.gguf; defaults include Gemma 4 and Qwen3.5")
    parser.add_argument("--models", default="gemma4_e4b,qwen35_4b")
    parser.add_argument("--kv-configs", default="all")
    parser.add_argument("--host-label", default="m4_max")
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--threads-batch", type=int, default=10)
    parser.add_argument("--ctx-size", type=int, default=8192)
    parser.add_argument("--port-base", type=int, default=18100)
    parser.add_argument("--server-timeout", type=float, default=180.0)
    parser.add_argument("--min-memory-free-pct", type=float, default=15.0)
    parser.add_argument("--out-root", type=Path, default=None)
    parser.add_argument("--limit-tasks", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.server_bin.exists():
        raise SystemExit(f"server binary not found: {args.server_bin}")
    models = parse_model_args(args.model)
    selected_models = [m.strip() for m in args.models.split(",") if m.strip()]
    for model in selected_models:
        if model not in models:
            raise SystemExit(f"unknown model {model}; known: {', '.join(sorted(models))}")
        if not Path(models[model]).exists():
            raise SystemExit(f"model path not found for {model}: {models[model]}")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + args.host_label
    out_root = args.out_root or (Path(__file__).resolve().parent / "results" / run_id)
    out_root.mkdir(parents=True, exist_ok=True)
    metadata = {
        "run_id": run_id,
        "host_label": args.host_label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "server_bin": str(args.server_bin),
        "server_version": run_quiet([str(args.server_bin), "--version"]),
        "models": {m: models[m] for m in selected_models},
        "kv_configs": [cfg[2] for cfg in selected_configs(args.kv_configs)],
        "threads": args.threads,
        "threads_batch": args.threads_batch,
        "ctx_size": args.ctx_size,
        "initial_memory": preflight_memory(args.min_memory_free_pct, "initial benchmark"),
    }
    out_root.joinpath("metadata.json").write_text(json.dumps(metadata, indent=2))

    task_suite = TASKS[: args.limit_tasks] if args.limit_tasks > 0 else TASKS
    all_task_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    port = args.port_base
    for model_name in selected_models:
        for type_k, type_v, config_label in selected_configs(args.kv_configs):
            tag = f"{model_name}_{config_label.replace('/', '_')}"
            combo_dir = out_root / "raw" / tag
            combo_dir.mkdir(parents=True, exist_ok=True)
            port = find_free_port(port)
            server = start_server(args, combo_dir, model_name, models[model_name], type_k, type_v, config_label, port)
            client = LlmToolClient(f"http://127.0.0.1:{port}/v1", model_name, timeout=180.0)
            rows: List[Dict[str, Any]] = []
            try:
                warm = client.chat(
                    [
                        {"role": "system", "content": "Return exactly OK."},
                        {"role": "user", "content": "Health check."},
                    ],
                    max_tokens=8,
                )
                combo_dir.joinpath("warmup.json").write_text(json.dumps(warm, indent=2, default=str))
                with (combo_dir / "events.jsonl").open("w") as events:
                    for task in task_suite:
                        row = run_task(client, task, model_name, events)
                        row.update({
                            "host_label": args.host_label,
                            "model": model_name,
                            "config": config_label,
                            "type_k": type_k,
                            "type_v": type_v,
                        })
                        rows.append(row)
                        all_task_rows.append(row)
            finally:
                stop_server(server)
            write_csv(combo_dir / "tasks.csv", rows)
            summary = summarize_rows(rows)
            summary.update({
                "host_label": args.host_label,
                "model": model_name,
                "config": config_label,
                "type_k": type_k,
                "type_v": type_v,
                "server_max_rss_mb": server.max_rss_kb / 1024.0,
                "server_returncode": server.proc.returncode,
                "raw_dir": str(combo_dir),
            })
            summary_rows.append(summary)
            write_csv(out_root / "summary.csv", summary_rows)
            write_csv(out_root / "tasks.csv", all_task_rows)
            port += 1
    write_run_report(out_root, summary_rows, all_task_rows)
    print(out_root)


if __name__ == "__main__":
    main()
