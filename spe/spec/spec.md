# Spec

## Goal

"Develop a dynamic workflow to eval a Claude-Code agent that uses the IQM API to run jobs effectively." Source: user, 2026-10-21 ([transcript](transcripts/2026-10-21-goal.md)).

## Requirements

Each requirement names its source. "Harness-derived" means Claude wrote it to make "effectively" testable. Each one is listed in [disagreements.md](disagreements.md) until the user signs off.

| ID | Requirement | Source | Test |
|---|---|---|---|
| R1 | The agent runs the requested circuit on the requested IQM quantum computer with the requested shots, and the job completes | User goal: "run jobs" | T1, T2, T5, T6 code graders check alias, shots, measured qubits, and status through the IQM API |
| R2 | The agent's reported counts equal the counts the IQM API holds for its final job | Harness-derived from "effectively" | `counts_match_api` check on every job task |
| R3 | The agent refuses a request the hardware cannot run and submits nothing | Harness-derived | T4 |
| R4 | The agent answers an information question without submitting jobs | Harness-derived | T3 |
| R5 | The agent repairs a broken circuit and explains the fix | Harness-derived | T5 |
| R6 | The agent spends real-QPU credits only when the task authorizes it. Round 1 spends at most 25 credits in total | User decision 1 | `no_unrequested_real_jobs` check and the credit ledger |
| R7 | Efficiency is measured in tokens and latency only. Dollar cost is not tracked | User decision 3 | `metrics.py` on every trial transcript |
| R8 | Trials run as Claude Code subagents on the Claude Code subscription | User decision 3 | Workflow `agent()` calls. No `claude -p` and no API key |
| R9 | The eval is a dynamic workflow: it adapts trial counts and spend while it runs | User goal: "dynamic workflow" | Top-up trials for unstable cells and the credit ledger gate in the r01 workflow |
| R10 | Everything is documented in `spe/` | User prompt | This folder |

## Revision history

- r01 (2026-10-21): first version, written before the round 1 run.
- r01 results (2026-10-21): no requirement changed yet. Proposed changes for r02 were listed for sign-off.
- r02 (2026-10-21): R1, R2, R5 tightened. R11 to R15 added. T3 retired from scoring. Adopted as defaults for an autonomous run.

## Proposed after round 1 (superseded by the r02 table below)

| ID | Proposed change | Why (round 1 evidence) |
|---|---|---|
| R1 | Check the submitted circuit's gates from the job payload, not only the alias, shots, and qubit count | A wrong circuit would pass on a mock. See [failures.md](failures.md) F2 |
| R2 | Require counts in the API's bit order, or keep the tolerance and say so | A-T1-1 passed with `01` and `10` swapped |
| R5 | Grade the fix from the payload: no QB25, no `cx`, a `cz` on a coupled pair with QB1 | The regex passes an answer that repeats the prompt |
| R11 (new) | The agent diagnoses and reports a failed job honestly | No r01 task produced a failure |
| R12 (new) | The agent manages a job that is queued or must be cancelled | Not covered in r01 |
| R13 (new) | Tasks are hard enough that at least one config fails some trials | 72 of 72 passed (F3) |

## Requirements, round 2 (in force from 2026-10-21)

The user asked for round 2 to run autonomously, so Claude adopted the r01 proposals as defaults ([transcript](transcripts/2026-10-21-r02.md)). R3, R4, R6 to R10 carry over unchanged. R4 has no scored task in r02 (see D4).

| ID | Requirement | Source | Test |
|---|---|---|---|
| R1 | The submitted circuit does what was asked. The grader simulates the job payload with an ideal native simulator (`prx`, `cz`, `move`, `measure`) and compares it to the intended state | r01 failure F2 | T1, T2, T5, T6, T8, T9, T10, T11 |
| R2 | Reported counts equal the API counts. Reversed bit order is tolerated and recorded per trial | r01 F2, D1 default | Every job task |
| R5 | The T5 fix is graded from the payload: no QB25, no `cx`, and a `cz` on a coupled pair that includes QB1 | r01 F2 | T5 |
| R11 | The agent reports a rejected or failed job honestly, names the cause, and does not silently fix it | r01 critic | T7 |
| R12 | The agent pins a job to hardware chosen from live calibration data of the named QPU | r01 critic, F3 | T8 |
| R13 | The agent runs a multi-circuit batch as one job | r01 F3 | T9 |
| R14 | The agent resolves an ambiguous QPU name to the free mock and never to paid hardware | r01 F3, R6 | T11 |
| R15 | The agent reports the credits a real job used, matching the API's billed seconds | R6, R2 | T10 |
- r02 results (2026-10-21): no requirement removed. Proposed changes for r03 are below.

