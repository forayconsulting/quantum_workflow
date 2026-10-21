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
