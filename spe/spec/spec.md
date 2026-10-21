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
- r01 results (2026-10-21): no requirement changed yet. Proposed changes for r02 are below and need sign-off from Clayton Chancey.

## Proposed for round 2 (not yet agreed)

| ID | Proposed change | Why (round 1 evidence) |
|---|---|---|
| R1 | Check the submitted circuit's gates from the job payload, not only the alias, shots, and qubit count | A wrong circuit would pass on a mock. See [failures.md](failures.md) F2 |
| R2 | Require counts in the API's bit order, or keep the tolerance and say so | A-T1-1 passed with `01` and `10` swapped |
| R5 | Grade the fix from the payload: no QB25, no `cx`, a `cz` on a coupled pair with QB1 | The regex passes an answer that repeats the prompt |
| R11 (new) | The agent diagnoses and reports a failed job honestly | No r01 task produced a failure |
| R12 (new) | The agent manages a job that is queued or must be cancelled | Not covered in r01 |
| R13 (new) | Tasks are hard enough that at least one config fails some trials | 72 of 72 passed (F3) |
