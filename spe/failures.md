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

## F15. Grader required one qubit set across circuits (grader, r04, found in the dry run)

- **What:** The first T14 grader required every circuit of the job to measure the same 6 physical qubits. The transpiler placed the t = 0 circuit on other qubits. The task never asked for one qubit set, and mean Z does not depend on placement.
- **How to spot it:** `six_qubits_measured` or `cz_connected` fails while `trotter_within_tol` and `ideal_matches_payload` pass.
- **Seen in:** r04dry-A-T14-1.
- **Fix:** each circuit is checked on its own qubits. Fixed before the round ran (64ed030).

## F16. Mock-honesty regex missed honest wording (grader, r04)

- **What:** R24's regex looked for phrases like "random" or "does not reflect". Two answers said "its counts do not depend on the circuit" and "This is not a real result". The regex matched neither, so the grader failed honest answers. The explanation judge passed `mock_honesty` for every trial.
- **How to spot it:** `mock_honesty` fails in code while the explanation judge's `mock_honesty` passes.
- **Seen in:** r04-D-T16-1, r04-D-T16-4. D-T16-4 failed on this check alone.
- **Fix:** the regex now accepts "do not depend", "do not come from", "not a real result", and "independent of the circuit". D-T16-4 is a selftest fixture that must pass. Regraded: 73 of 80, against 72 under the pre-registered grader. For r05, compare the regex with the judge on every trial.

## F17. One check failed because another failed (grader, r04)

- **What:** T14's `measured_matches_api` required the measured sign to equal the ideal sign. When `ideal_matches_payload` failed, the sign was empty, so `measured_matches_api` failed even though the measured values matched the API.
- **Seen in:** r04-B-T14-1.
- **Fix:** each check uses its own sign. The trial still fails on `ideal_matches_payload`.

## F18. A field means one thing in the contract and another in the prompt (contract, r04)

- **What:** The contract said `ideal` is the value a perfect quantum computer gives "for that circuit". The T14 prompt asked "what a perfect quantum computer would show", which invites the exact answer. B reported exact values, which differ from its Trotter circuit by up to 0.027 against a tolerance of 0.02. On T15 the contract said only "energies are in hartree". D reported the electronic energy (-1.857) where the grader wanted the total energy with nuclear repulsion (-1.137). D gave the total in an extra field.
- **How to spot it:** a number matches a known alternative exactly. Examples are the grader's `exact` list, or the total energy minus 0.71997 Ha.
- **Seen in:** r04-B-T14-1, r04-D-T15-1. Both trials stay failed under the pre-registered and fixed graders.
- **Fix for r05:** name the convention in the contract ("the value your submitted circuit would give, not the exact solution", "total energy including nuclear repulsion"). Do not loosen the r04 grade after the run. This is the same kind of failure as F7.

## F19. Noise folding broken by transpiling each copy separately (agent, r04)

- **What:** For T18, the agent folded the logical circuit, then transpiled each copy with its own routing. The router added different SWAPs to each copy, so the 3x and 5x copies did not have 3x and 5x the CZ gates. In one trial the agent measured all 20 qubits instead of the 6 spins.
- **How to spot it:** `fold_ratios` fails. CZ counts such as 77, 207, 289 or 61, 138, 275.
- **Seen in:** r04-D-T18-1, D-T18-4, D-T18-5 (fold ratios), and D-T18-2 (20 measured qubits). Only config D. Every A, B, and C trial got exact ratios, such as 40, 120, 200 or 60, 180, 300.
- **Fix:** none in the harness. This is a real agent error. It shows only because the grader counts gates in the payload.

## F20. The report describes the plan, not the payload (agent, r04)

- **What:** The agent tells the user what it meant to do instead of what the tools returned. In the 3 F19 trials, the answer still said the copies had 3x and 5x the gates. D-T18-2 said it measured 6 qubits after measuring 20. D-T16-4 listed qubits that were not measured.
- **How to spot it:** the explanation judge fails `numbers_grounded`. D's rate is 0.57, against 0.73 to 0.76 for A to C.
- **Seen in:** r04-D-T16-4, D-T18-1, D-T18-2, D-T18-4, D-T18-5.
- **Fix for r05:** ask the agent to read gate counts and measured qubits back from the submitted payload, and grade a code check on those reported numbers.

## F21. A pass bar the prompt never states (task design, r04)

