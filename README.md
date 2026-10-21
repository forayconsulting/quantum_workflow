# quantum_workflow

When will a quantum computer answer a real business question better than a classical computer? Proving that will take a date, a cost, and a fair classical comparison. This repo builds one part that such a comparison would need. It tests whether an AI agent can submit, track, and report quantum jobs correctly.

Nothing here shows quantum advantage. Quantum advantage means a quantum computer does a task faster, cheaper, or more accurately than the best known classical method. Teams have reported it on scientific benchmark tasks. We know of no verified quantum advantage on a commercially useful problem as of October 2026. Every circuit here uses 2 or 3 qubits, and a laptop can simulate each one.

## What this repo does today

Claude Code agents get small tasks and run them on IQM Resonance, a cloud quantum service. This repo uses 2 of its devices: Garnet (20 qubits) and Sirius (24 qubits). Each device also has a free mock. A mock accepts jobs but returns made-up counts without simulating anything. A job that runs a circuit 100 times (100 shots) on real Sirius hardware costs 0.30 credits.

The eval compares 4 agent setups. Each setup adds one thing to the setup before it:

- A: Opus with the repo as-is
- B: A plus a pointer to the docs
- C: B plus a tested helper script
- D: C running on Sonnet instead of Opus

Code decides pass or fail. The grader looks up every reported job ID in the IQM API. It also simulates the circuit the agent actually submitted on an ideal simulator. An LLM judge also reads each transcript, but its scores are descriptive only. A script blocks real-hardware jobs once a round reaches its credit limit.

## What it found

| Round | Trials passed | Real spend |
|---|---|---|
| 1 | 72 of 72 | 3.60 credits |
| 2 | 115 of 126 | 7.20 credits |
| 3 | 144 of 144 | 7.20 credits |

The Round 1 tasks were too easy. Round 2 used harder tasks, and the grader began simulating circuits. That grader crashed on 3 circuits that used an older payload format. Of those, 2 were valid, so the fixed Round 2 count is 117. In Round 3 every trial passed, so the eval compared tool calls and minutes instead. After every round, the credit ledger matched the IQM dashboard.

The mock cannot catch a wrong circuit. One agent gave an angle as 0.25 of a full turn. The API expected radians, so the circuit rotated by the wrong amount. A Bell circuit puts 2 qubits into the simplest entangled state, and a correct run gives only `00` and `11`. The Garnet mock still returned only `00` and `11`. Only simulating the submitted circuit caught the error.

In one Round 3 task, agents read Garnet's live calibration data, which lists the measured error rate of each qubit and qubit pair. Each agent picked the 3 connected qubits with the lowest errors and ran a GHZ circuit on them. A GHZ circuit puts 3 qubits into one shared entangled state. All 4 setups passed, but their median effort differed. Each median comes from only 3 trials.

| Setup | Tool calls | Minutes |
|---|---|---|
| A (Opus, repo as-is) | 19 | 1.56 |
| B (plus docs pointer) | 15 | 1.37 |
| C (plus helper script) | 11 | 0.84 |
| D (Sonnet plus helper) | 9 | 0.94 |

In Round 2, agents submitted 2 jobs that they never reported. Round 3 told agents to print each job ID right after submitting it, and unreported jobs fell to 0. The counts are small, so this is a strong hint, not proof.

Garnet recalibrated in the middle of Round 2, and the best qubit pair changed. Grading now uses the calibration that was live when each job ran.

On real hardware, the qubits agreed in about 93 percent of Bell shots and about 85 percent of GHZ-3 shots. This number catches some errors. It does not measure entanglement fidelity or speed.

## The SPE loop, and what it measured about the builder

The method is the SPE loop (Specify, Predict, Evaluate) from "SPE for Practitioners" by Clayton Chancey. The builder writes a spec, then commits a prediction with numbers before anything runs. The results update the spec.

```text
Specify   ->  spe/spec/spec.md          commit
Predict   ->  spe/predictions/rNN.yaml  commit, before any run
Evaluate  ->  results and scorecard     commit
Learn     ->  spe/prediction-log.md     predicted vs measured
Round     ->  git tag spe-r01, spe-r02, spe-r03
```

