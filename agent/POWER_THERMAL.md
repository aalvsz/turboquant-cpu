# Power and Thermal Measurement Notes

Use these as side-channel measurements for paper runs. They should be compared
within the same device, same room conditions, and same battery/power state.

## x86 Linux

The benchmark harness can sample Linux package energy and thermal zones:

```bash
python3 agent/run_agent_benchmark.py ... --telemetry
```

When available, each raw run writes:

- `profiler_samples.csv`: `thermal_max_c` and `rapl_package_energy_uj`
- `profile_summary.json`: `thermal_max_c`, `rapl_package_joules`, and `rapl_package_watts_avg`
- `summary.csv`: the same aggregate telemetry fields

This uses `/sys/class/powercap/intel-rapl:*` for package energy and sums package
domains on multi-socket systems. It uses `/sys/class/thermal/thermal_zone*/temp`
for temperatures. If RAPL is absent, use `turbostat` or
`perf stat -a -e power/energy-pkg/` where supported. If thermal zones are not
descriptive enough, install `lm-sensors` and record `sensors -j` alongside the
run.

On some Linux hosts the RAPL counters are root-readable only. For the current
boot, enable unprivileged sampling before the benchmark with:

```bash
sudo chmod a+r /sys/class/powercap/intel-rapl:*/energy_uj
```

## Apple Silicon macOS

For M-series Macs, the practical built-in source is `powermetrics`, usually with
sudo:

```bash
sudo powermetrics \
  --samplers cpu_power,gpu_power,thermal \
  --sample-rate 1000 \
  --sample-count 120 \
  --format plist \
  --output-file agent/results/powermetrics_m4.plist
```

`powermetrics` reports estimated SoC subsystem power. Apple notes these values
should not be used for cross-device comparison, but they are useful for
same-device config comparisons such as Q4 vs TBQ4 under controlled conditions.

Without sudo, `pmset -g therm` can only provide coarse thermal/performance
pressure messages, not package power.

## Raspberry Pi

Temperature and throttling are available without extra hardware:

```bash
cat /sys/class/thermal/thermal_zone0/temp
vcgencmd measure_temp
vcgencmd get_throttled
```

Paper-grade power on Raspberry Pi needs an external USB-C power meter or an
INA219/INA226-style inline power monitor. The SoC does not expose package energy
with the same quality as Intel RAPL.