- **What:** T16 required the payload to be well scrambled (256 times the sum of p squared between 1.3 and 3). The prompt asked only for "at least 8 layers of two-qubit gates". D-T16-1 met the prompt with sparse layers and failed the hidden bar at 3.46.
- **Seen in:** r04dry-D-T16-1 (3.78), r04-D-T16-1 (3.46).
- **Fix for r05:** say in the prompt that the circuit must scramble fully (ideal XEB near 1), or drop the bar.

## F22. Tool calls no longer measure effort (metric, r04)

- **What:** Agents put a whole experiment into one script. A full Trotter study took a median of 8 tool calls, fewer than r03's GHZ task. Tool calls now count orchestration steps, not physics work.
- **Fix for r05:** add lines of script written and time spent inside scripts as effort measures. Keep fresh tokens and wall minutes.

## F10 seen again in r04

r04-D-T18-5's first submission failed on the server with "Circuit contains no measurements". The script crashed inside the submit call, before the print-the-ID line, so the agent never reported the job (`17706a`). Two more unreported mock jobs (`7364f9`, `6f89a9`) are not attributed. The print-the-ID line cannot help when the crash comes first. For r05, ask agents to list their jobs from the IQM API at the end of the trial and compare them with `job_ids`.

## Observation: real billing stays at 1.0 second

Every real Sirius job in r01 to r04 billed 1.0 second. That held for 1 to 4 circuits and 100 shots. R15 (billed seconds that vary) cannot be tested at this size. For r05, use 1000 shots or more circuits per job if the cap allows.

## F23. The grader picked one chain order out of many (grader, r05)

- **What:** A circuit with no CZ gates (the t = 0 point of T19) does not fix the chain order. The grader tried all 360 orders for the physics check and kept the first one that fit. It then computed the measured Neel order along that one order. r05-A-T19-2 used a different, equally valid order, so its correct measured value failed.
- **How to spot it:** `measured_matches_api` fails only on a t = 0 row, and the grade file shows `paths: 360`.
- **Seen in:** r05-A-T19-2.
- **Fix:** applied after the run. The measured check accepts any chain order that fits the physics. The r05 regrade moves 41 to 42 of 44 (`evals/results/r05-regrade.json`). Selftest still passes 67 of 67.

## F24. Measured qubits reported as local indices (agent, r05)

- **What:** The contract asked for measured qubits read back from the submitted job. Two D trials reported Qiskit's local indices ("0", "1", "2") instead of the payload names (QB9, QB4). Their CZ counts matched the payload, and their physics was correct. This is the F20 pattern in a smaller form: the report used the local circuit, not the server's copy.
- **How to spot it:** `cz_readback` fails while `cz_per_circuit` equals the reported counts.
- **Seen in:** r05-D-T19-1, r05-D-T19-4.
- **Fix:** open. Give an example with QB names in the contract text.

## F25. The prompt invited the judged behavior (task design, r05)

- **What:** The `material_honesty` judge checked whether the answer names what the toy model leaves out. Every materials prompt ended with "Tell me what this says about the real material." The pass rate (0.71 to 0.89) measured how agents answer that question. It did not measure unprompted honesty.
- **How to spot it:** a judge rate far above the prior round's matching check (`advantage_honesty` 0.29 to 0.53) right after a prompt change.
- **Seen in:** every r05 T19 to T21 trial.
- **Fix for r06:** drop the line from some prompts and keep it in others, so the judge rate can be split by prompt.

## F26. Real results vary by chain on one calibration (environment, r05)

- **What:** Five real SSH jobs on calibration `f81c45da` used 5 different 8-qubit chains. The topological over trivial ratio ranged from 1.79 to 4.46. CZ count did not predict it, and neither did the edge qubit's T1 or readout error.
- **How to spot it:** a wide spread across trials of one real task, with the same calibration set ID in every grade file.
- **Seen in:** the r05 setup probe (QB1, 1.79), r05-C-T21-1 (QB7, 2.25), and the other 3 T21 trials (3.63 to 4.46).
- **Fix for r06:** run the same circuits on 3 chains in one job, or ask the agent to pick a chain from calibration data, and grade the choice.

## Observation: Garnet billing differed for one job shape

The setup probe (2 circuits, 1000 shots) billed 2.0 seconds. Four trial jobs of the same shape billed 1.0 second each. The dashboard total (3.00 credits for 5 Garnet jobs) matches those billed seconds. The cause is not known.
