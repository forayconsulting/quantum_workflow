# Scorecard, round r01

Trials: 72 complete, 0 incomplete, 0 peeked. Estimated real-QPU credits: 3.6.

| Config | pass@1 T1-T5 (95% CI) | pass^3 cells of 5 | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |
|---|---|---|---|---|---|---|---|---|
| A | 1.0 (0.796 to 1.0) | 5 | 3 of 3 | 6.5 | 228656.0 | 730.5 | 0.5 | 19 |
| B | 1.0 (0.796 to 1.0) | 5 | 3 of 3 | 6.5 | 311462.5 | 519.5 | 0.6 | 19 |
| C | 1.0 (0.796 to 1.0) | 5 | 3 of 3 | 6.5 | 319683.5 | 942.5 | 0.6 | 17 |
| D | 1.0 (0.796 to 1.0) | 5 | 3 of 3 | 5.0 | 177592.0 | 730.5 | 0.3 | 5 |

## Passes per cell (pass of n)

| Config | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|
| A | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| B | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| C | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| D | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |

## Judge PASS rate per check (descriptive, unvalidated)

| Config | tool_choice | arguments | when_to_call | when_not_to_call | multi_step | efficiency | honesty |
|---|---|---|---|---|---|---|---|
| A | 0.89 | 1.0 | 1.0 | 1.0 | 1.0 | 0.56 | 1.0 |
| B | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.56 | 1.0 |
| C | 0.94 | 1.0 | 1.0 | 1.0 | 1.0 | 0.61 | 1.0 |
| D | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.89 | 1.0 |

## T6 real-hardware jobs

| Trial | QPU | P(00)+P(11) | Est. credits | Created | Execution started |
|---|---|---|---|---|---|
| r01-A-T6-1 | sirius | 0.95 | 0.3 | 2026-10-21T15:31:26.644342Z | 2026-10-21T15:31:27.155434Z |
| r01-A-T6-2 | sirius | 0.94 | 0.3 | 2026-10-21T15:39:54.991869Z | 2026-10-21T15:39:56.346985Z |
| r01-A-T6-3 | sirius | 0.93 | 0.3 | 2026-10-21T15:43:26.872706Z | 2026-10-21T15:43:27.436486Z |
| r01-B-T6-1 | sirius | 0.97 | 0.3 | 2026-10-21T15:36:02.178781Z | 2026-10-21T15:36:02.728305Z |
| r01-B-T6-2 | sirius | 0.95 | 0.3 | 2026-10-21T15:41:01.046531Z | 2026-10-21T15:41:01.897837Z |
| r01-B-T6-3 | sirius | 0.94 | 0.3 | 2026-10-21T15:44:29.216981Z | 2026-10-21T15:44:29.888394Z |
| r01-C-T6-1 | sirius | 0.91 | 0.3 | 2026-10-21T15:37:51.750844Z | 2026-10-21T15:37:52.456114Z |
| r01-C-T6-2 | sirius | 0.93 | 0.3 | 2026-10-21T15:41:50.380715Z | 2026-10-21T15:41:51.227674Z |
| r01-C-T6-3 | sirius | 0.95 | 0.3 | 2026-10-21T15:45:19.398397Z | 2026-10-21T15:45:19.925343Z |
| r01-D-T6-1 | sirius | 0.92 | 0.3 | 2026-10-21T15:38:32.568420Z | 2026-10-21T15:38:33.396856Z |
| r01-D-T6-2 | sirius | 0.9 | 0.3 | 2026-10-21T15:42:31.855401Z | 2026-10-21T15:42:32.547800Z |
| r01-D-T6-3 | sirius | 0.94 | 0.3 | 2026-10-21T15:45:55.301864Z | 2026-10-21T15:45:55.840140Z |

## Failed trials

| Trial | Failed checks | Judge summary |
|---|---|---|
