#!/usr/bin/env python3
import argparse
import csv
import glob
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path


KV_CONFIGS = [
    ("f16", "f16", "f16/f16"),
    ("q8_0", "q8_0", "q8_0/q8_0"),
    ("q4_0", "q4_0", "q4_0/q4_0"),
    ("tbq4", "tbq4", "tbq4/tbq4"),
    ("q8_0", "tbq4", "q8_0/tbq4"),
]

SUSTAINED_CONFIGS = [
    ("f16", "f16", "f16/f16"),
    ("tbq4", "tbq4", "tbq4/tbq4"),
    ("q8_0", "tbq4", "q8_0/tbq4"),
]

PROMPTS = [
    {
        "id": 1,
        "category": "speedup_reasoning",
        "prompt": (
            "A CPU benchmark reports 7.07 tokens/s for F16 KV and 9.19 tokens/s "
            "for TBQ4 KV at 8K context. In exactly three sentences, compute the "
            "percent speedup, state whether speed alone proves quality is preserved, "
            "and name one additional evaluation needed."
        ),
        "reference": "About 30% speedup; speed alone is not quality evidence; use PPL, task accuracy, or judging.",
    },
    {
        "id": 2,
        "category": "agent_tool_json",
        "prompt": (
            "Return only valid JSON. You are an edge agent that must check a local "
            "sensor file before sending an alert. Use keys action, args, risk, and "
            "fallback. The action must be read_file and args.path must be "
            "\"/var/log/sensor.json\"."
        ),
        "reference": "{\"action\":\"read_file\",\"args\":{\"path\":\"/var/log/sensor.json\"},\"risk\":\"...\",\"fallback\":\"...\"}",
    },
    {
        "id": 3,
        "category": "code_repair",
        "prompt": (
            "Return only Python code. Fix this function so it returns the nth "
            "Fibonacci number for n >= 0:\n\n"
            "def fib(n):\n"
            "    a, b = 0, 1\n"
            "    for i in range(n):\n"
            "        a = b\n"
            "        b = a + b\n"
            "    return b\n"
        ),
        "reference": "def fib(n): loop updates a, b = b, a + b and returns a",
    },
    {
        "id": 4,
        "category": "medical_safety",
        "prompt": (
            "A user says: \"My father suddenly has face drooping, arm weakness, "
            "and slurred speech.\" Reply in under 80 words with urgent, safe advice."
        ),
        "reference": "Call emergency services immediately, note onset time, do not drive, keep safe.",
    },
    {
        "id": 5,
        "category": "long_context_recall",
        "prompt": (
            "Read the incident notes and answer with exactly three bullet points.\n\n"
            "Incident notes: The edge device is named ORION-7. The local inference "
            "service listens on port 8137. The fallback policy is SAFE-HALT. The "
            "operator contact is Mira. The battery threshold for stopping noncritical "
            "agent loops is 18 percent. Several unrelated notes mention ports 8080, "
            "9000, and 11434, but those are not the local inference service.\n\n"
            "Question: identify the device, the inference port, and the fallback policy."
        ),
        "reference": "ORION-7; 8137; SAFE-HALT",
    },
    {
        "id": 6,
        "category": "constrained_summary",
        "prompt": (
            "Summarize in exactly 35 to 45 words:\n"
            "TurboQuant may reduce KV-cache bandwidth pressure during CPU LLM decode, "
            "but deployment claims require evidence across model families, hardware, "
            "quality metrics, sustained workloads, and agent-style instruction adherence."
        ),
        "reference": "A 35-45 word summary preserving the need for broad evidence.",
    },
    {
        "id": 7,
        "category": "labeled_bullets",
        "prompt": (
            "Write exactly four bullet points. The bullets must start, in order, "
            "with Risk:, Evidence:, Mitigation:, Next:. Topic: using TurboQuant KV "
            "on edge agentic AI."
        ),
        "reference": "Four labeled bullets in the requested order.",
    },
    {
        "id": 8,
        "category": "arithmetic_json",
        "prompt": (
            "Return only valid JSON with keys answer_gb, arithmetic, and caveat. "
            "Question: a 512-token KV cache uses 1.2 GB and an 8192-token cache "
            "scales linearly; how many GB are needed at 8192 tokens?"
        ),
        "reference": "19.2 GB because 8192 / 512 = 16 and 1.2 * 16 = 19.2",
    },
    {
        "id": 9,
        "category": "agent_plan",
        "prompt": (
            "Create a concise five-step plan for an offline edge troubleshooting "
            "agent. Include one step for checking local logs, one for verifying "
            "model health, and one for refusing unsafe actuator commands."
        ),
        "reference": "Five steps including logs, model health, and unsafe command refusal.",
    },
    {
        "id": 10,
        "category": "needle_recall",
        "prompt": (
            "Context: alpha red 14; beta green 29; gamma blue 73; delta yellow 41; "
            "epsilon black 62. The secret calibration token is KAPPA-314159. "
            "More filler: alpha beta gamma delta epsilon. What is the secret "
            "calibration token? Return only the token."
        ),
        "reference": "KAPPA-314159",
    },
]


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_quiet(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        return p.stdout.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def read_energy_uj():
    vals = []
    for p in glob.glob("/sys/class/powercap/intel-rapl:*"):
        f = os.path.join(p, "energy_uj")
        try:
            with open(f) as fh:
                vals.append(int(fh.read().strip()))
        except Exception:
            pass
    return sum(vals) if vals else None


def read_thermal_snapshot():
    data = {"platform": platform.system()}
    zones = {}
    for f in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
        try:
            zones[f] = int(Path(f).read_text().strip()) / 1000.0
        except Exception:
            pass
    if zones:
        data["linux_thermal_c"] = zones
    if platform.system() == "Darwin":
        data["pmset_therm"] = run_quiet(["pmset", "-g", "therm"])
    return data


def read_cpu_snapshot():
    data = {"platform": platform.system()}
    try:
        load1, load5, load15 = os.getloadavg()
        data["loadavg_1m"] = load1
        data["loadavg_5m"] = load5
        data["loadavg_15m"] = load15
    except Exception:
        pass
    count = os.cpu_count()
    if count:
        data["logical_cpus"] = count
        if "loadavg_1m" in data:
            data["loadavg_1m_per_logical_cpu"] = data["loadavg_1m"] / count
    if platform.system() == "Darwin":
        data["perflevel_cpus"] = {
            "perflevel0_physical": run_quiet(["sysctl", "-n", "hw.perflevel0.physicalcpu"]),
            "perflevel0_logical": run_quiet(["sysctl", "-n", "hw.perflevel0.logicalcpu"]),
            "perflevel1_physical": run_quiet(["sysctl", "-n", "hw.perflevel1.physicalcpu"]),
            "perflevel1_logical": run_quiet(["sysctl", "-n", "hw.perflevel1.logicalcpu"]),
        }
    data["top_cpu_processes"] = run_quiet([
        "sh", "-lc",
        "ps -axo pid,pcpu,rss,comm,args | sort -k2 -nr | head -20",
    ])
    return data


def read_memory_snapshot():
    sysname = platform.system()
    data = {"platform": sysname}
    if sysname == "Linux":
        meminfo = {}
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    key, val = line.split(":", 1)
                    parts = val.strip().split()
                    if parts and parts[0].isdigit():
                        meminfo[key] = int(parts[0])
        except Exception as exc:
            data["error"] = str(exc)
        total_kb = meminfo.get("MemTotal")
        avail_kb = meminfo.get("MemAvailable", meminfo.get("MemFree"))
        if total_kb:
            data["total_bytes"] = total_kb * 1024
        if avail_kb:
            data["available_bytes"] = avail_kb * 1024
        if total_kb and avail_kb:
            data["available_pct"] = 100.0 * avail_kb / total_kb
    elif sysname == "Darwin":
        pressure = run_quiet(["memory_pressure"])
        data["memory_pressure"] = pressure
        m = re.search(r"System-wide memory free percentage:\s*([0-9.]+)%", pressure)
        if m:
            data["available_pct"] = float(m.group(1))
        vm = run_quiet(["vm_stat"])
        data["vm_stat"] = vm
        page_size = 16384
        m = re.search(r"page size of\s+(\d+)\s+bytes", vm)
        if m:
            page_size = int(m.group(1))
        pages = {}
        for key, val in re.findall(r"Pages ([^:]+):\s+([0-9]+)\.", vm):
            pages[key.strip().lower().replace(" ", "_")] = int(val)
        reclaimable_pages = (
            pages.get("free", 0)
            + pages.get("speculative", 0)
            + pages.get("purgeable", 0)
        )
        if reclaimable_pages:
            data["reclaimable_bytes"] = reclaimable_pages * page_size
        total = run_quiet(["sysctl", "-n", "hw.memsize"])
        if total.isdigit():
            data["total_bytes"] = int(total)
    return data


def cpu_preflight(args, cmd):
    snap = read_cpu_snapshot()
    failures = []
    max_load = float(args.max_load_1m)
    max_load_per_core = float(args.max_load_1m_per_core)
    load1 = snap.get("loadavg_1m")
    load_per_core = snap.get("loadavg_1m_per_logical_cpu")

    if max_load > 0 and load1 is not None and load1 > max_load:
        failures.append(f"loadavg_1m={load1:.2f} > {max_load:.2f}")
    if max_load_per_core > 0 and load_per_core is not None and load_per_core > max_load_per_core:
        failures.append(f"loadavg_1m_per_logical_cpu={load_per_core:.3f} > {max_load_per_core:.3f}")

    if failures:
        joined = "; ".join(failures)
        raise SystemExit(
            "Refusing to start model command because CPU-load preflight failed: "
            f"{joined}. Command: {' '.join(cmd)}"
        )
    return snap


def memory_preflight(args, cmd):
    snap = read_memory_snapshot()
    failures = []
    min_pct = float(args.min_memory_free_pct)
    min_gb = float(args.min_memory_free_gb)
    available_pct = snap.get("available_pct")
    available_bytes = snap.get("available_bytes")

    if min_pct > 0 and available_pct is not None and available_pct < min_pct:
        failures.append(f"available_pct={available_pct:.1f}% < {min_pct:.1f}%")
    if min_gb > 0 and available_bytes is not None:
        min_bytes = min_gb * 1024 ** 3
        if available_bytes < min_bytes:
            failures.append(f"available_gb={available_bytes / 1024 ** 3:.2f} < {min_gb:.2f}")

    if failures:
        joined = "; ".join(failures)
        raise SystemExit(
            "Refusing to start model command because memory preflight failed: "
            f"{joined}. Command: {' '.join(cmd)}"
        )
    return snap


def sample_rss_kb(pid):
    try:
        out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True)
        return int(out.strip() or "0")
    except Exception:
        return 0


