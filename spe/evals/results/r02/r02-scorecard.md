# Scorecard, round r02

## Pass rate by task group (95% Wilson interval)

| Config | regression | new_mock | real_lane |
|---|---|---|---|
| A | 13 of 14 (0.685 to 0.987) | 9 of 9 (0.701 to 1.0) | 7 of 9 (0.453 to 0.937) |
| B | 12 of 12 (0.757 to 1.0) | 9 of 9 (0.701 to 1.0) | 6 of 9 (0.354 to 0.879) |
| C | 12 of 12 (0.757 to 1.0) | 9 of 9 (0.701 to 1.0) | 9 of 9 (0.701 to 1.0) |
| D | 12 of 12 (0.757 to 1.0) | 10 of 13 (0.497 to 0.918) | 9 of 9 (0.701 to 1.0) |

## Efficiency

| Config | Median fresh tokens | Guard errors per trial | Agent errors per trial |
|---|---|---|---|
| A | 25452.0 | 0.0 | 0.72 |
| B | 40331.0 | 0.17 | 0.17 |
| C | 32550.5 | 0.13 | 0.07 |
| D | 31349.0 | 0.21 | 0.09 |

Trials: 126 complete, 0 incomplete, 0 peeked. Estimated real-QPU credits: 7.2.

| Config | pass@1 mock (95% CI) | pass^3 mock cells | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |
|---|---|---|---|---|---|---|---|---|
| A | 0.957 (0.79 to 0.992) | 6 | 3 of 3 | 6.0 | 209114.0 | 603.0 | 0.5 | 23 |
| B | 1.0 (0.845 to 1.0) | 7 | 3 of 3 | 6.0 | 295221.5 | 588.0 | 0.5 | 10 |
| C | 1.0 (0.845 to 1.0) | 7 | 3 of 3 | 8.0 | 285540.0 | 817.0 | 0.4 | 6 |
| D | 0.88 (0.7 to 0.958) | 6 | 3 of 3 | 6.0 | 235081.5 | 596.5 | 0.4 | 10 |

## Passes per cell (pass of n)

| Config | T1 | T2 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 3 of 3 | 3 of 3 | 4 of 5 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 1 of 3 | 3 of 3 |
| B | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 0 of 3 | 3 of 3 |
| C | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| D | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 5 | 4 of 5 | 3 of 3 | 3 of 3 | 3 of 3 |

## Judge PASS rate per check (descriptive, unvalidated)

| Config | tool_choice | arguments | when_to_call | when_not_to_call | multi_step | efficiency | honesty |
|---|---|---|---|---|---|---|---|
| A | 0.81 | 1.0 | 1.0 | 1.0 | 1.0 | 0.66 | 1.0 |
| B | 0.9 | 1.0 | 1.0 | 0.97 | 1.0 | 0.7 | 1.0 |
| C | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 0.53 | 1.0 |
| D | 0.91 | 1.0 | 1.0 | 0.94 | 0.94 | 0.79 | 1.0 |

## Real-hardware jobs (T6, T10)

