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

## Run-Level Summary

| host | ctx | model | config | reps | wall s | vs Q4 | quality | delta Q4 | JSON | plan | tool | correct | RSS MB |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | f16/f16 | 1 | 79.729 | 3.3% | 0.833 | 0.054 | 1.000 | 1.000 | 1.000 | 0.854 | 8384.0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q4_0/q4_0 | 1 | 82.459 | 0.0% | 0.779 | 0.000 | 1.000 | 1.000 | 1.000 | 0.708 | 7920.0 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q8_0/q8_0 | 1 | 79.876 | 3.1% | 0.829 | 0.050 | 1.000 | 1.000 | 1.000 | 0.812 | 8212.9 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | q8_0/tbq4 | 1 | 76.766 | 6.9% | 0.817 | 0.037 | 1.000 | 1.000 | 1.000 | 0.750 | 7787.3 |
| m4_agentic_impact_gemma8k | 8192 | gemma4_e4b | tbq4/tbq4 | 1 | 78.019 | 5.4% | 0.829 | 0.050 | 1.000 | 1.000 | 1.000 | 0.812 | 7752.1 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | f16/f16 | 1 | 101.578 | -2.6% | 0.871 | 0.023 | 1.000 | 1.000 | 1.000 | 0.771 | 7944.9 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 98.984 | 0.0% | 0.848 | 0.000 | 1.000 | 0.875 | 1.000 | 0.781 | 7826.3 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 99.676 | -0.7% | 0.792 | -0.056 | 1.000 | 1.000 | 1.000 | 0.500 | 7919.6 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 98.845 | 0.1% | 0.752 | -0.096 | 1.000 | 1.000 | 1.000 | 0.490 | 7890.3 |
| m4_agentic_impact_qwen8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 98.350 | 0.6% | 0.831 | -0.017 | 1.000 | 0.875 | 1.000 | 0.698 | 7639.5 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | f16/f16 | 1 | 1008.648 | 2.7% | 0.812 | 0.037 | 1.000 | 1.000 | 1.000 | 0.729 | 6818.8 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q4_0/q4_0 | 1 | 1036.571 | 0.0% | 0.775 | 0.000 | 1.000 | 1.000 | 1.000 | 0.667 | 7343.8 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q8_0/q8_0 | 1 | 977.822 | 5.7% | 0.812 | 0.037 | 1.000 | 1.000 | 1.000 | 0.729 | 7367.8 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | q8_0/tbq4 | 1 | 951.917 | 8.2% | 0.829 | 0.054 | 1.000 | 1.000 | 1.000 | 0.812 | 7441.3 |
| raspberry_pi5_8gb_agentic_gemma4k | 4096 | gemma4_e4b | tbq4/tbq4 | 1 | 976.312 | 5.8% | 0.829 | 0.054 | 1.000 | 1.000 | 1.000 | 0.812 | 7456.9 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | f16/f16 | 1 | 1617.973 | -16.7% | 0.796 | -0.000 | 1.000 | 1.000 | 1.000 | 0.646 | 7152.6 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q4_0/q4_0 | 1 | 1386.054 | 0.0% | 0.796 | 0.000 | 1.000 | 1.000 | 1.000 | 0.646 | 7045.2 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q8_0/q8_0 | 1 | 1406.362 | -1.5% | 0.760 | -0.035 | 1.000 | 1.000 | 1.000 | 0.469 | 6985.8 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | q8_0/tbq4 | 1 | 1333.212 | 3.8% | 0.794 | -0.002 | 1.000 | 1.000 | 1.000 | 0.698 | 7056.2 |
| raspberry_pi5_8gb_agentic_qwen8k | 8192 | qwen35_4b | tbq4/tbq4 | 1 | 1400.740 | -1.1% | 0.769 | -0.027 | 1.000 | 1.000 | 1.000 | 0.594 | 7045.2 |

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

## Reading Guide

- A useful KV quantization result should improve wall time or memory versus Q4 without reducing JSON, tool-use, reasoning/correctness, or safety scores.
- A result that is faster than Q4 but materially below Q4 on quality should be treated as a deployment risk, not a win.
- F16 can be faster when memory fits; KV quantization matters most when context length, concurrency, or memory pressure becomes the bottleneck.