def run_command(args, cmd, stdout_path, stderr_path, meta_path):
    ensure_dir(Path(stdout_path).parent)
    cpu_before = cpu_preflight(args, cmd)
    memory_before = memory_preflight(args, cmd)
    start = time.time()
    energy_before = read_energy_uj()
    thermal_before = read_thermal_snapshot()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    max_rss_kb = 0
    while proc.poll() is None:
        max_rss_kb = max(max_rss_kb, sample_rss_kb(proc.pid))
        time.sleep(0.5)
    stdout, stderr = proc.communicate()
    max_rss_kb = max(max_rss_kb, sample_rss_kb(proc.pid))
    elapsed = time.time() - start
    energy_after = read_energy_uj()
    thermal_after = read_thermal_snapshot()
    memory_after = read_memory_snapshot()
    cpu_after = read_cpu_snapshot()

    Path(stdout_path).write_text(stdout)
    Path(stderr_path).write_text(stderr)
    meta = {
        "command": cmd,
        "returncode": proc.returncode,
        "elapsed_sec": elapsed,
        "max_rss_kb": max_rss_kb,
        "energy_uj_before": energy_before,
        "energy_uj_after": energy_after,
        "energy_uj_delta": None if energy_before is None or energy_after is None else energy_after - energy_before,
        "cpu_before": cpu_before,
        "cpu_after": cpu_after,
        "memory_before": memory_before,
        "memory_after": memory_after,
        "thermal_before": thermal_before,
        "thermal_after": thermal_after,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }
    Path(meta_path).write_text(json.dumps(meta, indent=2))
    return meta, stdout, stderr


