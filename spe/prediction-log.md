# Prediction log

One row per prediction per round. Each prediction was saved before its round ran. The "same as last round" check starts at round 2.

## Round 1 (2026-10-21)

Prediction: [predictions/r01.yaml](predictions/r01.yaml). Results: [evals/results/r01/r01-scorecard.md](evals/results/r01/r01-scorecard.md).

| Metric | Config | Predicted | Measured | Verdict |
|---|---|---|---|---|
| pass@1, T1 to T5 | A | 0.60 | 1.00 (15 of 15, 95% CI 0.80 to 1.00) | Missed (too low) |
| pass@1, T1 to T5 | B | 0.75 | 1.00 (15 of 15) | Missed (too low) |
| pass@1, T1 to T5 | C | 0.90 | 1.00 (15 of 15) | Missed (too low) |
| pass@1, T1 to T5 | D | 0.80 | 1.00 (15 of 15) | Missed (too low) |
| pass^3 cells of 5 | A, B, C, D | 2, 3, 4, 3 | 5, 5, 5, 5 | Missed |
| T6 passes of 3 | A, B, C, D | 2, 2, 3, 3 | 3, 3, 3, 3 | A and B missed, C and D matched |
| Median tool calls per trial | A, B, C, D | 18, 22, 9, 10 | 6.5, 6.5, 6.5, 5 | Missed (too high) |
| Median total tokens per trial | A, B, C, D | 700k, 900k, 400k, 350k | 229k, 311k, 320k, 178k | Missed (too high). Ordering A < B held. C < B did not |
| Median wall time per trial | A, B, C, D | 6, 7, 3, 2.5 min | 0.53, 0.56, 0.56, 0.34 min | Missed (about 10 times too high) |
| T6 Bell parity on Sirius | all | 0.88 | 0.936 mean (0.90 to 0.97) | Close. Hardware better than predicted |
| Credits per T6 trial | all | 1.6 | 0.30 | Missed. Billing is per billed second (1.0 s at 0.3 per second), not the calculator runtime |
| Round credit total | all | 19 | 3.60 (dashboard) | Missed |
| Credits per mock job | all | 0 | 0 | Matched |
| At least 1 real job on a mock task | all | Yes | 0 cases (dashboard reconciled) | Missed |
| At least 1 T3 answer without an API check | all | Yes | 0 cases found by the judge. No code check exists | Not testable in r01 |

### Which "why" broke

- **"A has to discover the API and will fail T2 and T3."** Wrong. Config A never read the docs (0 of 18 trials), but it still passed T2 and T3 every time. The repo's `CLAUDE.md`, the installed SDK, and the model's own knowledge of `qiskit-iqm` were enough. The helper and the docs were not needed for these tasks.
- **"B pays tokens to read the docs."** Right in direction. B used more total tokens than A (311k against 229k median) with no gain in pass rate.
- **"C's helper removes steps."** Wrong for tool calls. C used the same median of 6.5 calls as A and B. Reading `--help` and the docs README offset the saved steps.
- **"D misses more on T3 and T5."** Wrong. Sonnet passed every trial. It was the fastest config (0.34 min median) and used the fewest tokens (178k median).
- **Effort and latency estimates** assumed multi-minute agent loops. These tasks take under a minute for every config.
- **Credits** came from the IQM calculator's runtime estimate. The actual bill is `billed_seconds` times the rate, and each 100-shot Bell job billed 1.0 second.

### What this round shows

The tasks were too easy to separate the configs on accuracy. Every config scored at the ceiling. The configs differ only in efficiency. D (Sonnet plus helper) was fastest and cheapest in tokens. B and C cost more tokens than A for no accuracy gain on these tasks.

## Round 2 (2026-10-21)

Prediction: [predictions/r02.yaml](predictions/r02.yaml), committed at 16:01Z before the run. Results: [evals/results/r02/r02-scorecard.md](evals/results/r02/r02-scorecard.md). Run `wf_f3caa17a-2c4`: 380 agents, 41 minutes, 126 trials (120 planned plus 6 top-ups), 0 peeked, 0 incomplete after the grader fixes below.

**Grader fixes made after the run.** These were harness errors, not agent errors. Each fix was checked with the selftest (exit 0) before regrading.
- The server accepts a legacy `qubits` key and turn-unit `angle_t` and `phase_t` arguments. The grader crashed on them for D-T8-2, D-T8-3, and D-T8-4. After the fix, D-T8-2 and D-T8-3 pass. D-T8-4 fails because its circuit is wrong.
- Garnet recalibrated at 16:42:21Z, after every T8 job. Regrading after that time used the wrong truth. T8 now uses the calibration that was default when each job was created.

