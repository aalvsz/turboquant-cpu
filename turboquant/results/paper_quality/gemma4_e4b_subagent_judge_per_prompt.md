| prompt_id | setting | correctness_1_5 | completeness_1_5 | coherence_1_5 | safety_1_5 | degenerate_0_1 | short_note |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | f16/f16 | 5 | 3 | 5 | 5 | 0 | Correct answer, but minimal vs reference detail. |
| 2 | f16/f16 | 5 | 3 | 4 | 5 | 0 | Accurate photosynthesis explanation, truncated before oxygen/byproduct close. |
| 3 | f16/f16 | 2 | 1 | 3 | 5 | 0 | Starts a good approach but no complete function; cut inside docstring. |
| 4 | f16/f16 | 5 | 2 | 3 | 5 | 0 | Correct FAST framing, but truncated before most symptoms. |
| 5 | f16/f16 | 5 | 2 | 3 | 5 | 0 | Explains 5-7-5 structure, but no example; truncated. |
| 1 | q8_0/q8_0 | 5 | 3 | 5 | 5 | 0 | Correct answer, but minimal vs reference detail. |
| 2 | q8_0/q8_0 | 5 | 3 | 4 | 5 | 0 | Same as f16: accurate but cut before finishing oxygen release. |
| 3 | q8_0/q8_0 | 2 | 1 | 3 | 5 | 0 | No complete Fibonacci implementation; cut inside docstring. |
| 4 | q8_0/q8_0 | 5 | 2 | 3 | 5 | 0 | Correct but incomplete FAST list due truncation. |
| 5 | q8_0/q8_0 | 5 | 2 | 3 | 5 | 0 | Correct structure, missing requested example. |
| 1 | q4_0/q4_0 | 5 | 3 | 5 | 5 | 0 | Correct answer, but minimal. |
| 2 | q4_0/q4_0 | 5 | 3 | 4 | 5 | 0 | Accurate core process, truncated before full outcome. |
| 3 | q4_0/q4_0 | 2 | 1 | 3 | 5 | 0 | Begins iterative solution, but no complete code. |
| 4 | q4_0/q4_0 | 5 | 2 | 3 | 5 | 0 | Correct urgency/FAST content, incomplete. |
| 5 | q4_0/q4_0 | 5 | 3 | 3 | 5 | 0 | Covers 5-7-5 and 17 syllables, but no example. |
| 1 | tbq4/tbq4 | 5 | 3 | 5 | 5 | 0 | Correct answer, but minimal. |
| 2 | tbq4/tbq4 | 5 | 3 | 4 | 5 | 0 | Good core facts, truncated before completing thought. |
| 3 | tbq4/tbq4 | 2 | 1 | 3 | 5 | 0 | Starts but does not provide a usable function. |
| 4 | tbq4/tbq4 | 5 | 2 | 3 | 5 | 0 | Correct FAST start, heavily truncated. |
| 5 | tbq4/tbq4 | 5 | 3 | 3 | 5 | 0 | Good structure coverage, missing example. |
| 1 | q8_0/tbq4 | 5 | 3 | 5 | 5 | 0 | Correct answer, but minimal. |
| 2 | q8_0/tbq4 | 5 | 3 | 4 | 5 | 0 | Accurate but ends before finishing oxygen release. |
| 3 | q8_0/tbq4 | 2 | 1 | 3 | 5 | 0 | No complete Fibonacci function; cut mid-docstring. |
| 4 | q8_0/tbq4 | 5 | 2 | 3 | 5 | 0 | Correct but truncated before full symptom list. |
| 5 | q8_0/tbq4 | 5 | 2 | 3 | 5 | 0 | Correct structure, no example; truncated. |

Across these rows there is no meaningful K/V-specific quality degradation. `f16/f16`, `q8_0/q8_0`, `q4_0/q4_0`, `tbq4/tbq4`, and `q8_0/tbq4` produce nearly identical content patterns. The main quality loss is generation-length truncation at 120 tokens, which hurts completeness and coherence for prompts 2-5, especially Fibonacci where no setting reaches a complete function.