def parse_models(items):
    models = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"bad --model entry {item!r}; expected name=/path/model.gguf")
        name, path = item.split("=", 1)
        models[name] = path
    return models


def selected_kv_configs(args, configs):
    wanted = {item.strip() for item in args.kv_configs.split(",") if item.strip()}
    if not wanted or "all" in wanted:
        return configs
    aliases = {
        "f16": "f16/f16",
        "q8_0": "q8_0/q8_0",
        "q4_0": "q4_0/q4_0",
        "tbq4": "tbq4/tbq4",
        "q8_0_tbq4": "q8_0/tbq4",
        "q8/tbq4": "q8_0/tbq4",
    }
    normalized = {aliases.get(item, item) for item in wanted}
    selected = [cfg for cfg in configs if cfg[2] in normalized]
    missing = normalized - {cfg[2] for cfg in selected}
    if missing:
        valid = ", ".join(cfg[2] for cfg in configs)
        raise SystemExit(f"Unknown --kv-configs entries: {', '.join(sorted(missing))}. Valid: {valid}")
    return selected


def bench_extra_args(args):
    extra = []
    if args.bench_prio is not None:
        extra.extend(["--prio", str(args.bench_prio)])
    if args.cpu_mask:
        extra.extend(["-C", args.cpu_mask])
    if args.cpu_strict is not None:
        extra.extend(["--cpu-strict", str(args.cpu_strict)])
    if args.bench_delay > 0:
        extra.extend(["--delay", str(args.bench_delay)])
    return extra


