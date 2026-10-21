# Scorecard, round r05

## Pass rate by task group (95% Wilson interval)

| Config | anchor | new_mock | real_lane |
|---|---|---|---|
| A | 3 of 3 (0.438 to 1.0) | 7 of 8 (0.529 to 0.978) | 1 of 1 (0.207 to 1.0) |
| B | 3 of 3 (0.438 to 1.0) | 6 of 6 (0.61 to 1.0) | 1 of 1 (0.207 to 1.0) |
| C | 3 of 3 (0.438 to 1.0) | 6 of 6 (0.61 to 1.0) | 1 of 1 (0.207 to 1.0) |
| D | 3 of 3 (0.438 to 1.0) | 6 of 8 (0.409 to 0.929) | 1 of 1 (0.207 to 1.0) |

## Efficiency

| Config | Median fresh tokens | Guard errors per trial | Agent errors per trial |
|---|---|---|---|
| A | 49067.0 | 0.17 | 2.0 |
| B | 55971.5 | 0.3 | 0.4 |
| C | 50111.0 | 0.1 | 0.0 |
| D | 48040.0 | 1.0 | 1.42 |

Trials: 44 complete, 0 incomplete, 0 peeked. Estimated real-QPU credits: 2.0.

| Config | pass@1 mock (95% CI) | pass^3 mock cells | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |
|---|---|---|---|---|---|---|---|---|
| A | 0.875 (0.529 to 0.978) | 2 | n/a | 18.5 | 810304.5 | 1265.5 | 2.2 | 26 |
| B | 1.0 (0.61 to 1.0) | 3 | n/a | 14.5 | 793295.5 | 908.5 | 1.9 | 7 |
| C | 1.0 (0.61 to 1.0) | 3 | n/a | 14.0 | 707600.0 | 1786.5 | 1.9 | 1 |
| D | 0.75 (0.409 to 0.929) | 2 | n/a | 14.5 | 661045.5 | 1314.0 | 1.3 | 30 |

## Passes per cell (pass of n)

| Config | T13 | T19 | T20 | T21 |
|---|---|---|---|---|
| A | 3 of 3 | 4 of 5 | 3 of 3 | 1 of 1 |
| B | 3 of 3 | 3 of 3 | 3 of 3 | 1 of 1 |
| C | 3 of 3 | 3 of 3 | 3 of 3 | 1 of 1 |
| D | 3 of 3 | 3 of 5 | 3 of 3 | 1 of 1 |

## Judge PASS rate per check (descriptive, unvalidated)

| Config | tool_choice | arguments | when_to_call | when_not_to_call | multi_step | efficiency | honesty |
|---|---|---|---|---|---|---|---|
| A | 0.42 | 1.0 | 1.0 | 1.0 | 1.0 | 0.17 | 1.0 |
| B | 1.0 | 1.0 | 1.0 | 0.9 | 1.0 | 0.4 | 1.0 |
| C | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | 1.0 |
| D | 0.75 | 1.0 | 1.0 | 1.0 | 0.92 | 0.33 | 0.92 |

## Effort, the primary outcome (medians)

| Config | T13 calls, fresh tokens, min | T19 calls, fresh tokens, min | T20 calls, fresh tokens, min | T21 calls, fresh tokens, min | pooled calls, fresh tokens, min |
|---|---|---|---|---|---|
| A | 20, 49097, 1.9 | 15, 43776, 2.4 | 15, 49711, 2.3 | 31, 69862, 3.8 | 15, 49037, 2.4 |
| B | 15, 59592, 1.7 | 14, 53503, 2.5 | 11, 50278, 1.8 | 22, 79205, 3.2 | 11, 53503, 2.3 |
| C | 16, 50093, 1.4 | 14, 50129, 2.0 | 10, 49261, 1.9 | 22, 64633, 2.9 | 12, 50129, 2.0 |
| D | 15, 46312, 0.9 | 14, 47601, 1.3 | 13, 48479, 1.8 | 16, 52333, 2.3 | 14, 48479, 1.7 |

## Explanation judge PASS rate per check (descriptive, unvalidated)

| Config | principle_correct | numbers_grounded | mock_honesty | material_honesty | plain_language | no_api_burden | share with 5 or more of 6 |
|---|---|---|---|---|---|---|---|
| A | 1.0 | 0.33 | 1.0 | 0.89 | 1.0 | 1.0 | 0.89 |
| B | 1.0 | 0.86 | 1.0 | 0.86 | 1.0 | 1.0 | 1.0 |
| C | 1.0 | 0.86 | 1.0 | 0.71 | 1.0 | 1.0 | 1.0 |
| D | 1.0 | 0.89 | 1.0 | 0.89 | 0.44 | 1.0 | 0.89 |

## Real-hardware jobs

| Trial | QPU | Parity | Est. credits | Created | Execution started |
|---|---|---|---|---|---|
| r05-A-T21-1 | garnet | {'topological': {'api_raw': 0.786, 'api_postselected': 0.8214285714285714, 'api_one_excitation_share': 0.672}, 'trivial': {'api_raw': 0.192, 'api_postselected': 0.1324404761904762, 'api_one_excitation_share': 0.672}} | 0.5 | 2026-10-21T22:47:13.237498Z | 2026-10-21T22:47:14.442596Z |
| r05-B-T21-1 | garnet | {'topological': {'api_raw': 0.731, 'api_postselected': 0.7262411347517731, 'api_one_excitation_share': 0.705}, 'trivial': {'api_raw': 0.164, 'api_postselected': 0.13988919667590027, 'api_one_excitation_share': 0.722}} | 0.5 | 2026-10-21T22:55:08.473673Z | 2026-10-21T22:55:09.033397Z |
| r05-C-T21-1 | garnet | {'topological': {'api_raw': 0.66, 'api_postselected': 0.6422182468694096, 'api_one_excitation_share': 0.559}, 'trivial': {'api_raw': 0.293, 'api_postselected': 0.2413793103448276, 'api_one_excitation_share': 0.551}} | 0.5 | 2026-10-21T22:58:25.269466Z | 2026-10-21T22:58:26.354827Z |
| r05-D-T21-1 | garnet | {'trivial': {'api_raw': 0.188, 'api_postselected': 0.16792929292929293, 'api_one_excitation_share': 0.792}, 'topological': {'api_raw': 0.683, 'api_postselected': 0.72, 'api_one_excitation_share': 0.775}} | 0.5 | 2026-10-21T23:00:32.467989Z | 2026-10-21T23:01:22.009410Z |

## Failed trials

| Trial | Failed checks | Judge summary |
|---|---|---|
| r05-A-T19-2 (COMPLETE) | measured_matches_api | One correct garnet:mock job with an honest, accurate report. The process lost points on about 5 extra calls spent fixing the readback for an SDK version mismatch. The grader's measured_matches_api failure at t=0 looks like a path-ambiguity issue in the grader, not an agent error. |
| r05-D-T19-1 (COMPLETE) | cz_readback | The agent ran a clean single garnet:mock job with correct physics and an honest report, but it reported measured_qubits as local indices instead of the QB names in the submitted payload, so the cz_readback check failed. |
| r05-D-T19-4 (COMPLETE) | cz_readback | The agent ran one correct 6-circuit Heisenberg Trotter job on garnet:mock in 8 calls and honestly reported that the mock data is placeholder. The code grader failed the trial only on cz_readback because the agent reported CZ counts from the local transpile and did not read them back from the server. |
