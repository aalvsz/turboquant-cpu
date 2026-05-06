# Agentic KV-Cache Quantization Impact Report

## Scope

- Measures tool calling, reasoning, JSON/schema stability, safety behavior, and end-to-end latency under different KV-cache formats.
- Model weights remain 4-bit GGUF; the configs in this report change only the KV cache.
- Q4 is the primary quantized baseline; F16 is the fit-in-memory speed baseline.

## Inputs

- `agent/results/20260505_m4_agentic_impact_gemma8k`
- `agent/results/20260505_m4_agentic_impact_qwen8k`
- `agent/results/20260505_pi_agentic_impact_gemma4k`
- `agent/results/20260505_pi_agentic_impact_qwen8k`
- `agent/results/20260506_x86_agentic_impact_8k`

## Run-Level Summary

| host | ctx | model | config | reps | wall s | vs Q4 | quality | delta Q4 | JSON | plan | tool | correct | RSS MB | therm C | energy J | W | throttle |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | f16/f16 | 1 | 79.729 | 3.3% | 0.833 | 0.054 | 1.000 | 1.000 | 1.000 | 0.854 | 8384.0 | 0.0 | 2894.4 | 35.8 | 0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 82.459 | 0.0% | 0.779 | 0.000 | 1.000 | 1.000 | 1.000 | 0.708 | 7920.0 | 0.0 | 1450.7 | 17.3 | 0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 79.876 | 3.1% | 0.829 | 0.050 | 1.000 | 1.000 | 1.000 | 0.812 | 8212.9 | 0.0 | 1372.7 | 17.0 | 0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 76.766 | 6.9% | 0.817 | 0.037 | 1.000 | 1.000 | 1.000 | 0.750 | 7787.3 | 0.0 | 1198.8 | 15.4 | 0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 78.019 | 5.4% | 0.829 | 0.050 | 1.000 | 1.000 | 1.000 | 0.812 | 7752.1 | 0.0 | 1130.1 | 14.4 | 0 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | f16/f16 | 1 | 101.578 | -2.6% | 0.871 | 0.023 | 1.000 | 1.000 | 1.000 | 0.771 | 7944.9 | 0.0 | 3401.7 | 33.4 | 0 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 98.984 | 0.0% | 0.848 | 0.000 | 1.000 | 0.875 | 1.000 | 0.781 | 7826.3 | 0.0 | 1236.8 | 12.3 | 0 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 99.676 | -0.7% | 0.792 | -0.056 | 1.000 | 1.000 | 1.000 | 0.500 | 7919.6 | 0.0 | 1210.8 | 12.0 | 0 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 98.845 | 0.1% | 0.752 | -0.096 | 1.000 | 1.000 | 1.000 | 0.490 | 7890.3 | 0.0 | 1296.1 | 13.0 | 0 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 98.350 | 0.6% | 0.831 | -0.017 | 1.000 | 0.875 | 1.000 | 0.698 | 7639.5 | 0.0 | 1206.8 | 12.1 | 0 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | f16/f16 | 1 | 1008.648 | 2.7% | 0.812 | 0.037 | 1.000 | 1.000 | 1.000 | 0.729 | 6818.8 | 78.2 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q4_0/q4_0 | 1 | 1036.571 | 0.0% | 0.775 | 0.000 | 1.000 | 1.000 | 1.000 | 0.667 | 7343.8 | 77.1 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q8_0/q8_0 | 1 | 977.822 | 5.7% | 0.812 | 0.037 | 1.000 | 1.000 | 1.000 | 0.729 | 7367.8 | 77.7 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q8_0/tbq4 | 1 | 951.917 | 8.2% | 0.829 | 0.054 | 1.000 | 1.000 | 1.000 | 0.812 | 7441.3 | 77.7 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | tbq4/tbq4 | 1 | 976.312 | 5.8% | 0.829 | 0.054 | 1.000 | 1.000 | 1.000 | 0.812 | 7456.9 | 77.7 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | f16/f16 | 1 | 1617.973 | -16.7% | 0.796 | -0.000 | 1.000 | 1.000 | 1.000 | 0.646 | 7152.6 | 76.5 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 1386.054 | 0.0% | 0.796 | 0.000 | 1.000 | 1.000 | 1.000 | 0.646 | 7045.2 | 77.1 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 1406.362 | -1.5% | 0.760 | -0.035 | 1.000 | 1.000 | 1.000 | 0.469 | 6985.8 | 77.1 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 1333.212 | 3.8% | 0.794 | -0.002 | 1.000 | 1.000 | 1.000 | 0.698 | 7056.2 | 77.1 | 0.0 | 0.0 | 0 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 1400.740 | -1.1% | 0.769 | -0.027 | 1.000 | 1.000 | 1.000 | 0.594 | 7045.2 | 77.1 | 0.0 | 0.0 | 0 |
| x86_i5_12500_agentic_8k | 8192 | gemma4_e4b | f16/f16 | 1 | 327.813 | 5.0% | 0.812 | 0.012 | 1.000 | 1.000 | 1.000 | 0.729 | 8610.6 | 90.0 | 21436.7 | 65.0 | 0 |
| x86_i5_12500_agentic_8k | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 345.110 | 0.0% | 0.800 | 0.000 | 1.000 | 1.000 | 1.000 | 0.750 | 7662.8 | 90.0 | 22626.2 | 65.0 | 0 |
| x86_i5_12500_agentic_8k | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 327.213 | 5.2% | 0.812 | 0.012 | 1.000 | 1.000 | 1.000 | 0.729 | 7995.6 | 90.0 | 21418.0 | 65.0 | 0 |
| x86_i5_12500_agentic_8k | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 342.629 | 0.7% | 0.808 | 0.008 | 1.000 | 1.000 | 1.000 | 0.771 | 7818.6 | 90.0 | 22339.7 | 64.7 | 0 |
| x86_i5_12500_agentic_8k | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 331.968 | 3.8% | 0.840 | 0.040 | 1.000 | 1.000 | 1.000 | 0.802 | 7647.1 | 88.0 | 21666.6 | 64.9 | 0 |
| x86_i5_12500_agentic_8k | 8192 | qwen35_4b | f16/f16 | 1 | 450.027 | 1.9% | 0.840 | 0.021 | 1.000 | 1.000 | 1.000 | 0.740 | 7480.6 | 90.0 | 29316.6 | 64.8 | 0 |
| x86_i5_12500_agentic_8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 458.793 | 0.0% | 0.819 | 0.000 | 1.000 | 1.000 | 1.000 | 0.635 | 7029.6 | 91.0 | 29849.1 | 64.9 | 0 |
| x86_i5_12500_agentic_8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 451.671 | 1.6% | 0.800 | -0.019 | 1.000 | 1.000 | 1.000 | 0.542 | 7200.4 | 91.0 | 29419.1 | 64.9 | 0 |
| x86_i5_12500_agentic_8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 424.230 | 7.5% | 0.773 | -0.046 | 1.000 | 1.000 | 1.000 | 0.531 | 6946.6 | 90.0 | 27700.3 | 65.1 | 0 |
| x86_i5_12500_agentic_8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 439.833 | 4.1% | 0.802 | -0.017 | 1.000 | 1.000 | 1.000 | 0.552 | 6978.8 | 91.0 | 28689.6 | 64.9 | 0 |

