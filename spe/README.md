# SPE: evaluating a Claude Code agent that runs IQM jobs

This folder applies the SPE loop (Specify, Predict, Evaluate) from Clayton Chancey's "SPE for Practitioners" (2026-10-17) to one question: how well does a Claude Code agent use the IQM Resonance API to run jobs?

## The loop here

| Step | File | Status |
|---|---|---|
| Specify | [spec/spec.md](spec/spec.md), [spec/disagreements.md](spec/disagreements.md), raw record in [spec/transcripts/](spec/transcripts/) | r01 to r03 written 2026-10-21. r04 proposals at the end of spec.md |
| Predict | [predictions/](predictions/) | r01 to r03 saved and committed before their runs. r04 draft |
| Evaluate | [evals/](evals/) and the results in [evals/results/](evals/results/) | r01: 72 of 72 passed, 3.60 credits. r02: 115 of 126 passed by the pre-registered grader, 7.20 credits. r03: 144 of 144 passed, 7.20 credits, 0 unreported jobs |
| Learn | [prediction-log.md](prediction-log.md), [failures.md](failures.md) | r01 to r03 written. Predictions matched only where they kept the baseline. Effort, not accuracy, separates the configs |

## Layout

| Path | Purpose |
|---|---|
| `agent-tools/iqm_run.py` | The helper that config C and D agents may use. It is the only file in `spe/` an agent under test is told about |
| `evals/configs/` | One file per configuration, plus the common preamble every trial gets |
| `evals/tasks/` | T1 to T6 with prompts and pass rules |
| `evals/graders/grade.py` | Code grader. Checks each reported job against the IQM API. `--selftest` runs 14 fixtures |
| `evals/graders/metrics.py` | Reads a trial's subagent transcript for tokens, tool calls, tool errors, wall time, and peeks |
| `evals/graders/judge.md` | Process rubric for the LLM judge. Descriptive only |
| `evals/harness/r01-workflow.js` | The Workflow script that ran the round |
| `evals/harness/ledger.md` | Credit balances and real-QPU spend |
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

Then run the Workflow tool with `scriptPath: spe/evals/harness/r03-workflow.js` and `args: {"round": "r04", "creditCap": 10, "topupCap": 24, "root": "<absolute path to this repo>"}`. Write and commit `predictions/r04.yaml` first. The harness needs an IQM token in `.env` (see `.env.example`) and a Python 3.12 environment at `.venv-iqm` with `iqm-client[qiskit]==35.0.3`, `requests`, and `python-dotenv`.

## Git history is the loop

Each round is a run of commits named after its SPE step, and each round ends with a tag (`spe-r01`, `spe-r02`). Run `git log --oneline --decorate` to see it.

## Round 1 in one paragraph

All 4 configs passed all 6 tasks (72 of 72 trials), so the tasks cannot rank the configs on accuracy. The configs differ in efficiency. Config D (Sonnet plus the helper) had a median of 0.34 minutes and 178k tokens per trial. Config B (Opus plus docs) had 0.56 minutes and 311k tokens. Real Sirius Bell jobs reached a mean parity of 0.936 and cost 0.30 credits each. 54 of the 60 tool errors came from the worktree guard, not from the agents. Round 2 needs harder tasks and stricter graders. See [failures.md](failures.md) and the proposals at the end of [spec/spec.md](spec/spec.md).

## Round 2 in one paragraph

Harder tasks and a grader that simulates each job's circuit finally separated the configs a little. With one invalid check removed (T10 credits, failures.md F6), A passed 31 of 32, B 30 of 30, C 30 of 30, and D (Sonnet) 31 of 34. D's misses were real: a units mix-up that the mock hid (F8) and two status-field slips (F7). The guard tip cut guard errors from about 0.75 to 0.21 or fewer per trial. Garnet recalibrated mid-round (F11), and the dashboard showed 2 unreported mock jobs (F10). Credits reconciled exactly: 18.90 left.

## Round 3 in one paragraph

With fair graders and prompts, every config passed all 12 tasks (144 of 144), including the new best-chain task T13. Effort still separated the configs. On T13, A needed a median of 19 tool calls and 1.56 minutes. D (Sonnet plus the helper) needed 9 calls and 0.94 minutes. Asking agents to print job IDs right after submitting cut unreported jobs from 2 to 0. Credits reconciled exactly at 11.70. Claude's predictions matched where they kept the baseline and missed on every "this will be hard" call. Round 4 should make effort the primary outcome (spec R19).

## Rules for this folder

- Write the prediction before the round runs, with author and date.
- Do not commit `spe/` while a round is running. Worktree trials check out `HEAD`, so uncommitted graders and predictions stay out of their view.
- `spe/` is committed, so trial worktrees contain the graders. `metrics.py` flags any read of a `spe/` path other than `agent-tools`, and the workflow halts on a peek. r02 had 0 peeks.
- Real-QPU credits are capped per round in the ledger.
