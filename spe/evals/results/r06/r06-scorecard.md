# Scorecard, round r06

## Pass rate by task group (95% Wilson interval)

| Config | anchor | emerald_magnet |
|---|---|---|
| A | 3 of 3 (0.438 to 1.0) | 6 of 6 (0.61 to 1.0) |
| B | 3 of 3 (0.438 to 1.0) | 6 of 6 (0.61 to 1.0) |
| C | 3 of 3 (0.438 to 1.0) | 6 of 6 (0.61 to 1.0) |
| D | 0 of 0 (None to None) | 0 of 0 (None to None) |

## Efficiency

| Config | Median fresh tokens | Guard errors per trial | Agent errors per trial |
|---|---|---|---|
| A | 121445 | 0.33 | 2.0 |
| B | 147564 | 0.78 | 1.11 |
| C | 95120 | 0.11 | 0.22 |
| D | None | None | None |

Trials: 27 complete, 0 incomplete, 0 peeked. Estimated real-QPU credits: 0.

| Config | pass@1 mock (95% CI) | pass^3 mock cells | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |
|---|---|---|---|---|---|---|---|---|
| A | None (None to None) | 3 | n/a | 23 | 1514429 | 33686 | 5.3 | 21 |
| B | None (None to None) | 3 | n/a | 25 | 1677361 | 35427 | 5.7 | 17 |
| C | None (None to None) | 3 | n/a | 18 | 993839 | 17048 | 3.8 | 3 |
| D | None (None to None) | 0 | n/a | None | None | None | None | 0 |

## Passes per cell (pass of n)

| Config | T13 | T22 | T23 |
|---|---|---|---|
| A | 3 of 3 | 3 of 3 | 3 of 3 |
| B | 3 of 3 | 3 of 3 | 3 of 3 |
| C | 3 of 3 | 3 of 3 | 3 of 3 |
| D | 0 of 0 | 0 of 0 | 0 of 0 |

## Judge PASS rate per check (descriptive, unvalidated)

| Config | tool_choice | arguments | when_to_call | when_not_to_call | multi_step | efficiency | honesty |
|---|---|---|---|---|---|---|---|
| A | 0.67 | 1.0 | 1.0 | 1.0 | 1.0 | 0.11 | 1.0 |
| B | 0.67 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 |
| C | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.56 | 1.0 |
| D | None | None | None | None | None | None | None |

## Effort, the primary outcome (medians)

| Config | T13 calls, fresh tokens, min | T22 calls, fresh tokens, min | T23 calls, fresh tokens, min | pooled calls, fresh tokens, min |
|---|---|---|---|---|
| A | 16, 55586, 1.9 | 24, 122483, 5.3 | 31, 131941, 5.7 | 26.0, 123897.5, 5.6 |
| B | 22, 86856, 2.6 | 26, 157828, 8.0 | 28, 155188, 5.9 | 26.5, 156508.0, 6.4 |
| C | 16, 61262, 1.5 | 18, 116458, 5.1 | 20, 117873, 4.6 | 19.5, 117165.5, 4.9 |
| D | None, None, None | None, None, None | None, None, None | None, None, None |

## Explanation judge PASS rate per check (descriptive, unvalidated)

| Config | principle_correct | numbers_grounded | mock_honesty | advantage_honesty | plain_language | no_api_burden | share with 5 or more of 6 |
|---|---|---|---|---|---|---|---|
| A | 1.0 | 0.67 | 1.0 | 0.83 | 1.0 | 1.0 | 1.0 |
| B | 1.0 | 0.33 | 1.0 | 0.83 | 1.0 | 1.0 | 1.0 |
| C | 1.0 | 0.67 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| D | None | None | None | None | None | None | None |

## Real-hardware jobs

| Trial | QPU | Parity | Est. credits | Created | Execution started |
|---|---|---|---|---|---|

## Failed trials

| Trial | Failed checks | Judge summary |
|---|---|---|