## Category Impact

| host | model | category | config | tasks | quality | delta Q4 | wall s | vs Q4 | JSON | tool | correct | safety |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_agentic_impact_gemma8k | gemma4_e4b | claim | f16/f16 | 1 | 0.900 | 0.000 | 9.493 | 4.6% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | quality | f16/f16 | 1 | 0.800 | 0.100 | 7.704 | 21.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | reasoning | f16/f16 | 2 | 0.750 | 0.033 | 11.993 | -9.7% | 1.000 | 1.000 | 0.750 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | retrieval | f16/f16 | 1 | 0.900 | 0.000 | 9.242 | 7.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | safety | f16/f16 | 1 | 0.800 | 0.267 | 9.977 | 3.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | schema | f16/f16 | 1 | 0.867 | 0.000 | 9.477 | 5.1% | 1.000 | 1.000 | 0.333 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | tool | f16/f16 | 1 | 0.900 | 0.000 | 9.849 | 6.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | claim | q4_0/q4_0 | 1 | 0.900 | 0.000 | 9.953 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | quality | q4_0/q4_0 | 1 | 0.700 | 0.000 | 9.851 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | reasoning | q4_0/q4_0 | 2 | 0.717 | 0.000 | 10.936 | 0.0% | 1.000 | 1.000 | 0.583 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | retrieval | q4_0/q4_0 | 1 | 0.900 | 0.000 | 9.959 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | safety | q4_0/q4_0 | 1 | 0.533 | 0.000 | 10.328 | 0.0% | 1.000 | 1.000 | 0.667 | 0.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | schema | q4_0/q4_0 | 1 | 0.867 | 0.000 | 9.989 | 0.0% | 1.000 | 1.000 | 0.333 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | tool | q4_0/q4_0 | 1 | 0.900 | 0.000 | 10.505 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | claim | q8_0/q8_0 | 1 | 0.900 | 0.000 | 9.731 | 2.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | quality | q8_0/q8_0 | 1 | 0.800 | 0.100 | 7.809 | 20.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | reasoning | q8_0/q8_0 | 2 | 0.750 | 0.033 | 11.242 | -2.8% | 1.000 | 1.000 | 0.750 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | retrieval | q8_0/q8_0 | 1 | 0.900 | 0.000 | 9.373 | 5.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | safety | q8_0/q8_0 | 1 | 0.800 | 0.267 | 10.249 | 0.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | schema | q8_0/q8_0 | 1 | 0.733 | -0.133 | 9.702 | 2.9% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | tool | q8_0/q8_0 | 1 | 1.000 | 0.100 | 10.528 | -0.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | claim | q8_0/tbq4 | 1 | 0.900 | 0.000 | 9.281 | 6.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | quality | q8_0/tbq4 | 1 | 0.700 | 0.000 | 8.874 | 9.9% | 1.000 | 1.000 | 0.500 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | reasoning | q8_0/tbq4 | 2 | 0.717 | 0.000 | 11.015 | -0.7% | 1.000 | 1.000 | 0.583 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.000 | 9.064 | 9.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | safety | q8_0/tbq4 | 1 | 0.800 | 0.267 | 9.936 | 3.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | schema | q8_0/tbq4 | 1 | 0.800 | -0.067 | 8.476 | 15.1% | 1.000 | 1.000 | 0.333 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | tool | q8_0/tbq4 | 1 | 1.000 | 0.100 | 9.105 | 13.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | claim | tbq4/tbq4 | 1 | 0.900 | 0.000 | 9.732 | 2.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | quality | tbq4/tbq4 | 1 | 0.800 | 0.100 | 9.157 | 7.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | reasoning | tbq4/tbq4 | 2 | 0.717 | 0.000 | 10.341 | 5.4% | 1.000 | 1.000 | 0.583 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | retrieval | tbq4/tbq4 | 1 | 0.900 | 0.000 | 9.839 | 1.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | safety | tbq4/tbq4 | 1 | 0.800 | 0.267 | 9.802 | 5.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | schema | tbq4/tbq4 | 1 | 0.800 | -0.067 | 8.801 | 11.9% | 1.000 | 1.000 | 0.333 | 1.000 |
| m4_agentic_impact_gemma8k | gemma4_e4b | tool | tbq4/tbq4 | 1 | 1.000 | 0.100 | 10.005 | 4.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | claim | f16/f16 | 1 | 0.800 | 0.000 | 12.891 | -7.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | quality | f16/f16 | 1 | 0.800 | 0.000 | 10.825 | 3.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | reasoning | f16/f16 | 2 | 0.900 | 0.075 | 13.246 | -7.6% | 1.000 | 1.000 | 0.750 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | retrieval | f16/f16 | 1 | 0.900 | 0.100 | 16.045 | -6.5% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | safety | f16/f16 | 1 | 0.933 | -0.067 | 12.252 | 1.4% | 1.000 | 1.000 | 0.667 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | schema | f16/f16 | 1 | 0.733 | 0.000 | 10.722 | -4.5% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | tool | f16/f16 | 1 | 1.000 | 0.000 | 12.351 | 8.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | claim | q4_0/q4_0 | 1 | 0.800 | 0.000 | 11.950 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | quality | q4_0/q4_0 | 1 | 0.800 | 0.000 | 11.172 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | reasoning | q4_0/q4_0 | 2 | 0.825 | 0.000 | 12.311 | 0.0% | 1.000 | 1.000 | 0.875 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | retrieval | q4_0/q4_0 | 1 | 0.800 | 0.000 | 15.070 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | safety | q4_0/q4_0 | 1 | 1.000 | 0.000 | 12.426 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | schema | q4_0/q4_0 | 1 | 0.733 | 0.000 | 10.261 | 0.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | tool | q4_0/q4_0 | 1 | 1.000 | 0.000 | 13.483 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | claim | q8_0/q8_0 | 1 | 0.800 | 0.000 | 12.630 | -5.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | quality | q8_0/q8_0 | 1 | 0.600 | -0.200 | 9.957 | 10.9% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | reasoning | q8_0/q8_0 | 2 | 0.733 | -0.092 | 12.637 | -2.6% | 1.000 | 1.000 | 0.417 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | retrieval | q8_0/q8_0 | 1 | 0.900 | 0.100 | 16.555 | -9.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | safety | q8_0/q8_0 | 1 | 0.933 | -0.067 | 12.334 | 0.7% | 1.000 | 1.000 | 0.667 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | schema | q8_0/q8_0 | 1 | 0.733 | 0.000 | 10.700 | -4.3% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | tool | q8_0/q8_0 | 1 | 0.900 | -0.100 | 12.225 | 9.3% | 1.000 | 1.000 | 0.500 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | claim | q8_0/tbq4 | 1 | 0.900 | 0.100 | 12.277 | -2.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | quality | q8_0/tbq4 | 1 | 0.600 | -0.200 | 10.585 | 5.2% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | reasoning | q8_0/tbq4 | 2 | 0.758 | -0.067 | 12.364 | -0.4% | 1.000 | 1.000 | 0.542 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.100 | 17.326 | -15.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | safety | q8_0/tbq4 | 1 | 0.467 | -0.533 | 11.079 | 10.8% | 1.000 | 1.000 | 0.333 | 0.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | schema | q8_0/tbq4 | 1 | 0.733 | 0.000 | 10.572 | -3.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | tool | q8_0/tbq4 | 1 | 0.900 | -0.100 | 12.277 | 8.9% | 1.000 | 1.000 | 0.500 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | claim | tbq4/tbq4 | 1 | 0.800 | 0.000 | 11.866 | 0.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | quality | tbq4/tbq4 | 1 | 0.800 | 0.000 | 10.916 | 2.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | reasoning | tbq4/tbq4 | 2 | 0.758 | -0.067 | 12.481 | -1.4% | 1.000 | 1.000 | 0.542 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | retrieval | tbq4/tbq4 | 1 | 0.900 | 0.100 | 16.140 | -7.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | safety | tbq4/tbq4 | 1 | 0.933 | -0.067 | 11.746 | 5.5% | 1.000 | 1.000 | 0.667 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | schema | tbq4/tbq4 | 1 | 0.800 | 0.067 | 10.287 | -0.3% | 1.000 | 1.000 | 0.333 | 1.000 |
| m4_agentic_impact_qwen8k | qwen35_4b | tool | tbq4/tbq4 | 1 | 0.900 | -0.100 | 12.433 | 7.8% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | claim | f16/f16 | 1 | 0.900 | 0.000 | 121.644 | 3.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | quality | f16/f16 | 1 | 0.800 | 0.100 | 101.096 | 14.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | reasoning | f16/f16 | 2 | 0.683 | -0.033 | 143.051 | -0.7% | 1.000 | 1.000 | 0.417 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | retrieval | f16/f16 | 1 | 0.900 | 0.000 | 120.828 | 2.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | safety | f16/f16 | 1 | 0.800 | 0.267 | 129.080 | 4.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | schema | f16/f16 | 1 | 0.733 | 0.000 | 117.919 | -5.1% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | tool | f16/f16 | 1 | 1.000 | 0.000 | 131.980 | 4.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | claim | q4_0/q4_0 | 1 | 0.900 | 0.000 | 125.898 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | quality | q4_0/q4_0 | 1 | 0.700 | 0.000 | 118.556 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | reasoning | q4_0/q4_0 | 2 | 0.717 | 0.000 | 142.097 | 0.0% | 1.000 | 1.000 | 0.583 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | retrieval | q4_0/q4_0 | 1 | 0.900 | 0.000 | 123.503 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | safety | q4_0/q4_0 | 1 | 0.533 | 0.000 | 134.788 | 0.0% | 1.000 | 1.000 | 0.667 | 0.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | schema | q4_0/q4_0 | 1 | 0.733 | 0.000 | 112.196 | 0.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | tool | q4_0/q4_0 | 1 | 1.000 | 0.000 | 137.437 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | claim | q8_0/q8_0 | 1 | 0.900 | 0.000 | 118.665 | 5.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | quality | q8_0/q8_0 | 1 | 0.800 | 0.100 | 97.699 | 17.6% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | reasoning | q8_0/q8_0 | 2 | 0.683 | -0.033 | 139.027 | 2.2% | 1.000 | 1.000 | 0.417 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | retrieval | q8_0/q8_0 | 1 | 0.900 | 0.000 | 117.311 | 5.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | safety | q8_0/q8_0 | 1 | 0.800 | 0.267 | 123.934 | 8.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | schema | q8_0/q8_0 | 1 | 0.733 | 0.000 | 116.056 | -3.4% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | tool | q8_0/q8_0 | 1 | 1.000 | 0.000 | 126.102 | 8.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | claim | q8_0/tbq4 | 1 | 0.900 | 0.000 | 119.678 | 4.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | quality | q8_0/tbq4 | 1 | 0.800 | 0.100 | 95.985 | 19.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | reasoning | q8_0/tbq4 | 2 | 0.750 | 0.033 | 134.266 | 5.5% | 1.000 | 1.000 | 0.750 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.000 | 111.129 | 10.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | safety | q8_0/tbq4 | 1 | 0.800 | 0.267 | 122.320 | 9.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | schema | q8_0/tbq4 | 1 | 0.733 | 0.000 | 119.376 | -6.4% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | tool | q8_0/tbq4 | 1 | 1.000 | 0.000 | 114.897 | 16.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | claim | tbq4/tbq4 | 1 | 0.900 | 0.000 | 120.003 | 4.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | quality | tbq4/tbq4 | 1 | 0.800 | 0.100 | 115.913 | 2.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | reasoning | tbq4/tbq4 | 2 | 0.717 | 0.000 | 132.341 | 6.9% | 1.000 | 1.000 | 0.583 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | retrieval | tbq4/tbq4 | 1 | 0.900 | 0.000 | 119.677 | 3.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | safety | tbq4/tbq4 | 1 | 0.800 | 0.267 | 126.072 | 6.5% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | schema | tbq4/tbq4 | 1 | 0.800 | 0.067 | 112.619 | -0.4% | 1.000 | 1.000 | 0.333 | 1.000 |
| raspberry_pi5_8gb_agentic_gemma4k | gemma4_e4b | tool | tbq4/tbq4 | 1 | 1.000 | 0.000 | 117.345 | 14.6% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | claim | f16/f16 | 1 | 0.800 | 0.000 | 185.165 | -8.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | quality | f16/f16 | 1 | 0.800 | 0.000 | 182.104 | -10.5% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | reasoning | f16/f16 | 2 | 0.800 | -0.050 | 210.375 | -17.3% | 1.000 | 1.000 | 0.750 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | retrieval | f16/f16 | 1 | 0.800 | 0.100 | 268.092 | -28.5% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | safety | f16/f16 | 1 | 0.933 | 0.000 | 195.554 | -17.9% | 1.000 | 1.000 | 0.667 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | schema | f16/f16 | 1 | 0.733 | 0.000 | 170.541 | -22.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | tool | f16/f16 | 1 | 0.700 | 0.000 | 195.767 | -10.5% | 1.000 | 1.000 | 0.500 | 0.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | claim | q4_0/q4_0 | 1 | 0.800 | 0.000 | 171.161 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | quality | q4_0/q4_0 | 1 | 0.800 | 0.000 | 164.788 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | reasoning | q4_0/q4_0 | 2 | 0.850 | 0.000 | 179.365 | 0.0% | 1.000 | 1.000 | 0.750 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | retrieval | q4_0/q4_0 | 1 | 0.700 | 0.000 | 208.559 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | safety | q4_0/q4_0 | 1 | 0.933 | 0.000 | 165.879 | 0.0% | 1.000 | 1.000 | 0.667 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | schema | q4_0/q4_0 | 1 | 0.733 | 0.000 | 139.735 | 0.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | tool | q4_0/q4_0 | 1 | 0.700 | 0.000 | 177.203 | 0.0% | 1.000 | 1.000 | 0.500 | 0.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | claim | q8_0/q8_0 | 1 | 0.800 | 0.000 | 178.413 | -4.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | quality | q8_0/q8_0 | 1 | 0.600 | -0.200 | 158.328 | 3.9% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | reasoning | q8_0/q8_0 | 2 | 0.758 | -0.092 | 178.974 | 0.2% | 1.000 | 1.000 | 0.542 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | retrieval | q8_0/q8_0 | 1 | 0.800 | 0.100 | 221.428 | -6.2% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | safety | q8_0/q8_0 | 1 | 0.933 | 0.000 | 172.078 | -3.7% | 1.000 | 1.000 | 0.667 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | schema | q8_0/q8_0 | 1 | 0.733 | 0.000 | 145.421 | -4.1% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | tool | q8_0/q8_0 | 1 | 0.700 | 0.000 | 172.746 | 2.5% | 1.000 | 1.000 | 0.500 | 0.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | claim | q8_0/tbq4 | 1 | 0.800 | 0.000 | 170.560 | 0.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | quality | q8_0/tbq4 | 1 | 0.700 | -0.100 | 156.511 | 5.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | reasoning | q8_0/tbq4 | 2 | 0.875 | 0.025 | 164.244 | 8.4% | 1.000 | 1.000 | 0.875 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.200 | 217.492 | -4.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | safety | q8_0/tbq4 | 1 | 0.800 | -0.133 | 157.413 | 5.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | schema | q8_0/tbq4 | 1 | 0.800 | 0.067 | 150.691 | -7.8% | 1.000 | 1.000 | 0.333 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | tool | q8_0/tbq4 | 1 | 0.600 | -0.100 | 152.058 | 14.2% | 1.000 | 1.000 | 0.000 | 0.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | claim | tbq4/tbq4 | 1 | 0.800 | 0.000 | 165.944 | 3.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | quality | tbq4/tbq4 | 1 | 0.600 | -0.200 | 161.331 | 2.1% | 1.000 | 1.000 | 0.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | reasoning | tbq4/tbq4 | 2 | 0.758 | -0.092 | 179.795 | -0.2% | 1.000 | 1.000 | 0.542 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | retrieval | tbq4/tbq4 | 1 | 0.900 | 0.200 | 242.381 | -16.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | safety | tbq4/tbq4 | 1 | 0.800 | -0.133 | 155.032 | 6.5% | 1.000 | 1.000 | 1.000 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | schema | tbq4/tbq4 | 1 | 0.933 | 0.200 | 154.868 | -10.8% | 1.000 | 1.000 | 0.667 | 1.000 |
| raspberry_pi5_8gb_agentic_qwen8k | qwen35_4b | tool | tbq4/tbq4 | 1 | 0.600 | -0.100 | 161.593 | 8.8% | 1.000 | 1.000 | 0.000 | 0.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | claim | f16/f16 | 1 | 0.900 | 0.000 | 39.921 | 4.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | quality | f16/f16 | 1 | 0.800 | 0.100 | 32.414 | 17.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | reasoning | f16/f16 | 2 | 0.683 | -0.067 | 46.087 | -0.0% | 1.000 | 1.000 | 0.417 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | retrieval | f16/f16 | 1 | 0.900 | 0.000 | 38.311 | 12.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | safety | f16/f16 | 1 | 0.800 | 0.267 | 41.580 | 2.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | schema | f16/f16 | 1 | 0.733 | -0.133 | 39.693 | 3.8% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | tool | f16/f16 | 1 | 1.000 | 0.000 | 43.721 | 1.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | claim | q4_0/q4_0 | 1 | 0.900 | 0.000 | 41.879 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | quality | q4_0/q4_0 | 1 | 0.700 | 0.000 | 39.112 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | reasoning | q4_0/q4_0 | 2 | 0.750 | 0.000 | 46.076 | 0.0% | 1.000 | 1.000 | 0.750 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | retrieval | q4_0/q4_0 | 1 | 0.900 | 0.000 | 43.880 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | safety | q4_0/q4_0 | 1 | 0.533 | 0.000 | 42.568 | 0.0% | 1.000 | 1.000 | 0.667 | 0.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | schema | q4_0/q4_0 | 1 | 0.867 | 0.000 | 41.244 | 0.0% | 1.000 | 1.000 | 0.333 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | tool | q4_0/q4_0 | 1 | 1.000 | 0.000 | 44.273 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | claim | q8_0/q8_0 | 1 | 0.900 | 0.000 | 40.636 | 3.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | quality | q8_0/q8_0 | 1 | 0.800 | 0.100 | 33.204 | 15.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | reasoning | q8_0/q8_0 | 2 | 0.683 | -0.067 | 46.115 | -0.1% | 1.000 | 1.000 | 0.417 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | retrieval | q8_0/q8_0 | 1 | 0.900 | 0.000 | 38.423 | 12.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | safety | q8_0/q8_0 | 1 | 0.800 | 0.267 | 41.225 | 3.2% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | schema | q8_0/q8_0 | 1 | 0.733 | -0.133 | 39.405 | 4.5% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | tool | q8_0/q8_0 | 1 | 1.000 | 0.000 | 42.089 | 4.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | claim | q8_0/tbq4 | 1 | 0.900 | 0.000 | 45.267 | -8.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | quality | q8_0/tbq4 | 1 | 0.800 | 0.100 | 35.001 | 10.5% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | reasoning | q8_0/tbq4 | 2 | 0.717 | -0.033 | 48.432 | -5.1% | 1.000 | 1.000 | 0.583 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.000 | 41.314 | 5.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | safety | q8_0/tbq4 | 1 | 0.800 | 0.267 | 40.590 | 4.6% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | schema | q8_0/tbq4 | 1 | 0.733 | -0.133 | 41.578 | -0.8% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | tool | q8_0/tbq4 | 1 | 0.900 | -0.100 | 42.016 | 5.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | claim | tbq4/tbq4 | 1 | 0.900 | 0.000 | 41.512 | 0.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | quality | tbq4/tbq4 | 1 | 0.800 | 0.100 | 36.775 | 6.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | reasoning | tbq4/tbq4 | 2 | 0.758 | 0.008 | 46.792 | -1.6% | 1.000 | 1.000 | 0.542 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | retrieval | tbq4/tbq4 | 1 | 0.900 | 0.000 | 39.327 | 10.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | safety | tbq4/tbq4 | 1 | 0.800 | 0.267 | 41.130 | 3.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | schema | tbq4/tbq4 | 1 | 0.800 | -0.067 | 37.909 | 8.1% | 1.000 | 1.000 | 0.333 | 1.000 |
| x86_i5_12500_agentic_8k | gemma4_e4b | tool | tbq4/tbq4 | 1 | 1.000 | 0.000 | 41.731 | 5.7% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | claim | f16/f16 | 1 | 0.800 | 0.000 | 55.890 | -2.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | quality | f16/f16 | 1 | 0.800 | 0.100 | 50.181 | 5.6% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | reasoning | f16/f16 | 2 | 0.825 | 0.033 | 56.455 | -2.0% | 1.000 | 1.000 | 0.875 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | retrieval | f16/f16 | 1 | 0.900 | 0.000 | 69.383 | 10.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | safety | f16/f16 | 1 | 0.933 | 0.000 | 56.384 | -0.4% | 1.000 | 1.000 | 0.667 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | schema | f16/f16 | 1 | 0.733 | 0.000 | 47.580 | -3.4% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | tool | f16/f16 | 1 | 0.900 | 0.000 | 57.700 | 5.1% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | claim | q4_0/q4_0 | 1 | 0.800 | 0.000 | 54.750 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | quality | q4_0/q4_0 | 1 | 0.700 | 0.000 | 53.157 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | reasoning | q4_0/q4_0 | 2 | 0.792 | 0.000 | 55.368 | 0.0% | 1.000 | 1.000 | 0.708 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | retrieval | q4_0/q4_0 | 1 | 0.900 | 0.000 | 77.175 | 0.0% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | safety | q4_0/q4_0 | 1 | 0.933 | 0.000 | 56.187 | 0.0% | 1.000 | 1.000 | 0.667 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | schema | q4_0/q4_0 | 1 | 0.733 | 0.000 | 46.010 | 0.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | tool | q4_0/q4_0 | 1 | 0.900 | 0.000 | 60.779 | 0.0% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | claim | q8_0/q8_0 | 1 | 0.800 | 0.000 | 55.532 | -1.4% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | quality | q8_0/q8_0 | 1 | 0.600 | -0.100 | 52.624 | 1.0% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | reasoning | q8_0/q8_0 | 2 | 0.767 | -0.025 | 57.119 | -3.2% | 1.000 | 1.000 | 0.583 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | retrieval | q8_0/q8_0 | 1 | 0.800 | -0.100 | 71.624 | 7.2% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | safety | q8_0/q8_0 | 1 | 0.933 | 0.000 | 55.198 | 1.8% | 1.000 | 1.000 | 0.667 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | schema | q8_0/q8_0 | 1 | 0.733 | 0.000 | 47.201 | -2.6% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | tool | q8_0/q8_0 | 1 | 1.000 | 0.100 | 55.253 | 9.1% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | claim | q8_0/tbq4 | 1 | 0.800 | 0.000 | 53.511 | 2.3% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | quality | q8_0/tbq4 | 1 | 0.600 | -0.100 | 47.906 | 9.9% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | reasoning | q8_0/tbq4 | 2 | 0.758 | -0.033 | 51.846 | 6.4% | 1.000 | 1.000 | 0.542 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | retrieval | q8_0/tbq4 | 1 | 0.900 | 0.000 | 68.092 | 11.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | safety | q8_0/tbq4 | 1 | 0.933 | 0.000 | 49.753 | 11.5% | 1.000 | 1.000 | 0.667 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | schema | q8_0/tbq4 | 1 | 0.733 | 0.000 | 46.430 | -0.9% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | tool | q8_0/tbq4 | 1 | 0.700 | -0.200 | 54.847 | 9.8% | 1.000 | 1.000 | 0.500 | 0.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | claim | tbq4/tbq4 | 1 | 0.800 | 0.000 | 52.598 | 3.9% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | quality | tbq4/tbq4 | 1 | 0.600 | -0.100 | 45.380 | 14.6% | 1.000 | 1.000 | 0.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | reasoning | tbq4/tbq4 | 2 | 0.758 | -0.033 | 58.101 | -4.9% | 1.000 | 1.000 | 0.542 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | retrieval | tbq4/tbq4 | 1 | 0.800 | -0.100 | 75.373 | 2.3% | 1.000 | 1.000 | 0.500 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | safety | tbq4/tbq4 | 1 | 1.000 | 0.067 | 53.471 | 4.8% | 1.000 | 1.000 | 1.000 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | schema | tbq4/tbq4 | 1 | 0.800 | 0.067 | 46.708 | -1.5% | 1.000 | 1.000 | 0.333 | 1.000 |
| x86_i5_12500_agentic_8k | qwen35_4b | tool | tbq4/tbq4 | 1 | 0.900 | 0.000 | 50.101 | 17.6% | 1.000 | 1.000 | 0.500 | 1.000 |

## Reading Guide

- A useful KV quantization result should improve wall time or memory versus Q4 without reducing JSON, tool-use, reasoning/correctness, or safety scores.
- A result that is faster than Q4 but materially below Q4 on quality should be treated as a deployment risk, not a win.
- F16 can be faster when memory fits; KV quantization matters most when context length, concurrency, or memory pressure becomes the bottleneck.
- Energy columns use RAPL package energy on x86 when available, otherwise battery discharge telemetry on macOS; Raspberry Pi rows currently expose thermal/throttle telemetry but not wall-power energy.