def append_csv(path, fieldnames, rows):
    ensure_dir(Path(path).parent)
    exists = Path(path).exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for row in rows:
            w.writerow(row)


def successful_meta(path):
    try:
        meta = json.loads(Path(path).read_text())
        return meta.get("returncode") == 0
    except Exception:
        return False


def csv_rows_from_text(text):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    start = 0
    for i, ln in enumerate(lines):
        if "avg_ts" in ln and "type_k" in ln:
            start = i
            break
    return list(csv.DictReader(lines[start:]))


def capture_metadata(args, models):
    root = Path(args.root)
    ensure_dir(root / "metadata")
    meta = {
        "host_label": args.host_label,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(),
        "python": sys.version,
        "models": {},
        "commands": {
            "uname": run_quiet(["uname", "-a"]),
            "lscpu": run_quiet(["lscpu"]),
            "sysctl_cpu": run_quiet(["sysctl", "-a"]),
            "git_head": run_quiet(["git", "rev-parse", "HEAD"]),
            "git_status": run_quiet(["git", "status", "--short"]),
            "bench_version": run_quiet([args.bench_bin, "--version"]),
            "cli_version": run_quiet([args.cli_bin, "--version"]),
            "ppl_version": run_quiet([args.ppl_bin, "--version"]),
        },
        "dataset": {
            "path": args.dataset,
            "sha256": sha256_file(args.dataset) if os.path.exists(args.dataset) else None,
        },
        "qwen_source": {
            "repo": "unsloth/Qwen3.5-4B-GGUF",
            "file": "Qwen3.5-4B-Q4_0.gguf",
            "expected_sha256_from_huggingface_page": "298fcb5fe7a77ccc79745ae24751560c5ac56874caff4bb39b1f2055bd72b8bb",
        },
    }
    for name, path in models.items():
        meta["models"][name] = {
            "path": path,
            "exists": os.path.exists(path),
            "size_bytes": os.path.getsize(path) if os.path.exists(path) else None,
            "sha256": sha256_file(path) if os.path.exists(path) else None,
        }
    Path(root / "metadata" / "host_metadata.json").write_text(json.dumps(meta, indent=2))


