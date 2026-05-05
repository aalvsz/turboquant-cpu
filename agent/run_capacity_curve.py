#!/usr/bin/env python3
"""Run context/concurrency capacity curves for CPU-only KV-cache configs."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import platform
import random
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from run_agent_benchmark import (
    KV_CONFIGS,
    energy_joules_from_uj_samples,
    find_free_port,
    linux_rapl_max_energy_range_uj,
    preflight_memory,
    sample_host_telemetry,
    sample_proc,
    server_version_major,
    server_version_text,
    wait_for_server,
    write_csv,
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


@dataclass
class ServerRun:
    proc: subprocess.Popen
    stdout_path: Path
    stderr_path: Path
    server_version: str
    stop_monitor: bool = False
    killed_for_rss: bool = False
    max_rss_kb: int = 0
    max_cpu_pct: float = 0.0
    samples: List[Dict[str, Any]] = field(default_factory=list)
    monitor_thread: Optional[threading.Thread] = None


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
        "q8_tbq4": "q8_0/tbq4",
        "q8_0/tbq4": "q8_0/tbq4",
    }
    labels = {aliases.get(item, item) for item in wanted}
    selected = [cfg for cfg in KV_CONFIGS if cfg[2] in labels]
    missing = labels - {cfg[2] for cfg in selected}
    if missing:
        raise SystemExit(f"unknown kv config(s): {', '.join(sorted(missing))}")
    return selected


def parse_int_list(spec: str, default: List[int]) -> List[int]:
    if not spec.strip():
        return default
    values = [int(item.strip()) for item in spec.split(",") if item.strip()]
    return values or default


def memory_snapshot() -> Dict[str, Any]:
    if platform.system() == "Linux":
        meminfo = Path("/proc/meminfo")
        if meminfo.exists():
            data = meminfo.read_text()
            out: Dict[str, Any] = {}
            for key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
                match = re.search(rf"{key}:\s+(\d+)", data)
                if match:
                    out[key.lower() + "_mb"] = int(match.group(1)) / 1024.0
            if out.get("memtotal_mb"):
                out["memavailable_pct"] = 100.0 * out.get("memavailable_mb", 0.0) / out["memtotal_mb"]
            return out
    return {}


def monitor_server(server: ServerRun, interval: float, telemetry: bool, max_rss_mb: float) -> None:
    while not server.stop_monitor and server.proc.poll() is None:
        rss, cpu = sample_proc(server.proc.pid)
        server.max_rss_kb = max(server.max_rss_kb, rss)
        server.max_cpu_pct = max(server.max_cpu_pct, cpu)
        row: Dict[str, Any] = {
            "elapsed_sec": round(time.time(), 3),
            "rss_kb": rss,
            "cpu_pct": cpu,
        }
        if telemetry:
            row.update(sample_host_telemetry())
        server.samples.append(row)
        if max_rss_mb > 0 and rss / 1024.0 > max_rss_mb:
            server.killed_for_rss = True
            server.proc.terminate()
            return
        time.sleep(interval)


def http_post_json(url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    raw = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def prompt_text(ctx_size: int, fill_ratio: float, worker_id: int) -> str:
    base = (
        "You are an offline CPU-only edge agent for an industrial inspection cell. "
        "Select a safe KV-cache deployment decision from local evidence only. "
        "The system compares f16/f16, q4_0/q4_0, q8_0/q8_0, tbq4/tbq4, and q8_0/tbq4. "
        "Prioritize low latency, no OOM, no throttling, and valid JSON. "
        f"Worker id: {worker_id}.\n"
    )
    trace = (
        "local_trace ts=2026-05-05 cpu_only=true tool_loop=true "
        "event=maintenance_log kv_pressure=active safety_policy=SAFE-HALT "
        "observation=long_context_agent_step budget_ms=2500 "
        "candidate_tbq4=reduce_kv_bandwidth candidate_f16=fast_when_memory_fits "
        "candidate_q4=memory_saving_baseline "
    )
    target_chars = max(len(base), int(ctx_size * 4 * fill_ratio))
    chunks = [base]
    while sum(len(item) for item in chunks) < target_chars:
        chunks.append(trace)
    return "".join(chunks)[:target_chars]


def parse_json_text(text: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        return True, json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return False, {}
        try:
            return True, json.loads(match.group(0))
        except Exception:
            return False, {}


def run_request(base_url: str, model: str, ctx_size: int, fill_ratio: float, max_tokens: int, timeout: float, worker_id: int) -> Dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "Return strict JSON with keys decision, evidence, caveats, next_action. "
                "Do not include markdown. Each value must be at most 10 words."
            ),
        },
        {
            "role": "user",
            "content": (
                prompt_text(ctx_size, fill_ratio, worker_id)
                + "\nReturn a compact deployment decision. Keep every field short."
            ),
        },
    ]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": max_tokens,
        "seed": 9000 + worker_id,
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "capacity_decision",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "decision": {"type": "string"},
                        "evidence": {"type": "string"},
                        "caveats": {"type": "string"},
                        "next_action": {"type": "string"},
                    },
                    "required": ["decision", "evidence", "caveats", "next_action"],
                },
            },
        },
    }
    start = time.perf_counter()
    try:
        data = http_post_json(base_url + "/v1/chat/completions", payload, timeout)
        elapsed = time.perf_counter() - start
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        valid, parsed = parse_json_text(content)
        usage = data.get("usage") or {}
        return {
            "worker_id": worker_id,
            "ok": True,
            "error": "",
            "wall_sec": elapsed,
            "json_valid": valid,
            "decision": parsed.get("decision", "") if valid else "",
            "prompt_tokens": int(usage.get("prompt_tokens") or usage.get("prompt_n") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or usage.get("predicted_n") or 0),
            "content": content,
        }
    except Exception as exc:
        return {
            "worker_id": worker_id,
            "ok": False,
            "error": repr(exc),
            "wall_sec": time.perf_counter() - start,
            "json_valid": False,
            "decision": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "content": "",
        }


def stop_server(server: ServerRun, out_dir: Path) -> Dict[str, Any]:
    server.stop_monitor = True
    if server.proc.poll() is None:
        server.proc.terminate()
        try:
            server.proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.proc.kill()
            server.proc.wait(timeout=10)
    if server.monitor_thread:
        server.monitor_thread.join(timeout=2)
    write_csv(out_dir / "profiler_samples.csv", server.samples)
    thermal_values = [float(s["thermal_max_c"]) for s in server.samples if s.get("thermal_max_c") not in (None, "")]
    throttled_values = [int(float(s["vcgencmd_throttled"])) for s in server.samples if s.get("vcgencmd_throttled") not in (None, "")]
    energy_samples = [
        (float(s["elapsed_sec"]), float(s["rapl_package_energy_uj"]))
        for s in server.samples
        if s.get("rapl_package_energy_uj") not in (None, "")
    ]
    pkg_joules = 0.0
    pkg_watts = 0.0
    if len(energy_samples) >= 2:
        pkg_joules, pkg_watts = energy_joules_from_uj_samples(energy_samples, linux_rapl_max_energy_range_uj())
    return {
        "server_returncode": server.proc.returncode,
        "server_max_rss_mb": server.max_rss_kb / 1024.0,
        "server_max_cpu_pct": server.max_cpu_pct,
        "server_profile_samples": len(server.samples),
        "thermal_max_c": max(thermal_values) if thermal_values else 0.0,
        "vcgencmd_throttled_last": throttled_values[-1] if throttled_values else 0,
        "vcgencmd_throttled_or": int(any(throttled_values)) if throttled_values else 0,
        "rapl_package_joules": pkg_joules,
        "rapl_package_watts_avg": pkg_watts,
        "killed_for_rss": server.killed_for_rss,
    }


def start_server(args: argparse.Namespace, out_dir: Path, model_name: str, model_path: str, type_k: str, type_v: str, label: str, ctx_size: int, concurrency: int, port: int) -> ServerRun:
    version_text = server_version_text(args.server_bin)
    if model_name.startswith("qwen") and not args.allow_legacy_qwen_server:
        major = server_version_major(version_text)
        if major is None or major < args.min_qwen_server_version:
            raise SystemExit("Refusing Qwen run with unverified llama-server; pass --allow-legacy-qwen-server for diagnosis.")
    total_ctx = ctx_size * concurrency
    preflight_memory(args.min_memory_free_pct, f"{model_name} {label} ctx={ctx_size} concurrency={concurrency}")
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
        str(total_ctx),
        "-ctk",
        type_k,
        "-ctv",
        type_v,
        "-fa",
        "on",
        "-ngl",
        "0",
        "-np",
        str(concurrency),
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
        cmd.extend(["--jinja", "--reasoning-budget", "0"])
    (out_dir / "server_command.json").write_text(json.dumps(cmd, indent=2))
    (out_dir / "server_version.txt").write_text(version_text + "\n")
    proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, text=True)
    stdout.close()
    stderr.close()
    server = ServerRun(proc=proc, stdout_path=stdout_path, stderr_path=stderr_path, server_version=version_text)
    server.monitor_thread = threading.Thread(
        target=monitor_server,
        args=(server, args.profile_interval, args.telemetry, args.max_rss_mb),
        daemon=True,
    )
    server.monitor_thread.start()
    try:
        wait_for_server(f"http://127.0.0.1:{port}", proc, timeout=args.server_timeout)
    except Exception:
        stop_server(server, out_dir)
        raise
    return server


def summarize_requests(rows: List[Dict[str, Any]], batch_wall_sec: float) -> Dict[str, Any]:
    request_times = sorted(float(r["wall_sec"]) for r in rows)
    ok_rows = [r for r in rows if r.get("ok")]
    total_prompt = sum(int(r.get("prompt_tokens") or 0) for r in rows)
    total_completion = sum(int(r.get("completion_tokens") or 0) for r in rows)
    p95 = request_times[min(len(request_times) - 1, int(0.95 * (len(request_times) - 1)))] if request_times else 0.0
    return {
        "requests": len(rows),
        "ok_requests": len(ok_rows),
        "error_requests": len(rows) - len(ok_rows),
        "json_valid_rate": sum(1 for r in rows if r.get("json_valid")) / len(rows) if rows else 0.0,
        "batch_wall_sec": batch_wall_sec,
        "mean_request_wall_sec": sum(request_times) / len(request_times) if request_times else 0.0,
        "p95_request_wall_sec": p95,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "prompt_tokens_per_sec": total_prompt / batch_wall_sec if batch_wall_sec > 0 else 0.0,
        "completion_tokens_per_sec": total_completion / batch_wall_sec if batch_wall_sec > 0 else 0.0,
    }


def write_report(out_root: Path, rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# KV-Cache Capacity Curve Report",
        "",
        f"Run folder: `{out_root}`",
        "",
        "| model | config | ctx/agent | concurrency | total ctx | ok | errors | JSON | wall s | mean req s | RSS MB | temp C | throttle | killed |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['config']} | {row['ctx_size']} | {row['concurrency']} | {row['server_ctx_total']} | "
            f"{row['ok_requests']} | {row['error_requests']} | {float(row['json_valid_rate']):.3f} | "
            f"{float(row['batch_wall_sec']):.3f} | {float(row['mean_request_wall_sec']):.3f} | "
            f"{float(row['server_max_rss_mb']):.1f} | {float(row.get('thermal_max_c') or 0.0):.1f} | "
            f"0x{int(float(row.get('vcgencmd_throttled_or') or 0)):x} | {int(bool(row.get('killed_for_rss')))} |"
        )
    lines.extend([
        "",
        "Lower wall time is better within a fixed context/concurrency cell. Rows killed by the RSS guard are capacity failures, not latency wins.",
        "The server context is `ctx/agent * concurrency` so each parallel slot has the target per-agent context budget.",
    ])
    out_root.joinpath("CAPACITY_CURVE_REPORT.md").write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-bin", type=Path, default=DEFAULT_SERVER_BIN)
    parser.add_argument("--model", action="append", default=[], help="name=/path/model.gguf")
    parser.add_argument("--models", default="qwen35_4b")
    parser.add_argument("--kv-configs", default="f16,q4,tbq4,q8_tbq4")
    parser.add_argument("--host-label", default="capacity_host")
    parser.add_argument("--threads", type=int, default=max(1, os.cpu_count() or 4))
    parser.add_argument("--threads-batch", type=int, default=max(1, os.cpu_count() or 4))
    parser.add_argument("--ctx-sizes", default="4096,8192,12288,16384")
    parser.add_argument("--concurrency", default="1,2,3")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--context-fill-ratio", type=float, default=0.35)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--port-base", type=int, default=19100)
    parser.add_argument("--server-timeout", type=float, default=240.0)
    parser.add_argument("--min-memory-free-pct", type=float, default=12.0)
    parser.add_argument("--max-rss-mb", type=float, default=7600.0)
    parser.add_argument("--profile-interval", type=float, default=1.0)
    parser.add_argument("--telemetry", action="store_true")
    parser.add_argument("--allow-legacy-qwen-server", action="store_true")
    parser.add_argument("--min-qwen-server-version", type=int, default=6)
    parser.add_argument("--shuffle-seed", type=int, default=20260505)
    parser.add_argument("--no-randomize-order", dest="randomize_order", action="store_false")
    parser.add_argument("--out-root", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.server_bin.exists():
        raise SystemExit(f"server binary not found: {args.server_bin}")
    models = parse_model_args(args.model)
    selected_models = [m.strip() for m in args.models.split(",") if m.strip()]
    for model_name in selected_models:
        if model_name not in models:
            raise SystemExit(f"unknown model {model_name}; known: {', '.join(sorted(models))}")
        if not Path(models[model_name]).exists():
            raise SystemExit(f"model path not found for {model_name}: {models[model_name]}")
    ctx_sizes = parse_int_list(args.ctx_sizes, [4096, 8192])
    concurrencies = parse_int_list(args.concurrency, [1])
    configs = selected_configs(args.kv_configs)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + args.host_label
    out_root = args.out_root or (Path(__file__).resolve().parent / "results" / run_id)
    out_root.mkdir(parents=True, exist_ok=True)
    jobs = [
        {
            "repeat": repeat,
            "ctx_size": ctx_size,
            "concurrency": concurrency,
            "model_name": model_name,
            "type_k": type_k,
            "type_v": type_v,
            "config_label": config_label,
        }
        for repeat in range(1, args.repeats + 1)
        for model_name in selected_models
        for ctx_size in ctx_sizes
        for concurrency in concurrencies
        for type_k, type_v, config_label in configs
    ]
    if args.randomize_order:
        random.Random(args.shuffle_seed).shuffle(jobs)
    metadata = {
        "run_id": run_id,
        "host_label": args.host_label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "server_bin": str(args.server_bin),
        "server_version": server_version_text(args.server_bin),
        "models": {m: models[m] for m in selected_models},
        "kv_configs": [cfg[2] for cfg in configs],
        "ctx_sizes": ctx_sizes,
        "concurrency": concurrencies,
        "repeats": args.repeats,
        "context_fill_ratio": args.context_fill_ratio,
        "max_tokens": args.max_tokens,
        "threads": args.threads,
        "threads_batch": args.threads_batch,
        "telemetry": args.telemetry,
        "max_rss_mb": args.max_rss_mb,
        "initial_memory": memory_snapshot(),
        "job_count": len(jobs),
    }
    out_root.joinpath("metadata.json").write_text(json.dumps(metadata, indent=2))
    summary_rows: List[Dict[str, Any]] = []
    request_rows: List[Dict[str, Any]] = []
    port = args.port_base
    for job_index, job in enumerate(jobs, start=1):
        model_name = job["model_name"]
        config_label = job["config_label"]
        ctx_size = int(job["ctx_size"])
        concurrency = int(job["concurrency"])
        repeat = int(job["repeat"])
        tag = f"ctx{ctx_size}_c{concurrency}_r{repeat:02d}_{model_name}_{config_label.replace('/', '_')}"
        combo_dir = out_root / "raw" / f"{job_index:04d}_{tag}"
        combo_dir.mkdir(parents=True, exist_ok=True)
        port = find_free_port(port)
        before_memory = memory_snapshot()
        server: Optional[ServerRun] = None
        row_base = {
            "job_index": job_index,
            "host_label": args.host_label,
            "repeat": repeat,
            "model": model_name,
            "config": config_label,
            "type_k": job["type_k"],
            "type_v": job["type_v"],
            "ctx_size": ctx_size,
            "concurrency": concurrency,
            "server_ctx_total": ctx_size * concurrency,
            "context_fill_ratio": args.context_fill_ratio,
            "raw_dir": str(combo_dir),
            "memavailable_mb_before": before_memory.get("memavailable_mb", 0.0),
            "memavailable_pct_before": before_memory.get("memavailable_pct", 0.0),
        }
        try:
            server = start_server(
                args,
                combo_dir,
                model_name,
                models[model_name],
                str(job["type_k"]),
                str(job["type_v"]),
                config_label,
                ctx_size,
                concurrency,
                port,
            )
            warmup = run_request(f"http://127.0.0.1:{port}", model_name, min(ctx_size, 1024), 0.05, 8, args.timeout, 0)
            combo_dir.joinpath("warmup.json").write_text(json.dumps(warmup, indent=2))
            start = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [
                    pool.submit(
                        run_request,
                        f"http://127.0.0.1:{port}",
                        model_name,
                        ctx_size,
                        args.context_fill_ratio,
                        args.max_tokens,
                        args.timeout,
                        worker_id,
                    )
                    for worker_id in range(1, concurrency + 1)
                ]
                rows = [future.result() for future in concurrent.futures.as_completed(futures)]
            batch_wall = time.perf_counter() - start
            for request_row in rows:
                request_row.update(row_base)
                request_rows.append(request_row)
            write_csv(combo_dir / "requests.csv", rows)
            summary = summarize_requests(rows, batch_wall)
            summary.update(row_base)
        except Exception as exc:
            summary = {
                **row_base,
                "requests": concurrency,
                "ok_requests": 0,
                "error_requests": concurrency,
                "json_valid_rate": 0.0,
                "batch_wall_sec": 0.0,
                "mean_request_wall_sec": 0.0,
                "p95_request_wall_sec": 0.0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "prompt_tokens_per_sec": 0.0,
                "completion_tokens_per_sec": 0.0,
                "error": repr(exc),
            }
            combo_dir.joinpath("error.txt").write_text(repr(exc) + "\n")
        finally:
            profile = {}
            if server is not None:
                profile = stop_server(server, combo_dir)
            summary.update(profile)
            after_memory = memory_snapshot()
            summary["memavailable_mb_after"] = after_memory.get("memavailable_mb", 0.0)
            summary["memavailable_pct_after"] = after_memory.get("memavailable_pct", 0.0)
            summary["server_version"] = " ".join((server.server_version if server else metadata["server_version"]).split())
            summary_rows.append(summary)
            write_csv(out_root / "summary.csv", summary_rows)
            write_csv(out_root / "requests.csv", request_rows)
            write_report(out_root, summary_rows)
        port += 1
    print(out_root)


if __name__ == "__main__":
    main()
