# SPE: evaluating a Claude Code agent that runs IQM jobs

This folder applies the SPE loop (Specify, Predict, Evaluate) from Clayton Chancey's "SPE for Practitioners" (2026-10-17) to one question: how well does a Claude Code agent use the IQM Resonance API to run jobs?

## The loop here

| Step | File | Status |
|---|---|---|
| Specify | [spec/spec.md](spec/spec.md), [spec/disagreements.md](spec/disagreements.md), raw record in [spec/transcripts/](spec/transcripts/) | r01 to r05 written 2026-10-21. r06 proposals at the end of spec.md |
| Predict | [predictions/](predictions/), approved plans in [plans/](plans/) | r01 to r05 saved and committed before their runs. r06 draft |
| Evaluate | [evals/](evals/) and the results in [evals/results/](evals/results/) | r01: 72 of 72 passed, 3.60 credits. r02: 115 of 126 passed by the pre-registered grader, 7.20 credits. r03: 144 of 144 passed, 7.20 credits, 0 unreported jobs. r04: 72 of 80 passed (73 with the fixed grader), 3.60 credits, 3 unreported mock jobs. r05: 41 of 44 passed (42 with the fixed grader), 3.00 credits, 0 unreported jobs |
| Learn | [prediction-log.md](prediction-log.md), [failures.md](failures.md) | r01 to r05 written. In r05, Claude's banded effort predictions beat the baseline for the first time, and IQM's noise model beat Claude on real edge probabilities |

## Layout

| Path | Purpose |
|---|---|
| `agent-tools/iqm_run.py` | The helper that config C and D agents may use. It is the only file in `spe/` an agent under test is told about |
| `evals/configs/` | One file per configuration, plus the common preamble every trial gets |
| `evals/tasks/` | T1 to T18 with pass rules. Prompts are in each round's workflow script |
| `evals/graders/grade.py` | Code grader. Checks each reported job against the IQM API and simulates its payload against exact physics. `--selftest` runs 57 fixtures |
| `evals/graders/metrics.py` | Reads a trial's subagent transcript for tokens, tool calls, tool errors, wall time, and peeks |
| `evals/graders/judge.md` | Process rubric for the LLM judge. Descriptive only |
| `evals/graders/explain.md` | Explanation rubric for the r04 judge: does the answer teach a non-expert. Descriptive only |
| `evals/harness/rNN-workflow.js` | The Workflow script that ran each round |
| `evals/harness/r04_oracles.py` | Builds and submits the r04 oracle and negative jobs |
| `evals/harness/ledger.md` | Credit balances and real-QPU spend |
| `evals/harness/r05_oracles.py` | Builds the r05 oracle and negative jobs, the real Garnet probe, and the IQMFakeGarnet baseline |
| `knowledge/` | Plain-language write-ups for readers who know neither Claude Code nor quantum computing |
| `evals/results/rNN/` | Per-trial files, `rNN.json`, the scorecard, and the dashboard |

## How a trial runs

1. The Workflow starts a Claude Code subagent in its own git worktree, with the config's preamble and the task. Configs A to C use Opus 5.5. Config D uses Sonnet 5.5.
2. A grading subagent (Sonnet, low effort) saves the trial's result object, then runs `grade.py` and `metrics.py`. Their JSON files are the source of truth.
3. A judge subagent (Opus 5.5) applies `judge.md` to the transcript.
4. Mock tasks (T1 to T5) run in parallel. The real-hardware task (T6) runs one trial at a time behind a credit gate.
5. Cells where only some trials passed get 2 more trials.

## How to rerun

```bash
.venv-iqm/bin/python -I spe/evals/graders/grade.py --selftest
```

Then run the Workflow tool with `scriptPath: spe/evals/harness/r05-workflow.js` and `args: {"round": "r06", "creditCap": <cap minus probe>, "topupCap": 24, "root": "<absolute path to this repo>"}`. Write and commit `predictions/r06.yaml` first. The harness needs an IQM token in `.env` (see `.env.example`) and a Python 3.12 environment at `.venv-iqm` with `iqm-client[qiskit]==35.0.3`, `requests`, and `python-dotenv`.

## Git history is the loop

Each round is a run of commits named after its SPE step, and each round ends with a tag (`spe-r01`, `spe-r02`). Run `git log --oneline --decorate` to see it.

## Round 1 in one paragraph