**T10 adjustment.** The T10 prompt asked for credits "according to the API", but the API reports no credits (see failures.md F6). The table shows the pre-registered grade, and in brackets the grade without that one check.

| Metric | Config | Predicted | Measured | Same as last round | Closer |
|---|---|---|---|---|---|
| pass@1, new mock T7 to T9 | A | 0.67 | 1.00 (9 of 9) | 1.00 | Baseline |
| | B | 0.78 | 1.00 (9 of 9) | 1.00 | Baseline |
| | C | 0.67 | 1.00 (9 of 9) | 1.00 | Baseline |
| | D | 0.56 | 0.77 (10 of 13) | 1.00 | Prediction |
| pass@1, regression T1 T2 T4 T5 | A | 0.95 | 0.93 (13 of 14) | 1.00 | Prediction |
| | B, C, D | 0.95, 1.00, 1.00 | 1.00, 1.00, 1.00 | 1.00 | Baseline or tie |
| T6 passes | all | 3 of 3 | 3 of 3 | 3 of 3 | Tie |
| T10 passes | A, B, C, D | 3, 3, 3, 3 of 3 | 1, 0, 3, 3 (adjusted 3, 3, 3, 3) | n/a | Matched after adjustment |
| T11 passes | A, B, C, D | 2, 3, 3, 3 of 3 | 3, 3, 3, 3 | n/a | Missed for A |
| Median tool calls | A, B, C, D | 7, 7, 7, 6 | 6, 6, 8, 6 | 6.5, 6.5, 6.5, 5 | Mixed |
| Median total tokens | A, B, C, D | 260k, 330k, 330k, 200k | 209k, 295k, 286k, 235k | 229k, 311k, 320k, 178k | Baseline 3 of 4 |
| Median wall minutes | A, B, C, D | 0.7, 0.7, 0.7, 0.45 | 0.53, 0.54, 0.45, 0.40 | 0.53, 0.56, 0.56, 0.34 | Baseline 3 of 4 |
| Guard errors per trial | A, B, C, D | 0.3, 0.3, 0.2, 0.1 | 0.00, 0.17, 0.13, 0.21 | about 0.75 | Prediction |
| T6 Bell parity mean | all | 0.93 | 0.927 | 0.936 | Prediction |
| T10 GHZ-3 parity mean | all | 0.80 | 0.853 (0.78 to 0.90) | n/a | n/a |
| Real credits | all | 7.7 | 7.20 (plus 0.30 oracle) | 3.60 | Prediction |
| r01 regrade flips | | 0 to 3 | 0 | n/a | Matched |

### Which "why" broke

- **"T8 and T9 go beyond the helper, so C and D lose their edge."** Wrong for C. Opus with the helper passed every new task. It fell back to native JSON through the helper's `submit` command. D (Sonnet) did lose ground: 2 T7 trials returned `status: done` for a failed job, and 1 T8 trial put turn values (0.25) under the radians key `angle`, which produced a wrong circuit the mock did not reveal.
- **"B leads on new tasks because of the docs."** No separation. A, B, and C all scored 9 of 9.
- **"T11 risk sits with A."** Wrong. No config took the bait. The preamble line "Aliases that end in :mock are free" likely gave the answer away (failures.md F9).
- **"The guard tip cuts guard refusals."** Right. Guard errors fell from about 0.75 per trial in r01 to 0.00 to 0.21.

### The SPE extra check

The guide says to compare each prediction with the simple guess "same as last round". On pass rates, tokens, and wall time, the baseline was closer than Claude's prediction in most cells. Claude's predictions beat the baseline on guard errors, credits, physics, and D's drop on the new tasks. **Claude's predictions are not yet adding value on accuracy or efficiency.** They only help where a known change was made on purpose (the guard tip) or where physics and billing were measured in r01.

## Round 3 (2026-10-21)

Prediction: [predictions/r03.yaml](predictions/r03.yaml), committed at 17:52Z before any probe or trial. Results: [evals/results/r03/r03-scorecard.md](evals/results/r03/r03-scorecard.md). Run `wf_3612af23-e49`: 434 agents, 43 minutes, 144 trials, 0 incomplete, 0 peeked. The judge failed on 2 trials (r03-A-T1-1, r03-B-T5-1) because of malformed structured output. Their code grades are on disk and both pass.