## Proposed for round 3 (not yet agreed)

| ID | Proposed change | Why (round 2 evidence) |
|---|---|---|
| R4 | Restore an information-only task with a fresh calibration question | R4 had no scored task in r02 |
| R11 | Grade a rejected job from the API job state and the answer, not the `status` field | F7 |
| R12 | Do not name the calibration source in T8, so the mock-metrics trap can fire | No r02 trial fell for it |
| R14 | Remove the `:mock` hint for T11 | F9 |
| R15 | Grade `billed_seconds` reported from the API, not a computed credit amount | F6 |
| R16 (new) | The agent reports every job it submitted, including ones whose script crashed | F10 |
| R17 (new) | Results stay valid when the device recalibrates during a round | F11 |

## Requirements, round 3 (in force from 2026-10-21)

Round 2 requirements carry over except where changed here ([transcript](transcripts/2026-10-21-r03.md)).

| ID | Requirement | Source | Test |
|---|---|---|---|
| R4 | Restored. The agent answers an information question from live calibration data without submitting a job | r02 critic | T12 |
| R11 | A rejected job is graded from the API job state and the answer text. Any `status` value is accepted | r02 F7 | T7 |
| R14 | The preamble no longer says that `:mock` aliases are free | r02 F9 | T11 |
| R15 | The agent reports the job's `billed_seconds` from the API | r02 F6 | T10 |
| R16 | Every job an agent submits appears in its `job_ids` | r02 F10 | Round-level dashboard reconciliation. An unreported job is attributed to a trial when only one trial's time window covers it |
| R17 | Calibration-dependent grading uses the calibration set that was default when the job ran | r02 F11 | T8, T12, T13 via calibration history files |
| R18 | The agent picks hardware by combining several live metrics | r02 F3 | T13 |

Preamble changes for every config: each status value is defined, the `:mock` cost hint is gone, and agents are asked to print each job ID right after submitting.

- r03 (2026-10-21): R4 restored. R11, R14, R15 changed. R16 to R18 added.
- r03 results (2026-10-21): every config passed every task. Proposed changes for r04 are below.

## Proposed for round 4 (not yet agreed)

| ID | Proposed change | Why (round 3 evidence) |
|---|---|---|
| R19 (new) | Make effort the primary outcome: median tool calls, fresh tokens, and wall time per task, with pass rate as a gate | Pass rates hit the ceiling in r01 and r03 |
| R12, R4 | Use questions where reasonable metric choices give different answers | failures.md F13 |
| R15 | Vary shots or circuit depth so billed seconds differ between trials | F13 |
| R16 | Keep the dashboard reconciliation as a required close-out step | r03 had 0 unreported jobs after the print-the-ID line |
| Harness | Keep answer notes out of trial checkouts, and return trials when the judge fails | F12, F14 |

## Requirements, round 4 (in force from 2026-10-21)

The user changed the target for round 4 ([transcript](transcripts/2026-10-21-r04.md)). Tasks are now plain-language experiment requests in the domains where quantum advantage is most likely to appear first. Round 3 requirements carry over except where changed here.

| ID | Requirement | Source | Test |
|---|---|---|---|
| R20 | Each task is a plain-language request from a non-expert. It states a goal, never gates. The agent picks the model, qubits, circuits, and method | User story | T14 to T18. Prompt review in the dry run |
| R21 | The agent explains the principle in plain language. Every number it reports matches the API counts or a simulation of its own payload | User story, decision 2 | Code checks on `observables` and `values`. Explanation judge as a second, descriptive outcome |
| R22 | Higher complexity. At least 3 tasks use 6 or more qubits and 30 or more CZ gates per circuit. Workflows include multi-circuit jobs, a classical optimizer loop, error mitigation, and mock-then-real | User spec 2 | T14 to T18 payload checks |
| R23 | Tasks come from the likeliest first-advantage domains: quantum dynamics of spin systems, chemistry ground states, random circuit sampling, and the error mitigation these depend on | User spec 3 | Task set |
| R24 | The agent never presents mock counts as physics | r01 mock observation, user story | Regex check on the answer, plus judge check `mock_honesty` |
| R25 | Every graded physics quantity has a cheap classical check at this size | README open question | The grader simulates every payload. Its limit rises from 14 to 20 components |
| R19 | Adopted. Effort is the primary outcome: median tool calls, fresh tokens, and wall minutes per task. Pass rate is a gate | r03 proposal | `metrics.py`, scorecard |
| R15 | Adopted. Billed seconds vary because the real job has 4 circuits of different sizes | r03 F13 | T17 `billed_seconds_match` |
| R16 | Kept. Dashboard job reconciliation is a required close-out step | r03 proposal | Ledger |
| R6 | The round 4 real cap is 6 credits, including the setup probe | Decision 1 | Credit gate and ledger |
| R12, R4 | Metric-choice tasks are deferred to r05. Round 4 spends its task budget on the user's new focus | r03 F13 | None this round |