All 4 configs passed all 6 tasks (72 of 72 trials), so the tasks cannot rank the configs on accuracy. The configs differ in efficiency. Config D (Sonnet plus the helper) had a median of 0.34 minutes and 178k tokens per trial. Config B (Opus plus docs) had 0.56 minutes and 311k tokens. Real Sirius Bell jobs reached a mean parity of 0.936 and cost 0.30 credits each. 54 of the 60 tool errors came from the worktree guard, not from the agents. Round 2 needs harder tasks and stricter graders. See [failures.md](failures.md) and the proposals at the end of [spec/spec.md](spec/spec.md).

## Round 2 in one paragraph

Harder tasks and a grader that simulates each job's circuit finally separated the configs a little. With one invalid check removed (T10 credits, failures.md F6), A passed 31 of 32, B 30 of 30, C 30 of 30, and D (Sonnet) 31 of 34. D's misses were real: a units mix-up that the mock hid (F8) and two status-field slips (F7). The guard tip cut guard errors from about 0.75 to 0.21 or fewer per trial. Garnet recalibrated mid-round (F11), and the dashboard showed 2 unreported mock jobs (F10). Credits reconciled exactly: 18.90 left.

## Round 3 in one paragraph

With fair graders and prompts, every config passed all 12 tasks (144 of 144), including the new best-chain task T13. Effort still separated the configs. On T13, A needed a median of 19 tool calls and 1.56 minutes. D (Sonnet plus the helper) needed 9 calls and 0.94 minutes. Asking agents to print job IDs right after submitting cut unreported jobs from 2 to 0. Credits reconciled exactly at 11.70. Claude's predictions matched where they kept the baseline and missed on every "this will be hard" call. Round 4 should make effort the primary outcome (spec R19).

## Local-only material

The IQM API docs (`docs/iqm/` and siblings), the account runbooks, `CLAUDE.md`, and `KEYS.md` were available to the agents during these rounds but are kept out of the public repo. Links to them from this folder resolve only in the original local checkout.

## Rules for this folder

- Write the prediction before the round runs, with author and date.
- Do not commit `spe/` while a round is running. Worktree trials check out `HEAD`, so uncommitted graders and predictions stay out of their view.
- `spe/` is committed, so trial worktrees contain the graders. `metrics.py` flags any read of a `spe/` path other than `agent-tools`, and the workflow halts on a peek. r02 had 0 peeks.
- Real-QPU credits are capped per round in the ledger.

## Round 4 in one paragraph

The user asked for experiments a non-expert could request in plain language, in the areas where quantum advantage is most likely to appear first. The new tasks were spin-chain dynamics (T14), the hydrogen molecule's ground state (T15), random circuit sampling scored with XEB (T16), GHZ states of 2 to 5 qubits on real Sirius (T17), and zero-noise extrapolation (T18). The grader simulated every submitted circuit and compared it with exact physics. Accuracy separated the configs for the first time. A and C passed all 22 of their trials. B passed 21 of 22. D (Sonnet plus the helper) passed 11 of 18 on the new mock tasks, and 1 of 5 on T18. There it transpiled each folded copy separately, which broke the noise scaling, and then told the user the scaling was right (failures.md F19, F20). After the run, two grader bugs were fixed (F16, F17). They moved the total from 72 to 73 of 80. Real Sirius GHZ agreement fell from 0.947 at 2 qubits to 0.791 at 5. Every real job billed 1.0 second, and credits reconciled exactly at 7.80.

## Round 5 in one paragraph

The user asked for very specific materials science examples and a truly interesting prediction that would then be tested. The tasks were the KCuF3 Heisenberg chain (T19), the Hubbard dimer as a toy model of the Mott insulator La2CuO4 (T20), and the SSH chain of polyacetylene on real Garnet (T21). Claude predicted that polyacetylene's topological edge state would stay clearly visible on real hardware, with a raw edge contrast of 3 or more. Across 5 real jobs the contrast averaged 3.25 (median 3.63), so the call held on the pool. It failed on 2 of the 5 chains, and the ratio ranged from 1.79 to 4.46 on one calibration set (failures.md F26). IQM's own noise model beat Claude on the edge probabilities. A, B, and C passed every trial after one grader fix (F23). D passed 13 of 15 and missed only on reporting qubit names (F24). Credits reconciled exactly at 4.80, with 0 unreported jobs. The plain-language write-up is [knowledge/quantum-materials-explainer.md](knowledge/quantum-materials-explainer.md).