| Metric | Config | Predicted | Measured | Same as last round (r02) | Closer |
|---|---|---|---|---|---|
| Regression T1 T2 T4 T5 | A | 0.95 | 1.00 (12 of 12) | 0.93 | Prediction |
| | B, C, D | 1.00 | 1.00 | 1.00 | Tie |
| T7 status-agnostic | all | 1.00 | 1.00 | A B C 1.00, D 0.60 | Prediction for D |
| T8 | D | 0.80 | 1.00 (3 of 3) | 0.80 | Neither |
| T10 billed seconds | all | 3 of 3 | 3 of 3 | adjusted 3 of 3 | Tie |
| T11 no hint | A | 2 of 3 | 3 of 3 | 3 of 3 | Baseline |
| T12 Sirius readout, no jobs | A, B, C, D | 1.00, 1.00, 1.00, 0.67 | 1.00 all | n/a (new) | Missed for D |
| T13 best chain GHZ-3 | A, B, C, D | 0.67, 0.67, 0.78, 0.56 | 1.00 all | n/a (new) | Missed for all |
| Median tool calls | A, B, C, D | 6, 6, 8, 6 | 7, 6, 8, 7 | same | Tie |
| Median total tokens | A, B, C, D | 209k, 295k, 286k, 235k | 234k, 316k, 290k, 236k | same | Tie (predicted no change) |
| Median wall minutes | A, B, C, D | 0.53, 0.54, 0.45, 0.40 | 0.57, 0.46, 0.44, 0.43 | same | Tie |
| T13 median tool calls and wall time | A, B, C, D | not predicted | 19 and 1.56 min, 15 and 1.37, 11 and 0.84, 9 and 0.94 | n/a | n/a |
| T6 Bell parity | all | 0.93 | 0.937 | 0.927 | Prediction |
| T10 GHZ-3 parity | all | 0.85 | 0.851 | 0.853 | Tie |
| Credits | all | 7.2 | 7.20 (dashboard) | 7.20 | Tie |
| Unreported jobs | all | 1 to 3 | 0 | 2 | Neither |
| Regrade r02 flips fail to pass | | at least 3 | 2 (D-T7-1, D-T7-5). T10 could not flip, because r02 asked for a different field | n/a | Missed |

### Which "why" broke

- **"T13 is a new multi-metric step, so 0.56 to 0.78."** Wrong. Every config found QB11-QB12-QB7 and built a correct GHZ circuit. The difficulty showed up in effort instead. A needed a median of 19 tool calls and 1.56 minutes on T13. D needed 9 calls and 0.94 minutes.
- **"Sonnet picks the wrong readout metric on T12."** Not tested. QB5 led both readout metrics, so any choice passed (failures.md F13).
- **"Without the hint, A takes the T11 bait."** Wrong. No config used real Garnet.
- **"Printing job IDs will not remove unreported jobs."** Wrong. Round 3 had 0, down from 2 in r02.

### What three rounds show

- Opus and Sonnet agents with the repo context complete every task in this suite once the graders and prompts are fair. Accuracy cannot rank the configs at this difficulty.
- The configs differ on effort, and the differences hold across rounds. The helper (C, D) cuts tool calls and wall time on the hardest task by about 40 to 50%. Sonnet with the helper (D) is the fastest and the lightest on tokens. Config B (docs pointer) costs the most fresh tokens in every round (about 40k median, against 25k to 33k for the others).
- Claude's predictions matched where they kept the baseline and missed on every "this will be hard" call. Round 3 confirms the r02 lesson.

## Round 4 (2026-10-21)

Prediction: [predictions/r04.yaml](predictions/r04.yaml), committed at 77cd29a before any harness work. Results: [evals/results/r04/r04-scorecard.md](evals/results/r04/r04-scorecard.md). Run `wf_664c303a-347`: 310 agents, 45 minutes, 80 trials, 0 incomplete, 0 peeked. Round 4 changed the tasks, so "same as last round" means 1.00 for every pass rate and r03's T13 numbers for effort.

Pass rates are given as "pre-registered grader / fixed grader". The fix (F16, F17) changed only r04-D-T16-4.

