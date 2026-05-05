# Agentic KV-Cache Impact Execution Status

Date: 2026-05-06

## Completed

- Apple M4 Max: completed at 8K context for Gemma 4 E4B and Qwen3.5 4B.
- Raspberry Pi 5 8GB: completed for Qwen3.5 4B at 8K context.
- Raspberry Pi 5 8GB: completed for Gemma 4 E4B at 4K context.

## Raspberry Pi Safety Notes

- Free memory was checked before running.
- Runs were serialized; no concurrent model servers were used.
- Gemma was not run at 8K on the Raspberry Pi because the 4K run already reached 7.46 GB max RSS on an 8 GB device. Running Gemma at 8K would be an avoidable OOM risk.
- The Raspberry Pi reported `throttled=0x0` throughout the completed runs.
- Raspberry Pi power is not measured here. The report includes thermal and throttling telemetry only; paper-grade Pi power needs an external USB-C power meter.

## Still Not Fresh-Rerun

- x86 Axelera host was not rerun in this pass. It remains blocked by Tailscale SSH policy from this Mac:

```text
tailscale: tailnet policy does not permit you to SSH to this node
Connection closed by 100.103.130.13 port 22
```

Previous x86 artifacts are still present elsewhere under `agent/results`, but this M4+Pi report only aggregates fresh agentic-impact runs from M4 and Raspberry Pi.