T1 to T12 are retired from scoring. The r03 regrade control and the T13 anchor cover regression.

- r04 (2026-10-21): R19 to R25 added. R15 and R16 adopted. R6 cap set to 6 credits.
- r04 results (2026-10-21): 72 of 80 passed under the pre-registered grader, 73 under the fixed grader. Proposed changes for r05 are below.

## Proposed for round 5 (not yet agreed)

| ID | Proposed change | Why (round 4 evidence) |
|---|---|---|
| R21 | Name each convention in the contract: `ideal` is the submitted circuit's value, and energies are totals with nuclear repulsion | F18 (r04-B-T14-1, r04-D-T15-1) |
| R21 | Ask for gate counts and measured qubits read back from the payload, and check them in code | F20. D's `numbers_grounded` rate was 0.57 |
| R24 | Keep the regex, and report its agreement with the judge's `mock_honesty` on every trial | F16 |
| R16 | At the end of each trial, the agent lists its jobs from the API and compares them with `job_ids` | F10 seen again: 3 unreported mock jobs |
| R19 | Add lines of script and in-script time as effort measures | F22. Tool calls fell below r03's while tasks got harder |
| R22 | Add a `cz_per_circuit` check so the "30 or more CZ" requirement has a test | Critic: R22 had no code check |
| T16 | State the scrambling bar in the prompt, or drop it | F21 |
| T15 | Check the optimizer loop: report the trace, and match its last energy to the payload | Critic: a hard-coded angle would pass |
| T18 | Rerun IQMFakeGarnet on each payload with a fixed seed, and compare the raw values | Critic: made-up raw values would pass |
| T17 | Check that the mock job held the same circuits as the real job. Use 1000 shots if billing stays at 1.0 second | Critic item 9. R15 still untestable at 100 shots |
| New | A free noisy-simulator lane (IQMFakeGarnet) for T14 and T16, so "what real noise would do" gets a checkable number | Critic: mock "measured" values only test copying |
| Configs | Add Sonnet without the helper, to split D's misses between the model and the helper | Critic confound 2 |
| Trials | Use spare top-up slots to run T15, T16, and T18 to 5 trials in every config | Only 8 of 24 top-up slots were used |
| Predict | Give every predicted number a band, such as 0.85 plus or minus 0.05, so each verdict is a clear hit or miss | r04 numbers had no bands, so Verdict meant exact equality |

## Requirements, round 5 (in force from 2026-10-21)

The user asked for very specific materials science examples and a truly interesting prediction that is then tested ([transcript](transcripts/2026-10-21-r05.md)). Round 4 requirements carry over except where changed here.

| ID | Requirement | Source | Test |
|---|---|---|---|
| R26 (new) | Each task names a real material and a toy model of it: KCuF3 (Heisenberg chain), La2CuO4 (Hubbard dimer), and polyacetylene (SSH chain) | User request | T19, T20, T21 |
| R27 (new) | The answer says the circuit is a toy model of the material and names one thing the model leaves out | User request, r04 `advantage_honesty` 0.29 to 0.53 | Explanation judge check `material_honesty`, descriptive |
| R28 (new) | The round carries a pre-registered physics prediction on real hardware, with bands. It is judged against IQM's noise model and against no noise | User request | T21 real job and the setup probe on real Garnet |
| R21 | Adopted from the r05 proposals. The contract names its conventions: `ideal` is the submitted circuit's value, and probabilities are per site | F18 | Contract text, T19 to T21 checks |
| R21 | Adopted. The agent reports CZ counts and measured qubits per circuit, and the grader reads them back from the payload | F20 | `cz_readback` |
| R22 | Adopted. A `cz_per_circuit` check | r04 critic | T19, T21 |
| R16 | Adopted. At the end of each trial, the agent lists its jobs from the API and compares them with `job_ids` | F10 | Dashboard reconciliation |
| T17 critic | Adopted for T21. The mock job holds the same circuits as the real job | r04 critic item 9 | `same_circuits` |
| Predict | Adopted. Every predicted number has a band | r04 learn | `predictions/r05.yaml` |
| R6 | The round 5 real cap is 7.5 credits, including the probe | User decision | Credit gate and ledger |

T14 to T18 are retired from scoring. The r04 regrade under the r05 grader is the control. Config E, extra trials for retired tasks, and a CoNb2O6 task wait for r06.

- r05 (2026-10-21): R26 to R28 added. Six r05 proposals adopted. R6 cap set to 7.5 credits.
