# Raspberry Pi Capacity Curve Status

Generated: 2026-05-05

## Status

The Raspberry Pi capacity-curve experiment was started from scratch with the new
`agent/run_capacity_curve.py` harness. Qwen 3.5 4B runs completed remotely, but
the result folders could not be copied back after the SSH transport changed:

- Tailscale can still reach `raspberrypi` at `100.84.61.68`.
- Normal SSH over the previous LAN address `10.15.1.39` times out.
- The Mac is currently on `192.168.111.0/24`; SSH responders on that subnet did
  not accept the prepared Pi users/keys.
- Port 22 on `100.84.61.68` is Tailscale SSH, not OpenSSH, and requires an
  interactive Tailscale account check in a browser.
- Alternate Tailscale ports tested (`2200`, `2222`, `8022`, `22222`) refused
  connections.

Because the Tailscale check is an account login form, it could not be completed
autonomously from the terminal without browser credentials.

## Completed Remotely Before Fetch Was Blocked

Remote repo path:
`/home/anderalsa/turboquant-cpu`

Remote result folders:

- `agent/results/20260505_pi_qwen_capacity_curve`
- `agent/results/20260505_pi_qwen_context_curve_c1`

Observed Qwen single-agent context sweep before SSH loss:

| ctx | config | wall s | JSON valid | max RSS MB |
|---:|---|---:|---:|---:|
| 8192 | f16/f16 | 173.9 | 1.0 | 4917.9 |
| 8192 | q4_0/q4_0 | 213.3 | 1.0 | 4729.9 |
| 8192 | tbq4/tbq4 | 188.3 | 1.0 | 4729.9 |
| 8192 | q8_0/tbq4 | 190.7 | 1.0 | 4762.9 |
| 12288 | f16/f16 | 265.0 | 1.0 | 5051.4 |
| 12288 | q4_0/q4_0 | 352.1 | 1.0 | 4771.1 |
| 12288 | tbq4/tbq4 | 291.8 | 1.0 | 4771.5 |
| 12288 | q8_0/tbq4 | 311.2 | 1.0 | 4820.4 |
| 16384 | f16/f16 | 364.7 | 1.0 | 5182.9 |
| 16384 | q4_0/q4_0 | 522.1 | 1.0 | 4809.9 |
| 16384 | tbq4/tbq4 | 424.7 | 1.0 | 4811.4 |

The final `16384 q8_0/tbq4` row completed after the last status snapshot, but
its exact values are only in the remote `summary.csv`.

Observed Qwen 4K concurrency sweep rows before the long outlier was stopped:

| ctx | concurrency | config | wall s | JSON valid | max RSS MB |
|---:|---:|---|---:|---:|---:|
| 4096 | 1 | f16/f16 | 91.9 | 1.0 | 4788.7 |
| 4096 | 1 | q4_0/q4_0 | 100.0 | 1.0 | 4692.9 |
| 4096 | 1 | tbq4/tbq4 | 93.4 | 1.0 | 4693.4 |
| 4096 | 1 | q8_0/tbq4 | 92.6 | 1.0 | 4710.0 |
| 4096 | 2 | f16/f16 | 270.9 | 0.0 | 5367.4 |
| 4096 | 2 | q4_0/q4_0 | 258.6 | 0.5 | 4985.0 |
| 4096 | 2 | tbq4/tbq4 | 275.5 | 0.0 | 4998.8 |

## Next Resume Commands

After LAN SSH is restored or the Tailscale browser check succeeds:

```bash
rsync -av anderalsa@<pi-lan-ip>:/home/anderalsa/turboquant-cpu/agent/results/20260505_pi_qwen_capacity_curve agent/results/
rsync -av anderalsa@<pi-lan-ip>:/home/anderalsa/turboquant-cpu/agent/results/20260505_pi_qwen_context_curve_c1 agent/results/
```

Before running any remaining Gemma rows, check free memory and throttling:

```bash
ssh anderalsa@<pi-lan-ip> 'free -h; vcgencmd measure_temp; vcgencmd get_throttled; pgrep -af "llama-server|run_capacity_curve.py" || true'
```

Then run Gemma with an RSS guard. Do not run unguarded 8K Gemma F16 on the
8 GB Pi because prior 4K Gemma rows already reached about 7.4 GB RSS.
