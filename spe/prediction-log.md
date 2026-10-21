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