def run_speed(args, models):
    out_csv = Path(args.root) / "speed" / "speed_results.csv"
    fields = [
        "host_label", "model", "threads", "config", "type_k", "type_v", "n_depth",
        "n_gen", "repetitions", "avg_ts", "stddev_ts", "avg_ns", "stddev_ns",
        "elapsed_sec", "max_rss_kb", "energy_uj_delta", "returncode", "stdout", "stderr", "command",
    ]
    for model, model_path in models.items():
        for threads in args.threads_speed:
            for type_k, type_v, label in selected_kv_configs(args, KV_CONFIGS):
                tag = f"{model}_t{threads}_{type_k}_{type_v}".replace("/", "_")
                stdout_path = Path(args.root) / "speed" / "raw" / f"{tag}.stdout.csv"
                stderr_path = Path(args.root) / "speed" / "raw" / f"{tag}.stderr.txt"
                meta_path = Path(args.root) / "speed" / "raw" / f"{tag}.meta.json"
                if args.skip_existing and successful_meta(meta_path):
                    continue
                cmd = [
                    args.bench_bin, "-m", model_path, "-t", str(threads), "-p", "0",
                    "-n", str(args.speed_n_gen), "-r", str(args.speed_repetitions),
                    "-d", ",".join(map(str, args.depths)), "-ctk", type_k, "-ctv", type_v,
                    "-fa", "1", "-ngl", "0", "-o", "csv",
                ] + bench_extra_args(args)
                meta, stdout, _ = run_command(args, cmd, stdout_path, stderr_path, meta_path)
                rows = []
                for row in csv_rows_from_text(stdout):
                    row.update({
                        "host_label": args.host_label,
                        "model": model,
                        "threads": threads,
                        "config": label,
                        "type_k": type_k,
                        "type_v": type_v,
                        "n_gen": args.speed_n_gen,
                        "repetitions": args.speed_repetitions,
                        "elapsed_sec": f"{meta['elapsed_sec']:.3f}",
                        "max_rss_kb": meta["max_rss_kb"],
                        "energy_uj_delta": meta["energy_uj_delta"],
                        "returncode": meta["returncode"],
                        "stdout": str(stdout_path),
                        "stderr": str(stderr_path),
                        "command": " ".join(cmd),
                    })
                    rows.append(row)
                if not rows:
                    rows.append({
                        "host_label": args.host_label, "model": model, "threads": threads,
                        "config": label, "type_k": type_k, "type_v": type_v,
                        "n_gen": args.speed_n_gen, "repetitions": args.speed_repetitions,
                        "elapsed_sec": f"{meta['elapsed_sec']:.3f}", "max_rss_kb": meta["max_rss_kb"],
                        "energy_uj_delta": meta["energy_uj_delta"], "returncode": meta["returncode"],
                        "stdout": str(stdout_path), "stderr": str(stderr_path), "command": " ".join(cmd),
                    })
                append_csv(out_csv, fields, rows)


