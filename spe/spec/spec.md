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
