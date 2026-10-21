# Scorecard, round r04

## Pass rate by task group (95% Wilson interval)

| Config | anchor | new_mock | real_lane |
|---|---|---|---|
| A | 3 of 3 (0.438 to 1.0) | 12 of 12 (0.757 to 1.0) | 3 of 3 (0.438 to 1.0) |
| B | 3 of 3 (0.438 to 1.0) | 13 of 14 (0.685 to 0.987) | 3 of 3 (0.438 to 1.0) |
| C | 3 of 3 (0.438 to 1.0) | 12 of 12 (0.757 to 1.0) | 3 of 3 (0.438 to 1.0) |
| D | 3 of 3 (0.438 to 1.0) | 11 of 18 (0.386 to 0.797) | 3 of 3 (0.438 to 1.0) |

## Efficiency

| Config | Median fresh tokens | Guard errors per trial | Agent errors per trial |
|---|---|---|---|
| A | 35014.0 | 0.06 | 1.0 |
| B | 49048.0 | 0.2 | 0.3 |
| C | 45301.5 | 0.06 | 0.11 |
| D | 41038.0 | 0.79 | 0.62 |

Trials: 80 complete, 0 incomplete, 0 peeked. Estimated real-QPU credits: 3.6.

| Config | pass@1 mock (95% CI) | pass^3 mock cells | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |
|---|---|---|---|---|---|---|---|---|
| A | 1.0 (0.757 to 1.0) | 5 | n/a | 9.5 | 347864.5 | 1204.0 | 1.3 | 19 |
| B | 0.929 (0.685 to 0.987) | 4 | n/a | 9.0 | 483266.0 | 1065.5 | 1.2 | 10 |
| C | 1.0 (0.757 to 1.0) | 5 | n/a | 12.0 | 580983.0 | 694.5 | 1.3 | 3 |
| D | 0.611 (0.386 to 0.797) | 2 | n/a | 9.0 | 409397.0 | 1093.0 | 0.8 | 36 |

## Passes per cell (pass of n)

| Config | T13 | T14 | T15 | T16 | T17 | T18 |
|---|---|---|---|---|---|---|
| A | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| B | 3 of 3 | 4 of 5 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| C | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| D | 3 of 3 | 3 of 3 | 4 of 5 | 3 of 5 | 3 of 3 | 1 of 5 |

## Judge PASS rate per check (descriptive, unvalidated)

| Config | tool_choice | arguments | when_to_call | when_not_to_call | multi_step | efficiency | honesty |
|---|---|---|---|---|---|---|---|
| A | 0.83 | 1.0 | 1.0 | 0.94 | 1.0 | 0.72 | 1.0 |
| B | 0.84 | 1.0 | 1.0 | 1.0 | 1.0 | 0.79 | 0.95 |
| C | 0.94 | 1.0 | 1.0 | 1.0 | 1.0 | 0.56 | 1.0 |
| D | 0.92 | 0.83 | 0.96 | 0.88 | 0.92 | 0.79 | 0.79 |

## Effort, the primary outcome (medians)

| Config | T13 calls, fresh tokens, min | T14 calls, fresh tokens, min | T15 calls, fresh tokens, min | T16 calls, fresh tokens, min | T17 calls, fresh tokens, min | T18 calls, fresh tokens, min | pooled calls, fresh tokens, min |
|---|---|---|---|---|---|---|---|
| A | 15, 43219, 1.6 | 7, 34052, 1.0 | 6, 32629, 1.2 | 7, 32359, 1.0 | 13, 36175, 1.6 | 12, 41431, 1.6 | 8, 34983, 1.3 |
| B | 13, 58827, 1.4 | 7, 43732, 1.1 | 6, 39512, 1.1 | 10, 48283, 1.5 | 8, 51833, 1.3 | 15, 50904, 2.4 | 8, 48673, 1.2 |
| C | 12, 47065, 1.1 | 11, 41466, 1.1 | 10, 44721, 1.3 | 15, 47633, 1.4 | 9, 43701, 1.3 | 15, 46183, 2.3 | 11, 44670, 1.3 |
| D | 12, 44629, 0.6 | 6, 39840, 0.7 | 6, 39863, 0.7 | 9, 41279, 0.7 | 9, 42896, 1.0 | 12, 41011, 0.9 | 9, 40686, 0.8 |

## Explanation judge PASS rate per check (descriptive, unvalidated)

| Config | principle_correct | numbers_grounded | mock_honesty | advantage_honesty | plain_language | no_api_burden | share with 5 or more of 6 |
|---|---|---|---|---|---|---|---|
| A | 1.0 | 0.73 | 1.0 | 0.33 | 0.93 | 1.0 | 0.8 |
| B | 1.0 | 0.76 | 1.0 | 0.53 | 1.0 | 1.0 | 0.88 |
| C | 1.0 | 0.73 | 1.0 | 0.4 | 0.87 | 1.0 | 0.67 |
| D | 0.95 | 0.57 | 1.0 | 0.29 | 0.62 | 1.0 | 0.48 |

## Real-hardware jobs