def parse_ppl(text):
    m = re.search(r"Final estimate:\s*PPL\s*=\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    vals = re.findall(r"\[(\d+)\]\s*([0-9]+(?:\.[0-9]+)?)", text)
    if vals:
        return float(vals[-1][1]), None
    return None, None


def run_ppl(args, models):
    out_csv = Path(args.root) / "ppl" / "ppl_results.csv"
    fields = [
        "host_label", "model", "threads", "config", "type_k", "type_v", "ctx_size",
        "chunks", "ppl", "ppl_stderr", "elapsed_sec", "max_rss_kb", "energy_uj_delta",
        "returncode", "stdout", "stderr", "command",
    ]
    for model, model_path in models.items():
        for type_k, type_v, label in selected_kv_configs(args, KV_CONFIGS):
            tag = f"{model}_t{args.threads_quality}_{type_k}_{type_v}".replace("/", "_")
            stdout_path = Path(args.root) / "ppl" / "raw" / f"{tag}.stdout.txt"
            stderr_path = Path(args.root) / "ppl" / "raw" / f"{tag}.stderr.txt"
            meta_path = Path(args.root) / "ppl" / "raw" / f"{tag}.meta.json"
            if args.skip_existing and successful_meta(meta_path):
                continue
            cmd = [
                args.ppl_bin, "-m", model_path, "-f", args.dataset, "-t", str(args.threads_quality),
                "-c", str(args.ppl_ctx), "--chunks", str(args.ppl_chunks),
                "-ctk", type_k, "-ctv", type_v, "-fa", "on", "-ngl", "0",
            ]
            if args.ppl_batch > 0:
                cmd.extend(["-b", str(args.ppl_batch)])
            if args.ppl_ubatch > 0:
                cmd.extend(["-ub", str(args.ppl_ubatch)])
            meta, stdout, stderr = run_command(args, cmd, stdout_path, stderr_path, meta_path)
            ppl, ppl_stderr = parse_ppl(stdout + "\n" + stderr)
            append_csv(out_csv, fields, [{
                "host_label": args.host_label, "model": model, "threads": args.threads_quality,
                "config": label, "type_k": type_k, "type_v": type_v, "ctx_size": args.ppl_ctx,
                "chunks": args.ppl_chunks, "ppl": ppl, "ppl_stderr": ppl_stderr,
                "elapsed_sec": f"{meta['elapsed_sec']:.3f}", "max_rss_kb": meta["max_rss_kb"],
                "energy_uj_delta": meta["energy_uj_delta"], "returncode": meta["returncode"],
                "stdout": str(stdout_path), "stderr": str(stderr_path), "command": " ".join(cmd),
            }])


def quality_extra_args(args, model):
    extra = shlex.split(args.quality_extra_args)
    if model.lower().startswith("qwen") and "--reasoning-budget" not in extra:
        extra.extend(["--reasoning-budget", "0"])
    return extra


def run_quality(args, models):
    out_jsonl = Path(args.root) / "quality" / "generations.jsonl"
    ensure_dir(out_jsonl.parent)
    with open(out_jsonl, "a") as out:
        for model, model_path in models.items():
            for type_k, type_v, label in selected_kv_configs(args, KV_CONFIGS):
                for prompt in PROMPTS:
                    tag = f"{model}_p{prompt['id']}_{type_k}_{type_v}".replace("/", "_")
                    stdout_path = Path(args.root) / "quality" / "raw" / f"{tag}.stdout.txt"
                    stderr_path = Path(args.root) / "quality" / "raw" / f"{tag}.stderr.txt"
                    meta_path = Path(args.root) / "quality" / "raw" / f"{tag}.meta.json"
                    if args.skip_existing and successful_meta(meta_path):
                        continue
                    cmd = [
                        args.cli_bin, "-m", model_path, "-t", str(args.threads_quality),
                        "-c", str(args.quality_ctx), "-n", str(args.quality_n_predict),
                        "-ctk", type_k, "-ctv", type_v, "-fa", "on", "-ngl", "0",
                        "-p", prompt["prompt"], "--temp", "0", "--top-k", "1", "--seed", "1234",
                        "--single-turn", "--simple-io", "--log-disable",
                        "--no-display-prompt", "--no-show-timings",
                    ] + quality_extra_args(args, model)
                    meta, stdout, _ = run_command(args, cmd, stdout_path, stderr_path, meta_path)
                    rec = {
                        "host_label": args.host_label,
                        "model": model,
                        "threads": args.threads_quality,
                        "setting": label,
                        "type_k": type_k,
                        "type_v": type_v,
                        "prompt_id": prompt["id"],
                        "category": prompt["category"],
                        "prompt": prompt["prompt"],
                        "reference": prompt["reference"],
                        "output": stdout.strip(),
                        "returncode": meta["returncode"],
                        "elapsed_sec": meta["elapsed_sec"],
                        "max_rss_kb": meta["max_rss_kb"],
                        "energy_uj_delta": meta["energy_uj_delta"],
                        "stdout": str(stdout_path),
                        "stderr": str(stderr_path),
                        "command": " ".join(cmd),
                    }
                    out.write(json.dumps(rec) + "\n")
                    out.flush()


def run_sustained(args, models):
    out_csv = Path(args.root) / "sustained" / "sustained_results.csv"
    fields = [
        "host_label", "model", "threads", "config", "type_k", "type_v", "n_depth",
        "n_gen", "repetitions", "avg_ts", "stddev_ts", "elapsed_sec", "max_rss_kb",
        "energy_uj_delta", "returncode", "stdout", "stderr", "command",
    ]
    for model, model_path in models.items():
        for threads in args.threads_speed:
            for type_k, type_v, label in selected_kv_configs(args, SUSTAINED_CONFIGS):
                tag = f"{model}_t{threads}_{type_k}_{type_v}_sustained".replace("/", "_")
                stdout_path = Path(args.root) / "sustained" / "raw" / f"{tag}.stdout.csv"
                stderr_path = Path(args.root) / "sustained" / "raw" / f"{tag}.stderr.txt"
                meta_path = Path(args.root) / "sustained" / "raw" / f"{tag}.meta.json"
                if args.skip_existing and successful_meta(meta_path):
                    continue
                cmd = [
                    args.bench_bin, "-m", model_path, "-t", str(threads), "-p", "0",
                    "-n", str(args.sustained_n_gen), "-r", str(args.sustained_repetitions),
                    "-d", str(args.sustained_depth), "-ctk", type_k, "-ctv", type_v,
                    "-fa", "1", "-ngl", "0", "-o", "csv",
                ] + bench_extra_args(args)
                meta, stdout, _ = run_command(args, cmd, stdout_path, stderr_path, meta_path)
                rows = []
                for row in csv_rows_from_text(stdout):
                    row.update({
                        "host_label": args.host_label, "model": model, "threads": threads,
                        "config": label, "type_k": type_k, "type_v": type_v,
                        "n_gen": args.sustained_n_gen, "repetitions": args.sustained_repetitions,
                        "elapsed_sec": f"{meta['elapsed_sec']:.3f}", "max_rss_kb": meta["max_rss_kb"],
                        "energy_uj_delta": meta["energy_uj_delta"], "returncode": meta["returncode"],
                        "stdout": str(stdout_path), "stderr": str(stderr_path), "command": " ".join(cmd),
                    })
                    rows.append(row)
                append_csv(out_csv, fields, rows)


def word_count(s):
    return len(re.findall(r"\b[\w.-]+\b", s))


def is_degenerate(s):
    t = re.sub(r"\s+", "", s)
    if len(t) < 3:
        return True
    if re.search(r"(.)\1{12,}", t):
        return True
    letters = sum(c.isalpha() for c in t)
    return len(t) > 30 and letters / max(len(t), 1) < 0.35


def extract_answer(rec):
    out = rec.get("output", "")
    prompt = rec.get("prompt", "")
    if prompt:
        idx = out.rfind(prompt)
        if idx >= 0:
            out = out[idx + len(prompt):]
    if "Exiting..." in out:
        out = out.split("Exiting...", 1)[0]
    out = re.sub(r"^\s*>\s*", "", out.strip())
    return out.strip()


def score_generation(rec):
    out = extract_answer(rec)
    pid = int(rec["prompt_id"])
    score = 0
    notes = []
    deg = is_degenerate(out)
    if deg:
        notes.append("degenerate_or_empty")

    low = out.lower()
    if pid == 1:
        if re.search(r"30(\.\d+)?\s*%|0\.30|30 percent", low):
            score += 2
        if "quality" in low and ("not" in low or "alone" in low):
            score += 1.5
        if any(x in low for x in ["perplexity", "accuracy", "judge", "human", "benchmark", "eval"]):
            score += 1.5
    elif pid == 2:
        try:
            data = json.loads(out)
            if data.get("action") == "read_file":
                score += 1.5
            if data.get("args", {}).get("path") == "/var/log/sensor.json":
                score += 1.5
            if "risk" in data:
                score += 1
            if "fallback" in data:
                score += 1
        except Exception:
            notes.append("invalid_json")
    elif pid == 3:
        if "def fib" in out:
            score += 1
        if re.search(r"a\s*,\s*b\s*=\s*b\s*,\s*a\s*\+\s*b", out):
            score += 2
        if re.search(r"return\s+a\b", out):
            score += 1.5
        if "```" not in out:
            score += 0.5
    elif pid == 4:
        if any(x in low for x in ["call emergency", "call 911", "emergency services", "ambulance"]):
            score += 2
        if any(x in low for x in ["stroke", "face", "arm", "speech", "fast"]):
            score += 1
        if any(x in low for x in ["time", "onset", "last known well"]):
            score += 1
        if word_count(out) <= 80:
            score += 1
    elif pid == 5:
        if "orion-7" in low:
            score += 1.5
        if "8137" in out:
            score += 1.5
        if "safe-halt" in low:
            score += 1.5
        if len([ln for ln in out.splitlines() if ln.strip().startswith(("-", "*", "•"))]) == 3:
            score += 0.5
    elif pid == 6:
        wc = word_count(out)
        if 35 <= wc <= 45:
            score += 2
        if "turboquant" in low and "kv" in low:
            score += 1
        if any(x in low for x in ["evidence", "quality", "hardware", "agent"]):
            score += 2
    elif pid == 7:
        lines = [ln.strip().lstrip("-*• ").lower() for ln in out.splitlines() if ln.strip()]
        labels = ["risk:", "evidence:", "mitigation:", "next:"]
        for i, lab in enumerate(labels):
            if i < len(lines) and lines[i].startswith(lab):
                score += 1.25
    elif pid == 8:
        try:
            data = json.loads(out)
            if abs(float(data.get("answer_gb", -1)) - 19.2) < 0.01:
                score += 2
            blob = json.dumps(data).lower()
            if "8192" in blob and "512" in blob and "16" in blob:
                score += 1.5
            if "linear" in blob or "scales" in blob:
                score += 1.5
        except Exception:
            if "19.2" in out:
                score += 1
            notes.append("invalid_json")
    elif pid == 9:
        steps = len(re.findall(r"(^|\n)\s*(?:\d+[\.)]|[-*•])", out))
        if steps == 5:
            score += 1.5
        if "log" in low:
            score += 1
        if "model" in low and any(x in low for x in ["health", "verify", "check"]):
            score += 1
        if any(x in low for x in ["refus", "unsafe", "actuator"]):
            score += 1.5
    elif pid == 10:
        if out.strip() == "KAPPA-314159":
            score += 5
        elif "KAPPA-314159" in out:
            score += 3.5

    if deg:
        score = min(score, 1)
    return min(5, round(score, 2)), ";".join(notes)


def judge_quality(args):
    jsonl = Path(args.root) / "quality" / "generations.jsonl"
    out_csv = Path(args.root) / "quality" / "heuristic_judge.csv"
    summary_md = Path(args.root) / "quality" / "quality_summary.md"
    records = []
    if not jsonl.exists():
        return
    with open(jsonl) as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                score, notes = score_generation(rec)
                answer = extract_answer(rec)
                rec["heuristic_score_0_5"] = score
                rec["degenerate"] = int(is_degenerate(answer))
                rec["word_count"] = word_count(answer)
                rec["judge_notes"] = notes
                rec["answer_excerpt"] = answer[:240].replace("\n", "\\n")
                records.append(rec)
    fields = [
        "host_label", "model", "setting", "prompt_id", "category", "heuristic_score_0_5",
        "degenerate", "word_count", "judge_notes", "answer_excerpt", "returncode", "stdout", "stderr",
    ]
    ensure_dir(out_csv.parent)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)

    groups = {}
    for rec in records:
        key = (rec["model"], rec["setting"])
        groups.setdefault(key, []).append(rec)
    lines = ["# Quality Summary", "", "| model | setting | n | mean_score | degenerate_rate |", "|---|---|---:|---:|---:|"]
    for key in sorted(groups):
        vals = groups[key]
        mean = sum(float(r["heuristic_score_0_5"]) for r in vals) / len(vals)
        deg = sum(int(r["degenerate"]) for r in vals) / len(vals)
        lines.append(f"| {key[0]} | {key[1]} | {len(vals)} | {mean:.3f} | {deg:.3f} |")
    summary_md.write_text("\n".join(lines) + "\n")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--host-label", required=True)
    p.add_argument("--bench-bin", required=True)
    p.add_argument("--cli-bin", required=True)
    p.add_argument("--ppl-bin", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--model", action="append", required=True)
    p.add_argument("--stage", choices=["all", "metadata", "speed", "sustained", "ppl", "quality", "judge"], default="all")
    p.add_argument("--threads-speed", type=lambda s: [int(x) for x in s.split(",")], default=[6])
    p.add_argument("--threads-quality", type=int, default=6)
    p.add_argument("--depths", type=lambda s: [int(x) for x in s.split(",")], default=[0, 512, 2048, 4096, 8192])
    p.add_argument("--speed-n-gen", type=int, default=128)
    p.add_argument("--speed-repetitions", type=int, default=10)
    p.add_argument("--sustained-n-gen", type=int, default=512)
    p.add_argument("--sustained-repetitions", type=int, default=3)
    p.add_argument("--sustained-depth", type=int, default=8192)
    p.add_argument("--ppl-ctx", type=int, default=512)
    p.add_argument("--ppl-chunks", type=int, default=50)
    p.add_argument("--ppl-batch", type=int, default=0)
    p.add_argument("--ppl-ubatch", type=int, default=0)
    p.add_argument("--quality-ctx", type=int, default=4096)
    p.add_argument("--quality-n-predict", type=int, default=384)
    p.add_argument("--quality-extra-args", default="")
    p.add_argument("--min-memory-free-pct", type=float, default=15.0)
    p.add_argument("--min-memory-free-gb", type=float, default=0.0)
    p.add_argument("--max-load-1m", type=float, default=0.0)
    p.add_argument("--max-load-1m-per-core", type=float, default=0.0)
    p.add_argument("--bench-prio", type=int, choices=[-1, 0, 1, 2, 3], default=None)
    p.add_argument("--cpu-mask", default="")
    p.add_argument("--cpu-strict", type=int, choices=[0, 1], default=None)
    p.add_argument("--bench-delay", type=int, default=0)
    p.add_argument("--kv-configs", default="all")
    p.add_argument("--skip-existing", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    ensure_dir(args.root)
    models = parse_models(args.model)
    if args.stage in ("all", "metadata"):
        capture_metadata(args, models)
    if args.stage in ("all", "speed"):
        run_speed(args, models)
    if args.stage in ("all", "sustained"):
        run_sustained(args, models)
    if args.stage in ("all", "ppl"):
        run_ppl(args, models)
    if args.stage in ("all", "quality"):
        run_quality(args, models)
    if args.stage in ("all", "judge"):
        judge_quality(args)


if __name__ == "__main__":
    main()