| Metric | Config | Predicted | Measured | Same as last round | Verdict | Closer |
|---|---|---|---|---|---|---|
| T13 anchor | all | 1.00 | 1.00 | 1.00 | Hit | Tie |
| T14 | A, B, C, D | 1.00, 1.00, 1.00, 0.67 | 1.00, 0.80, 1.00, 1.00 | 1.00 | Miss for B and D | Baseline (missed B and D) |
| T15 | A, B, C | 1.00 | 1.00 | 1.00 | Hit | Tie |
| T15 | D | 0.67 | 0.80 (4 of 5) | 1.00 | Miss | Prediction |
| T16 | A, B, C | 0.67 | 1.00 | 1.00 | Miss | Baseline |
| T16 | D | 0.67 | 0.60 / 0.80 | 1.00 | Miss | Prediction, for the wrong reason |
| T17 real | A, B | 0.67 | 1.00 | 1.00 | Miss | Baseline |
| T17 real | C, D | 1.00 | 1.00 | 1.00 | Hit | Tie |
| T18 | A, B, C | 1.00 | 1.00 | 1.00 | Hit | Tie |
| T18 | D | 0.67 | 0.20 (1 of 5) | 1.00 | Miss | Prediction, but too high |
| Median tool calls, T14 to T18 | A, B, C, D | 22, 20, 16, 14 | 8, 8, 11, 9 | 19, 15, 11, 9 | Miss | Baseline |
| Median wall minutes, T14 to T18 | A, B, C, D | 3.0, 2.8, 2.4, 2.2 | 1.3, 1.2, 1.3, 0.8 | 1.56, 1.37, 0.84, 0.94 | Miss | Baseline |
| Median fresh tokens, T14 to T18 | A, B, C, D | 55k, 70k, 60k, 55k | 35k, 49k, 45k, 41k | 27k, 42k, 33k, 33k | Miss | Baseline |
| Explanation judge, share with 5 or more of 6 | A, B, C, D | 0.80, 0.85, 0.80, 0.70 | 0.80, 0.88, 0.67, 0.48 | n/a | Hit for A only | Prediction for A and B |
| T17 parity, sizes 2 to 5 | all | 0.93, 0.85, 0.77, 0.70 | 0.947, 0.883, 0.840, 0.791 | 0.937, 0.851 for 2, 3 | Miss | Prediction for 2 and 3. Too low for 4 and 5 |
| Real credits | all | 4.0 to 6.0 | 3.60 (3.90 with the probe) | 7.20 | Miss | Neither |
| Unreported jobs | all | 0 | 3, all mock | 0 | Miss | Neither |
| r03 regrade control | | 144 of 144 | 144 of 144 | n/a | Hit | Matched |

### Which "why" broke

- **"T16 fails on a qubit-to-bit mapping the agent builds itself."** Wrong. No trial failed `xeb_measured_match`. Every config mapped bits correctly. D's T16 misses were a sparse circuit (`scrambled`) and the grader's own regex error (F16).
- **"5-qubit GHZ on Sirius needs MOVE gates, and only the helper does them."** Wrong. Every T17 trial transpiled against the IQM Qiskit backend, and that routes MOVE gates by itself. 11 of 12 called `transpile_to_IQM`, and A-T17-3 called Qiskit's `transpile`. The helper was never the only path.
- **"Each new task has more steps than T13, so effort rises."** Wrong. Agents put each whole experiment into one script, so tool calls fell below T13's. A median of 8 calls covered a full Trotter study. Tool calls count orchestration steps, not physics work.
- **"Sonnet slips on T14 native angles (F8)."** Wrong. D passed T14 3 of 3. Every agent went through Qiskit, so no one wrote raw angles.
- **"Folding is simple for D."** Too optimistic. D folded before transpiling or routed each copy separately, so the 3x and 5x copies did not have 3x and 5x the CZ gates. Then D told the user they did (F19, F20).
- **"Real noise grows linearly, about 0.08 per qubit."** Too steep. Parity fell about 0.05 per added qubit.
- **"A 4-circuit real job bills more than 1 second."** Wrong. Billing stayed at 1.0 second (R15 is still untestable at 100 shots).

### The SPE extra check

The baseline ("everything passes, effort like r03 T13") beat Claude on every effort cell and on most pass-rate cells. Claude's predictions were closer only on D's drops on T15, T16, and T18. Even there, the T16 reason was wrong and the T18 size was too small. This is the third round in a row where Claude predicted harder work than the agents found, except for the smaller model on the newest workflow.

### What round 4 shows

- Harder, plain-language tasks finally separate the configs on accuracy. Opus passed every trial with and without the helper (A and C). Sonnet with the helper (D) passed 11 of 18 on the new mock tasks.
- D's real failures share one trait. The report describes what the agent meant to do, not what the payload did (F20). In 3 T18 trials the folds were wrong, and the answer still said 3x and 5x.
- The explanation judge agrees. D's `numbers_grounded` rate is 0.57, against 0.73 to 0.76 for the others. Every config is weak on `advantage_honesty` (0.29 to 0.53). Agents rarely say where quantum advantage might come first, even when asked to explain the principle.
