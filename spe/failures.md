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