Git shows that the Round 2 and Round 3 predictions were committed before those runs started and were not changed afterward. The Round 1 prediction was committed after its run, so git alone does not prove its order.

Claude designed this eval, so the prediction log records how well one AI model predicts other AI agents. The record is not flattering:

- For Round 1, Claude predicted 2.5 to 7 minutes per trial. The measured medians were 0.34 to 0.56 minutes
- In Round 2, the guess "same as last round" came closer than Claude on most pass-rate, token, and wall-time cells
- In Round 3, Claude predicted pass rates of 0.56 to 0.78 on the GHZ task. Every setup scored 1.00

Most misses were in the same direction. Claude expected the agents it tested to do worse than they did.

The grader also made a mistake. One task asked for a credit value "according to the API," but the API returns only billed seconds. Setup B's agents said so, and the grader failed them (failure F6).

## What an agent has to do between a question and a quantum computer

A business user will not write quantum circuits. An agent will turn the question into jobs the hardware can run. That agent has 6 jobs:

1. Translate the question into a precise problem
2. Decide whether any quantum method fits (often the honest answer is no)
3. Pick hardware and qubits from live calibration data
4. Run the strongest classical baseline on the same problem
5. Verify the work with code instead of trusting the agent's own report
6. Report cost, error, and whether quantum helped

This repo tests a small part of step 3 (picking qubits on one device), plus step 5 and part of step 6. No run here has compared against a classical baseline yet.

## The goal: from a business question to a quantum experiment

This section describes a goal. It is not a result.

Take the question "Which suppliers are 2 hops from a sanctioned entity?" A standard graph search answers it on a laptop in seconds, even with millions of links. No quantum method is likely to beat that. Some papers test quantum methods on harder graph tasks, such as finding hidden clusters or matching a known fraud pattern. None has beaten strong classical solvers at a useful scale.

The best-known exponential speedup from a quantum walk (Childs and coauthors, 2003) holds only for one specially built graph, and no business graph is known to have that structure. Other known speedups for these tasks are at most quadratic, and each quantum step on error-corrected hardware is much slower than a classical step. Loading a graph with N edges also takes time that grows with N.

For now, this project aims to make an honest comparison that anyone can repeat. A person asks a question in plain English. Claude writes the spec and picks a quantum method and the strongest classical method available that day. Claude then commits a prediction, runs both methods, and reports the full time and cost.

## A benchmark for one use case over time

The same loop can ask each round whether quantum beats the classical baseline on one problem yet. Each round would commit a claim in this form:

> On problem P at size N, device D beats classical baseline B (best known as of date T) on metric M by X, with total time and cost C, including data loading.

Today the honest prediction is "no advantage." For business graph problems, every public result we know of supports that prediction. This repo has not tested it yet. Each round would log the date, the device, the calibration, the dated baseline, and the credits spent. Over time, the tags would show whether advantage arrived for that one problem, and when.

One question is still open. This repo grades each circuit by simulating it on a laptop, which fails beyond about 30 to 40 qubits. So this grader stops working long before any advantage could appear. Future tasks will need answers that a classical computer can check cheaply, such as a route cost or a graph path. A cheap check shows that an answer is valid, but not that it is the best one. Choosing those tasks is the next design problem.

## Start here

- `spe/README.md` explains the eval and each round
- `spe/prediction-log.md` lists every prediction next to its result
- `spe/failures.md` lists failure types F1 to F14, including grader and task errors
- `git log --oneline --decorate` shows the loop as commits and round tags

The author keeps the internal API docs and runbooks outside this repo.

## Run it

```bash
cp .env.example .env        # add your own tokens
python3.12 -m venv .venv-iqm
.venv-iqm/bin/pip install "iqm-client[qiskit]==35.0.3" requests python-dotenv
.venv-iqm/bin/python scripts/check_iqm.py
```

The scripts in `scripts/` check your connections to IBM Quantum, IQM Resonance, and D-Wave. They do not spend credits.