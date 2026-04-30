| prompt_id | setting | correctness_1_5 | completeness_1_5 | coherence_1_5 | safety_1_5 | degenerate_0_1 | short_note |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | f16/f16 | 3 | 4 | 5 | 5 | 0 | wrong speedup arithmetic, otherwise answers constraints |
| 2 | f16/f16 | 4 | 4 | 5 | 5 | 0 | correct No, minor premise slip on swimming |
| 3 | f16/f16 | 2 | 2 | 4 | 5 | 0 | invalid JSON wrapper and wrong answer field |
| 4 | f16/f16 | 3 | 4 | 5 | 5 | 0 | format mostly right, content overclaims evidence |
| 5 | f16/f16 | 3 | 3 | 5 | 5 | 0 | good gist but 55 words, outside limit |
| 6 | f16/f16 | 4 | 4 | 5 | 5 | 0 | fix correct, but fenced despite code-only request |
| 7 | f16/f16 | 4 | 3 | 3 | 5 | 1 | correct approach, truncated ending |
| 8 | f16/f16 | 5 | 4 | 5 | 4 | 0 | urgent stroke advice, omits time noted and keep safe |
| 1 | q8_0/q8_0 | 3 | 4 | 5 | 5 | 0 | wrong speedup arithmetic, rest OK |
| 2 | q8_0/q8_0 | 4 | 4 | 5 | 5 | 0 | correct No, minor all-birds-swim omission |
| 3 | q8_0/q8_0 | 2 | 2 | 4 | 5 | 0 | invalid JSON wrapper and wrong answer field |
| 4 | q8_0/q8_0 | 3 | 4 | 5 | 5 | 0 | labels OK, evidence and mitigation not well grounded |
| 5 | q8_0/q8_0 | 3 | 3 | 5 | 5 | 0 | accurate gist but 54 words |
| 6 | q8_0/q8_0 | 4 | 4 | 5 | 5 | 0 | corrected bug, but not code-only |
| 7 | q8_0/q8_0 | 4 | 3 | 3 | 5 | 1 | correct puzzle logic, truncated |
| 8 | q8_0/q8_0 | 5 | 4 | 5 | 4 | 0 | good emergency advice, misses timing detail |
| 1 | q4_0/q4_0 | 5 | 5 | 5 | 5 | 0 | correct 30.4 percent and constraints |
| 2 | q4_0/q4_0 | 4 | 4 | 5 | 5 | 0 | correct conclusion, muddles swim premise |
| 3 | q4_0/q4_0 | 2 | 2 | 4 | 5 | 0 | invalid JSON wrapper and wrong answer field |
| 4 | q4_0/q4_0 | 3 | 4 | 5 | 5 | 0 | follows label format, content partly speculative |
| 5 | q4_0/q4_0 | 3 | 3 | 5 | 5 | 0 | good summary but 50 words |
| 6 | q4_0/q4_0 | 4 | 4 | 5 | 5 | 0 | fix correct, fenced output violates only-code |
| 7 | q4_0/q4_0 | 4 | 3 | 3 | 5 | 1 | right answer and logic, truncated scenario B |
| 8 | q4_0/q4_0 | 5 | 4 | 5 | 4 | 0 | safe stroke response, missing symptom-time note |
| 1 | tbq4/tbq4 | 4 | 5 | 5 | 5 | 0 | close speedup, quality caveat included |
| 2 | tbq4/tbq4 | 4 | 4 | 5 | 5 | 0 | correct No, but swim/fly wording imprecise |
| 3 | tbq4/tbq4 | 3 | 2 | 2 | 5 | 1 | arithmetic reaches 19.2GB but JSON is truncated |
| 4 | tbq4/tbq4 | 3 | 4 | 5 | 5 | 0 | format OK, claims unprovided perplexity drop |
| 5 | tbq4/tbq4 | 3 | 3 | 5 | 5 | 0 | good gist but 53 words |
| 6 | tbq4/tbq4 | 4 | 4 | 5 | 5 | 0 | corrected function, fenced despite instruction |
| 7 | tbq4/tbq4 | 4 | 3 | 2 | 5 | 1 | correct start, cuts off mid-reasoning |
| 8 | tbq4/tbq4 | 5 | 4 | 5 | 4 | 0 | safe core advice, lacks timing and keep-safe steps |
| 1 | q8_0/tbq4 | 3 | 4 | 5 | 5 | 0 | reports ratio as speedup, percent not computed |
| 2 | q8_0/tbq4 | 5 | 4 | 5 | 5 | 0 | correct and concise, no extra caveat |
| 3 | q8_0/tbq4 | 2 | 2 | 4 | 5 | 0 | invalid JSON wrapper and wrong answer field |
| 4 | q8_0/tbq4 | 3 | 4 | 5 | 5 | 0 | labels OK, content generic and overconfident |
| 5 | q8_0/tbq4 | 3 | 3 | 5 | 5 | 0 | faithful but 54 words |
| 6 | q8_0/tbq4 | 4 | 4 | 5 | 5 | 0 | bug fixed, markdown fence violates code-only |
| 7 | q8_0/tbq4 | 4 | 3 | 2 | 5 | 1 | right box, truncated mid-sentence |
| 8 | q8_0/tbq4 | 5 | 4 | 5 | 4 | 0 | urgent stroke advice, missing timing detail |

Most failures are shared across settings: JSON/code fencing, overlong summaries, and truncated logic-puzzle answers. There is no broad K/V quality collapse, but `tbq4/tbq4` shows the clearest localized degradation on prompt 3 due a truncated invalid JSON response, with `tbq4/tbq4` and `q8_0/tbq4` also slightly worse coherence on the truncated logic puzzle.
