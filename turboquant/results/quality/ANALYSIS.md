
## Quality Metric: Cosine Similarity to Claude Reference

Higher = closer to ideal output. Range [0, 1].

| Model | f16 | q8_0 | q4_0 | tbq4 | tbq3 | tbq2 |
|---|---:|---:|---:|---:|---:|---:|
| gemma2_9b | 0.621 | 0.628 | 0.503 | 0.511 | 0.588 | 0.547 |
| llama3.1_8b | 0.498 | 0.489 | 0.587 | 0.587 | 0.505 | 0.227 |
| qwen2.5_7b | 0.667 | 0.629 | 0.286 | 0.012 | 0.091 | 0.097 |

## Summary: Mean Cosine Similarity per KV Type (across models)

| KV Type | Mean | Interpretation |
|---|---:|---|
| f16 | 0.595 | good — some divergence |
| q8_0 | 0.582 | good — some divergence |
| q4_0 | 0.459 | good — some divergence |
| tbq4 | 0.370 | moderate — noticeable quality loss |
| tbq3 | 0.395 | moderate — noticeable quality loss |
| tbq2 | 0.290 | moderate — noticeable quality loss |

## Per-Prompt Detail

### gemma2_9b

| Prompt | F16 | Q8_0 | Q4_0 | TBQ4 | TBQ3 | TBQ2 |
|---|---:|---:|---:|---:|---:|---:|
| The capital of France is | 0.689 | 0.689 | 0.211 | 0.211 | 0.553 | 0.553 |
| Explain photosynthesis in one paragraph. | 0.789 | 0.789 | 0.676 | 0.759 | 0.753 | 0.641 |
| Write a Python function to compute the nth Fibonac... | 0.462 | 0.494 | 0.462 | 0.494 | 0.503 | 0.503 |
| What are the main symptoms of a stroke? | 0.516 | 0.523 | 0.517 | 0.524 | 0.535 | 0.387 |
| Describe the structure of a haiku with an example. | 0.648 | 0.648 | 0.648 | 0.568 | 0.597 | 0.648 |

### llama3.1_8b

| Prompt | F16 | Q8_0 | Q4_0 | TBQ4 | TBQ3 | TBQ2 |
|---|---:|---:|---:|---:|---:|---:|
| The capital of France is | 0.211 | 0.211 | 0.689 | 0.689 | 0.689 | 0.605 |
| Explain photosynthesis in one paragraph. | 0.783 | 0.792 | 0.789 | 0.669 | 0.499 | 0.000 |
| Write a Python function to compute the nth Fibonac... | 0.249 | 0.249 | 0.249 | 0.467 | 0.400 | 0.211 |
| What are the main symptoms of a stroke? | 0.571 | 0.571 | 0.571 | 0.456 | 0.369 | 0.000 |
| Describe the structure of a haiku with an example. | 0.677 | 0.624 | 0.638 | 0.656 | 0.566 | 0.318 |

### qwen2.5_7b

| Prompt | F16 | Q8_0 | Q4_0 | TBQ4 | TBQ3 | TBQ2 |
|---|---:|---:|---:|---:|---:|---:|
| The capital of France is | 0.689 | 0.689 | 0.500 | 0.000 | 0.000 | 0.487 |
| Explain photosynthesis in one paragraph. | 0.743 | 0.765 | 0.025 | 0.001 | 0.000 | 0.000 |
| Write a Python function to compute the nth Fibonac... | 0.625 | 0.570 | 0.190 | 0.031 | 0.213 | 0.000 |
| What are the main symptoms of a stroke? | 0.496 | 0.465 | 0.387 | 0.000 | 0.000 | 0.000 |
| Describe the structure of a haiku with an example. | 0.784 | 0.655 | 0.327 | 0.027 | 0.242 | 0.000 |