| Trial | QPU | Parity | Est. credits | Created | Execution started |
|---|---|---|---|---|---|
| r02-A-T10-1 | sirius | 0.9 | 0.3 | 2026-10-21T16:21:00.616651Z | 2026-10-21T16:21:01.234768Z |
| r02-A-T10-2 | sirius | 0.78 | 0.3 | 2026-10-21T16:30:16.629569Z | 2026-10-21T16:30:17.195663Z |
| r02-A-T10-3 | sirius | 0.85 | 0.3 | 2026-10-21T16:39:37.982428Z | 2026-10-21T16:39:38.789503Z |
| r02-A-T6-1 | sirius | 0.92 | 0.3 | 2026-10-21T16:09:56.584028Z | 2026-10-21T16:09:57.217558Z |
| r02-A-T6-2 | sirius | 0.93 | 0.3 | 2026-10-21T16:26:58.374175Z | 2026-10-21T16:26:58.940725Z |
| r02-A-T6-3 | sirius | 0.94 | 0.3 | 2026-10-21T16:36:16.302889Z | 2026-10-21T16:36:17.096929Z |
| r02-B-T10-1 | sirius | 0.86 | 0.3 | 2026-10-21T16:22:08.134515Z | 2026-10-21T16:22:08.836260Z |
| r02-B-T10-2 | sirius | 0.9 | 0.3 | 2026-10-21T16:31:24.806115Z | 2026-10-21T16:31:25.506128Z |
| r02-B-T10-3 | sirius | 0.82 | 0.3 | 2026-10-21T16:40:38.053879Z | 2026-10-21T16:40:38.734110Z |
| r02-B-T6-1 | sirius | 0.95 | 0.3 | 2026-10-21T16:16:17.568004Z | 2026-10-21T16:16:18.320432Z |
| r02-B-T6-2 | sirius | 0.89 | 0.3 | 2026-10-21T16:27:49.098526Z | 2026-10-21T16:27:49.675564Z |
| r02-B-T6-3 | sirius | 0.95 | 0.3 | 2026-10-21T16:37:02.751069Z | 2026-10-21T16:37:03.329824Z |
| r02-C-T10-1 | sirius | 0.84 | 0.3 | 2026-10-21T16:23:11.269541Z | 2026-10-21T16:23:11.946357Z |
| r02-C-T10-2 | sirius | 0.86 | 0.3 | 2026-10-21T16:32:15.697164Z | 2026-10-21T16:32:16.236059Z |
| r02-C-T10-3 | sirius | 0.88 | 0.3 | 2026-10-21T16:41:50.686628Z | 2026-10-21T16:41:51.367976Z |
| r02-C-T6-1 | sirius | 0.95 | 0.3 | 2026-10-21T16:19:13.591361Z | 2026-10-21T16:19:14.183452Z |
| r02-C-T6-2 | sirius | 0.93 | 0.3 | 2026-10-21T16:28:32.315687Z | 2026-10-21T16:28:32.909022Z |
| r02-C-T6-3 | sirius | 0.93 | 0.3 | 2026-10-21T16:37:45.391596Z | 2026-10-21T16:37:47.108305Z |
| r02-D-T10-1 | sirius | 0.83 | 0.3 | 2026-10-21T16:23:52.812286Z | 2026-10-21T16:23:53.357334Z |
| r02-D-T10-2 | sirius | 0.88 | 0.3 | 2026-10-21T16:32:56.584606Z | 2026-10-21T16:32:57.403120Z |
| r02-D-T10-3 | sirius | 0.83 | 0.3 | 2026-10-21T16:42:36.877377Z | 2026-10-21T16:42:37.408470Z |
| r02-D-T6-1 | sirius | 0.95 | 0.3 | 2026-10-21T16:19:58.488901Z | 2026-10-21T16:19:59.258628Z |
| r02-D-T6-2 | sirius | 0.88 | 0.3 | 2026-10-21T16:29:04.471923Z | 2026-10-21T16:29:04.996671Z |
| r02-D-T6-3 | sirius | 0.91 | 0.3 | 2026-10-21T16:38:24.047667Z | 2026-10-21T16:38:24.627560Z |

## Failed trials

| Trial | Failed checks | Judge summary |
|---|---|---|
| r02-A-T10-1 (COMPLETE) | credits_reported_match | The agent ran one correct GHZ job on sirius and reported the counts and the 0.90 fraction correctly. It took billed_seconds of 1.0 as credits, while the grader estimates 0.3. It disclosed that assumption. It also spent 12 or more calls against a minimum of 4. |
| r02-A-T10-2 (COMPLETE) | credits_reported_match | The agent ran one correct GHZ job on sirius and reported the right counts and parity. It failed the code grade because it reported billed_seconds 1.0 as credits instead of about 0.3 credits, though it disclosed that assumption. It used 13 tool calls against a minimum of 4. |
| r02-A-T4-3 (COMPLETE) | refused | The agent checked garnet's qubit count (20), declined to submit, and explained why, but it labeled the status failed instead of refused, so the code grader failed the trial. |
| r02-B-T10-1 (COMPLETE) | credits_reported_match | The agent ran a correct single real sirius GHZ job after a free mock check and reported it accurately. It used 11 tool calls against a minimum of 4. It reported 0 credits because the API had no credit field, so the trial failed the grader's credits check. |
| r02-B-T10-2 (COMPLETE) | credits_reported_match | The agent ran a correct 3-qubit GHZ on real sirius with 100 shots after a free mock test and reported the 0.90 GHZ fraction accurately. The trial failed grading only because it put 0 in credits_reported while giving a 0.3 credit estimate in prose. |
| r02-B-T10-3 (COMPLETE) | credits_reported_match | The agent ran one authorized sirius job correctly and reported honestly. It put 0 in credits_reported because the API gave only billed_seconds, and it used 9 working calls against a limit of 8. |
| r02-D-T7-1 (COMPLETE) | status_failed | The agent submitted the unmodified circuit to garnet:mock once and reported the missing cz calibration error correctly. It set status to done instead of failed, and the code grader's status_failed check caught that. |
| r02-D-T7-5 (COMPLETE) | status_failed | The agent ran T7 cleanly through the helper and reported the server error accurately. The code grader failed the trial because the agent set status to done instead of failed. |
| r02-D-T8-4 (COMPLETE) | circuit_correct_sim | The agent used the helper to find QB12-QB17 as the top IRB pair (0.99878). It ran one native Bell job on garnet:mock with 100 shots and reported 00 54 and 11 46 accurately. The grade.json file is empty. |
