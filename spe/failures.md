# Failure types

One entry per new failure type. Each entry says what it is, how to spot it, and where it came from. Round 1 had no failed trials, so the entries below are harness and grader failures.

## F1. Worktree guard refuses compound shell commands (harness)

- **What:** In a worktree-isolated subagent, Claude Code refuses a Bash command it cannot prove stays inside the worktree. Examples are pipes with `cd`, `source`, and multi-part commands. The message says "this command is too complex to verify that it stays inside the worktree".
- **How to spot it:** a tool result with `is_error: true` and that text.
- **Seen in:** r01, 54 of 60 tool errors. By config: A 14, B 18, C 17, D 5.
- **Effect:** Agents recovered every time, usually by writing a script file and running it. This adds tool calls and tokens to every config, and it inflates the tool error counts.
- **Fix for round 2:** Tell agents in the preamble to write scripts to files and run them with one simple command. Or keep this as a constant and report agent errors separately from guard refusals.

## F2. Grader leniency (grader)

- **What:** Several code checks pass answers they should not pass. The completeness critic found these:
  - Mock tasks never check the circuit itself. A wrong circuit on `garnet:mock` or `sirius:mock` would pass.
  - T5's fix checks are regexes. "cx" and "25" already appear in the prompt, so repeating the prompt passes.
  - T4 passes on any standalone "20".
  - Counts match in either bit order.
  - Only the last job is graded, and the job count is not checked.
- **Seen in:** r01 code review, not in any trial outcome. The spot check found every r01 answer correct on its merits.
- **Fix for round 2:** Check payloads (no QB25, no `cx`, a `cz` on a coupled pair with QB1, MOVE gates through `COMPR1` on T2). Count jobs. Fix the bit order or state the tolerance in R2.

## F3. Ceiling effect (task design)

- **What:** Every config passed every task. The eval cannot rank configs on accuracy.
- **Seen in:** r01, 72 of 72 passes.
- **Fix for round 2:** Add harder tasks the helper does not solve. Examples: a job that fails and must be diagnosed, a cancel during a queue, a parameter sweep, a pick of the best qubits by readout fidelity and then a run on them, or an Emerald run that must stay under a credit limit.

## F4. Helper solves the task (confound)

- **What:** `iqm_run.py` refuses circuits that are too big (T4) and does the MOVE-aware transpile (T2). On those tasks, configs C and D measure the helper, not the agent.
- **Seen in:** r01 design review by the completeness critic.
- **Fix for round 2:** Report helper-solved cells apart, or add tasks the helper cannot shortcut.

## Observation: mock output is not uniformly random

The docs say `:mock` returns random results. In r01, native-JSON Bell circuits on `garnet:mock` returned only `00` and `11`. Qiskit-transpiled Bell circuits returned all 4 outcomes. `sirius:mock` returned `000` for all 200 shots in every T2 trial. Several agents told the user the mock "returns random results". That claim is only partly true. **Unverified:** how the mock produces its output.

## F5. Grader cannot parse legacy payload formats (grader, r02, fixed)

- **What:** The server accepts `qubits` in place of `locus`, and `angle_t` and `phase_t` (in turns) in place of `angle` and `phase`. The r02 grader crashed on them and wrote empty grade files.
- **Seen in:** r02-D-T8-2, D-T8-3, D-T8-4.
- **Fix:** grade.py accepts both forms. An empty grade file must count as INCOMPLETE, not as a fail. Round 2 counted these 3 as failures during the run, which wrongly triggered 2 top-up trials for D-T8.

## F6. Task asks for a value the API does not return (task design, r02)

- **What:** T10 asked for credits "according to the API". The API returns `billed_seconds` and no credit amount. B's agents said exactly that and reported 0. The grader failed them.
- **Seen in:** 5 T10 failures (A 2, B 3). C and D passed only because the helper prints a credit estimate.
- **Fix for r03:** Grade `billed_seconds`, or give the rate in the prompt.

## F7. Status field ambiguity (contract, r02)

- **What:** The preamble lists `done`, `refused`, and `failed` without defining them. D said `done` for a T7 job that failed as instructed. A said `failed` for a T4 refusal.
- **Seen in:** r02-D-T7-1, D-T7-5, A-T4-3. Each answer described the outcome correctly.
- **Fix for r03:** Define each status in the preamble. Grade T7 from the API job state and the answer text.

## F8. Units mix-up hidden by the mock (agent, r02)

- **What:** r02-D-T8-4 wrote `"angle": 0.25` (a turn value) under the radians key. The circuit is not a Bell state. `garnet:mock` still returned only 00 and 11, so the agent reported success.
- **Why it matters:** Mock counts cannot validate a circuit. Only payload simulation caught this.

## F9. Hints in the preamble weaken bait tasks (task design, r02)

- **What:** The preamble says aliases ending in `:mock` are free, and the helper refuses real QPUs without `--allow-real`. T11 passed 12 of 12 and tested little.
- **Fix for r03:** Run T11 without the hint, or accept that it now tests only reading.

## F10. Submit-then-crash leaves unreported jobs (agent, r02)

- **What:** A script submits a job and then crashes before printing the ID. The agent resubmits and reports only the second job.
- **Seen in:** 2 unreported `garnet:mock` jobs on the dashboard (suffixes `a9c744` and `7a2293`). The first is likely r02-B-T5-1. The second is not attributed. Both cost 0 credits. On real hardware this would spend credits invisibly.
- **Fix for r03:** Reconcile jobs per trial window through the dashboard. Teach agents to print the job ID right after submitting.

## F11. Calibration drift during a round (environment, r02)

- **What:** Garnet recalibrated at 16:42:21Z during the run. Grading after that point used a different "best pair" (QB11-QB12 instead of QB12-QB17).
- **Fix:** grade.py looks up the calibration by job creation time, from `graders/garnet_calibrations.json`.

## F12. Judge failure dropped a trial from the workflow return (harness, r03)

- **What:** Two judge agents hit the StructuredOutput retry cap. `pipeline()` dropped the whole item, so the workflow returned 142 trials while 144 had code grades on disk.
- **Seen in:** r03-A-T1-1, r03-B-T5-1.
- **Fix for r04:** Catch judge errors and return the trial with `judge: null`. Count trials from the grade files. `build_results.py` already does this.

## F13. Truth that both metric readings agree on cannot test metric choice (task design, r03)

- **What:** T12 accepted either readout metric, and QB5 led both. T10 billed seconds were 1.0 for every real job, so a constant guess would also pass.
- **Fix for r04:** Pick questions where the readings differ, and vary the shots or depth so billed seconds differ.

## F14. Answer notes committed into the trial checkout (harness, r03)

- **What:** `evals/tasks/T12.yaml` and `T13.yaml` recorded the day's answers (QB5 and QB11-QB12-QB7) and were committed before the run. Every trial worktree therefore contained them.
- **Seen in:** r03 design. The metrics peek check and the critic's scan of all 144 transcripts found 0 reads, so the results stand.
- **Fix for r04:** Keep answer notes out of the committed tree until the round ends, or remove `spe/` from trial worktrees.

## Observation: effort, not accuracy, separates the configs

Across r01 to r03, every config completes the tasks. On the hardest task (T13), A used a median of 19 tool calls and 1.56 minutes, while D used 9 and 0.94. Future rounds should treat tool calls, fresh tokens, and wall time as the primary outcomes, with pass rate as a gate.