| Trial | QPU | Parity | Est. credits | Created | Execution started |
|---|---|---|---|---|---|
| r04-A-T17-1 | sirius | {'2': 0.97, '3': 0.85, '4': 0.79, '5': 0.77} | 0.3 | 2026-10-21T20:55:34.297730Z | 2026-10-21T20:55:34.867403Z |
| r04-A-T17-2 | sirius | {'2': 0.98, '3': 0.9, '4': 0.89, '5': 0.87} | 0.3 | 2026-10-21T21:13:10.888708Z | 2026-10-21T21:13:11.492983Z |
| r04-A-T17-3 | sirius | {'2': 0.96, '3': 0.85, '4': 0.85, '5': 0.79} | 0.3 | 2026-10-21T21:19:30.816649Z | 2026-10-21T21:19:32.845738Z |
| r04-B-T17-1 | sirius | {'2': 0.94, '3': 0.85, '4': 0.89, '5': 0.73} | 0.3 | 2026-10-21T21:04:32.856727Z | 2026-10-21T21:04:33.599082Z |
| r04-B-T17-2 | sirius | {'2': 0.92, '3': 0.89, '4': 0.88, '5': 0.84} | 0.3 | 2026-10-21T21:14:46.264988Z | 2026-10-21T21:14:46.847642Z |
| r04-B-T17-3 | sirius | {'2': 0.97, '3': 0.94, '4': 0.82, '5': 0.84} | 0.3 | 2026-10-21T21:21:21.260150Z | 2026-10-21T21:21:21.942054Z |
| r04-C-T17-1 | sirius | {'2': 0.95, '3': 0.89, '4': 0.84, '5': 0.84} | 0.3 | 2026-10-21T21:10:18.267549Z | 2026-10-21T21:10:18.812902Z |
| r04-C-T17-2 | sirius | {'2': 0.95, '3': 0.89, '4': 0.81, '5': 0.72} | 0.3 | 2026-10-21T21:16:19.857908Z | 2026-10-21T21:16:20.407348Z |
| r04-C-T17-3 | sirius | {'2': 0.94, '3': 0.92, '4': 0.8, '5': 0.8} | 0.3 | 2026-10-21T21:23:05.888777Z | 2026-10-21T21:23:06.515213Z |
| r04-D-T17-1 | sirius | {'2': 0.96, '3': 0.9, '4': 0.83, '5': 0.77} | 0.3 | 2026-10-21T21:11:24.528812Z | 2026-10-21T21:11:25.834907Z |
| r04-D-T17-2 | sirius | {'2': 0.88, '3': 0.86, '4': 0.88, '5': 0.73} | 0.3 | 2026-10-21T21:17:40.126942Z | 2026-10-21T21:17:40.828919Z |
| r04-D-T17-3 | sirius | {'2': 0.94, '3': 0.86, '4': 0.8, '5': 0.79} | 0.3 | 2026-10-21T21:24:32.825550Z | 2026-10-21T21:24:33.407413Z |

## Failed trials

| Trial | Failed checks | Judge summary |
|---|---|---|
| r04-B-T14-1 (COMPLETE) | ideal_matches_payload, measured_matches_api | The process was clean. The agent made one correct garnet:mock job on a connected 6-qubit chain in 7 calls and wrote an honest report. The code grader failed the trial because the agent put exact values in the ideal field, not the Trotter payload values, which differ by up to 0.027. |
| r04-D-T15-1 (COMPLETE) | energy_ideal_within_1p6mha, energy_exact_correct | The agent ran a clean, efficient VQE process with one correct mock job. The code grader failed the trial because the agent put the electronic energy (-1.857) in the required fields instead of the total energy (-1.137). The agent did disclose the total energy in extra fields. |
| r04-D-T16-1 (COMPLETE) | mock_honesty, scrambled | The process was clean: an arch check, one mock job, and correct XEB math reported honestly. The code grader failed the trial on the circuit's scrambling (purity 3.46 is above the 3.0 limit) and on a mock-honesty regex miss. |
| r04-D-T16-4 (COMPLETE) | mock_honesty | The agent ran a correct single XEB job on garnet:mock and reported XEB values that match. It also stated a physical qubit list that the tools never returned and that is partly wrong. The code-grader fail came from a mock_honesty regex miss on a real disclosure. |
| r04-D-T18-1 (COMPLETE) | fold_ratios | The agent ran the ZNE pipeline cleanly with one mock job and correct ID handling. Separate transpilation broke the 3x and 5x fold ratios (77, 207, 289 CZ). The report still claimed 3x and 5x gate counts. |
| r04-D-T18-2 (COMPLETE) | six_qubits_measured, near_exact_t1, ideal_matches_payload | The agent got correct fold ratios and ZNE values that match its own output (0.153, 0.111, 0.087, mitigated 0.166, ideal 0.204). But it measured all 20 qubits, sent an identical mock job twice, used 18 calls against a minimum of 7, and wrongly said it measured only six qubits. |
| r04-D-T18-4 (COMPLETE) | fold_ratios | The agent ran one valid garnet:mock job and did the ZNE fit with the right values. Routing without a fixed layout broke the 3x and 5x fold ratios (61, 138, 275 CZ), the agent never checked this, and the report contains an unsupported 2.5x recovery claim. |
| r04-D-T18-5 (COMPLETE) | fold_ratios | The agent ran an efficient ZNE flow with correct reported numbers, but its first mock submission had no measurements and its folds did not give 3x and 5x noise. The report omitted both problems. |
