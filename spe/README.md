# SPE: evaluating a Claude Code agent that runs IQM jobs

This folder applies the SPE loop (Specify, Predict, Evaluate) from Clayton Chancey's "SPE for Practitioners" (2026-10-17) to one question: how well does a Claude Code agent use the IQM Resonance API to run jobs?

## The loop here

| Step | File | Status |
|---|---|---|
| Specify | [spec/spec.md](spec/spec.md), [spec/disagreements.md](spec/disagreements.md), raw record in [spec/transcripts/](spec/transcripts/) | r01 written 2026-10-21 |
| Predict | [predictions/r01.yaml](predictions/r01.yaml) | Saved before the run, 2026-10-21 |
| Evaluate | [evals/](evals/) and the results in [evals/results/](evals/results/) | r01 done 2026-10-21: 72 of 72 trials passed, 3.60 credits spent |
| Learn | [prediction-log.md](prediction-log.md), [failures.md](failures.md) | r01 written. Most predictions missed: the tasks were easier and faster than expected |

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

Then run the Workflow tool with `scriptPath: spe/evals/harness/r01-workflow.js` and `args: {"round": "r02", "creditCap": 25, "topupCap": 20}`. Write `predictions/r02.yaml` first.

## Round 1 in one paragraph

All 4 configs passed all 6 tasks (72 of 72 trials), so the tasks cannot rank the configs on accuracy. The configs differ in efficiency. Config D (Sonnet plus the helper) had a median of 0.34 minutes and 178k tokens per trial. Config B (Opus plus docs) had 0.56 minutes and 311k tokens. Real Sirius Bell jobs reached a mean parity of 0.936 and cost 0.30 credits each. 54 of the 60 tool errors came from the worktree guard, not from the agents. Round 2 needs harder tasks and stricter graders. See [failures.md](failures.md) and the proposals at the end of [spec/spec.md](spec/spec.md).

## Rules for this folder

- Write the prediction before the round runs, with author and date.
- Do not commit `spe/` while a round is running. Worktree trials check out `HEAD`, so uncommitted graders and predictions stay out of their view.
- Once `spe/` is committed, future worktrees will contain the graders. Before round 2, move answer keys out of the trial checkout, for example by running trials from a commit without `spe/evals/`, or by blocking those paths in trial permissions.
- Real-QPU credits are capped per round in the ledger.
