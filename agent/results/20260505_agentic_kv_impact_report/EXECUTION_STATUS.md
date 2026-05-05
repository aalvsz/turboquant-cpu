# Agentic KV-Cache Impact Execution Status

Date: 2026-05-05

## Plan

1. Run the same agentic-impact suite on every device: Apple M4 Max, x86 Axelera host, and Raspberry Pi.
2. Use the same two models: `gemma4_e4b` and `qwen35_4b`.
3. Test the same KV-cache configurations: `f16/f16`, `q4_0/q4_0`, `q8_0/q8_0`, `q8_0/tbq4`, and `tbq4/tbq4`.
4. Measure end-to-end wall time, JSON/schema validity, tool-use success, reasoning/correctness, safety behavior, token throughput, memory, and available telemetry.
5. Check free memory before starting remote runs.
6. Write per-run artifacts and a consolidated analysis report under this folder.

## Completed

- Apple M4 Max: completed for Gemma and Qwen at 8K context with all KV-cache configs.
- Consolidated report generated in `AGENTIC_KV_IMPACT_REPORT.md`.
- Raw M4 run folders:
  - `agent/results/20260505_m4_agentic_impact_gemma8k`
  - `agent/results/20260505_m4_agentic_impact_qwen8k`

## Blocked Devices

### x86 Axelera host

The host is online over Tailscale, but SSH is denied by tailnet policy before any memory check or benchmark can run.

Probe results:

```text
tailscale ping --timeout=5s --c=1 100.103.130.13
pong from ander-worker (100.103.130.13) via 88.10.216.17:41641 in 24ms

ssh -o BatchMode=yes -o ConnectTimeout=8 ubuntu@100.103.130.13 'hostname; free -h'
tailscale: tailnet policy does not permit you to SSH to this node
Connection closed by 100.103.130.13 port 22
```

### Raspberry Pi

The Pi is online over Tailscale, but Tailscale SSH requires an interactive browser check. The old LAN address is no longer reachable from this Mac.

Probe results:

```text
tailscale ping --timeout=5s --c=1 100.84.61.68
pong from raspberrypi (100.84.61.68) via DERP(mad) in 24ms
2026/05/05 18:09:53 direct connection not established

ssh -o BatchMode=yes -o ConnectTimeout=8 anderalsa@100.84.61.68 'hostname; free -h'
# Tailscale SSH requires an additional check.
# To authenticate, visit: https://login.tailscale.com/a/l533528039ce57

ssh -o BatchMode=yes -o ConnectTimeout=8 anderalsa@10.15.1.39 'hostname; free -h'
ssh: connect to host 10.15.1.39 port 22: Operation timed out
```

Alternate Tailscale ports `2022`, `2200`, `2222`, and `8022` were refused on the Pi.

## Current Device Coverage

The agentic-impact experiment is complete on M4 Max only. The x86 and Raspberry Pi fresh runs are blocked by access, not by benchmark code or model availability.

Previous x86 and Raspberry Pi results remain in `agent/results`, but they are not replacements for this new agentic-impact suite because they used earlier task suites and/or different execution conditions.
