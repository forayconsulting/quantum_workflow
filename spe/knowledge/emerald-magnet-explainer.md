# Did a 54-qubit quantum computer get the physics right?

Written 2026-10-22, after round 6 of this project. This page is for a reader who has not used Claude Code and has not studied quantum computing. Every number on it comes from the files listed at the end.

## What we asked

Rounds 1 to 5 used at most 10 qubits. A laptop could check each of those results in under a second. For round 6 we asked for a harder problem that suits today's quantum computers. We moved to IQM Emerald, a real machine in Finland with 54 qubits. The experiment used every qubit and every one of the 85 connections between them.

The experiment simulates a flat sheet of 54 tiny magnets, called spins. Each spin points up or down. Each spin is linked to the spins next to it. A sideways magnetic field tries to tip the spins over. We started every spin pointing up, applied 3 rounds of the field and the links, and then measured how many spins still pointed up. That measure is the magnetization. It is 1 when every spin points up and 0 when the spins point up and down equally often. We ran it at 4 field strengths.

IBM used this same model, called the kicked Ising model, in a 2023 paper on 127 qubits. That paper claimed results beyond what classical computers could check. Within weeks, other groups reproduced its numbers on ordinary computers.

## Why a laptop can still check it

Writing down the full state of 54 qubits takes 2 to the power 54 numbers, about 18 million billion. No laptop can store that. The magnetization of one spin after 3 rounds depends only on the spins at most 2 links away, though. That is at most 13 spins. A laptop can simulate 13 spins exactly in a fraction of a second. Our checking program does this once for each of the 54 spins. This shortcut is called a light cone. The same shortcut let other groups check IBM's paper.

## What the real machine showed

We ran the experiment once on real Emerald, with 250 measurements per field strength.

| Field strength | Exact answer | Real Emerald | Real Emerald, corrected |
|---|---|---|---|
| None | 1.000 | 0.987 | 1.000 |
| Weak (0.2 pi) | 0.452 | 0.476 | 0.482 |
| Medium (0.35 pi) | 0.113 | 0.154 | 0.156 |
| Strong (0.5 pi) | 0.000 | 0.031 | 0.032 |

The corrected column divides each value by the no-field value. The exact answer at no field is 1, so this removes some of the machine's error. After that correction, the weak-field and medium-field values were within 0.03 and 0.04 of the exact answers. We had predicted a gap of 0.10 or less, so the prediction held.

Our reason was wrong, though. We expected noise to pull every value toward 0. Instead the real values came out above the exact ones. Qubits that lose energy fall back to the 0 state, and in this experiment that state counts as pointing up. So the noise pushed the magnetization up. A guess of "no noise at all" matched the raw values better than our prediction did.

This is one run with no repeats. It shows that the machine can get close. It does not show how close it gets on average.

## What it cost

IQM gives 30 free credits a month. We had 4.80 left and allowed this round to spend all of them. We predicted the job would bill 1 to 2 seconds, based on IQM's smaller 20-qubit machine. It billed 8.0 seconds, which is 6.00 credits. IQM ran the job anyway, and the account now shows −1.20 credits. IQM's own price calculator had estimated 4.6 seconds, which was closer than our guess. We now estimate every real job with that calculator before we send it.

## How the AI assistant did

Claude Code is an AI assistant that writes and runs programs. We gave it the experiment as a plain-English request and ran it 27 times in 3 setups. All 3 setups used the larger Claude model (Opus). Setup A had the project folder. Setup B also had our notes on IQM's system. Setup C also had a small tested program for sending jobs. With credits gone, every attempt used IQM's free test service. That service checks each job but returns made-up numbers.

All 27 attempts passed every check. In every attempt, the assistant found the light-cone shortcut on its own and computed the exact answers correctly. So this task no longer separates the setups. We had predicted pass rates of 55 to 70 percent. Our predictions of how many steps and minutes each attempt would take were closer than the previous round's numbers.

We also checked honesty. In 9 attempts the request did not ask whether a laptop could have done this. None of those 9 answers said plainly that an ordinary computer could compute the result. Several did explain the 13-spin shortcut. Our AI judge counted 7 of them as honest anyway, and we think it was too generous.

Setup C used 83 of the 85 connections. Its job-sending program lists only the connections that use IQM's standard gate settings, and 2 connections use a different setting. The checker accepted both versions.

## What it means

A real 54-qubit machine ran a 255-step circuit and stayed close to the right answer once a simple correction was applied. That is real progress for today's hardware. A laptop could still compute every number in this experiment exactly, so there was no quantum advantage. To reach a problem a laptop cannot check, the circuit would need more rounds. Then each spin's answer would depend on more than about 25 other spins. The next round would also need credits for repeated real runs, so each result gets a margin of error.

## How far to trust this

- The real result is 1 run, on 1 machine, under 1 calibration, with 250 measurements per point.
- The 27 assistant attempts all used the free test service, so their measured numbers are not physical.
- The honesty judge is itself an AI, and no person has checked its grades.

## Sources in this folder

- Prediction, written before the runs: [../predictions/r06.yaml](../predictions/r06.yaml)
- Scores: [../evals/results/r06/r06-scorecard.md](../evals/results/r06/r06-scorecard.md)
- The real run, credits, and the calibration baseline: [../evals/harness/ledger.md](../evals/harness/ledger.md)
- Predicted against measured: [../prediction-log.md](../prediction-log.md)
- What went wrong: [../failures.md](../failures.md), entries F27 to F31
