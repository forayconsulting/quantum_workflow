# Can an AI assistant run materials experiments on a quantum computer?

Written 2026-10-21, after round 5 of this project. This page is for a reader who has not used Claude Code and has not studied quantum computing. Every number on it comes from the results files named at the end.

## What we did

Claude Code is an AI assistant that works inside a computer's terminal. It can write and run programs on its own. We gave it plain-English requests, the kind a curious person without a physics degree might write. Each request asked for an experiment on a real material. The assistant had to design the experiment, write the program, send it to a quantum computer over the internet, and explain the result in plain words.

The quantum computers belong to IQM, a company in Finland. We used two of them. Garnet is a real machine with 20 qubits. Garnet's "mock" is a free test service. It accepts the same jobs and checks that they are valid, but it sends back made-up numbers instead of real measurements.

We asked each request many times, in 4 setups:

| Setup | What the assistant had |
|---|---|
| A | The larger Claude model (Opus) and the project folder |
| B | A, plus a pointer to our written notes on IQM's system |
| C | B, plus a small tested program that sends jobs for it |
| D | The same as C, but with the smaller Claude model (Sonnet) |

In round 5 we ran 44 attempts in 23 minutes and spent 3.00 of IQM's free monthly credits.

## How we checked the work

We did not trust the assistant's own report. A separate checking program read every job back from IQM's servers. It simulated the exact circuit the assistant had sent, on an ordinary computer, with no noise. It then compared that result with the exact answer from physics. The checker also confirmed that every number in the report matched IQM's records.

Before any experiment ran, we wrote down predictions, each with a margin of error. We saved them in the project history, so nobody could change them afterward. Then we compared the predictions with what happened.

A second AI read each answer and judged whether a non-expert could follow it. That judge describes the answers. It does not decide pass or fail.

## The three materials

### KCuF3, a chain of tiny magnets

KCuF3 (potassium copper fluoride) is a real crystal. Each copper atom acts as a tiny magnet, which physicists call a spin. The spins sit in long chains, and each one prefers to point opposite to its neighbors. We asked the assistant to start 6 spins in a perfect up, down, up, down pattern and watch what happens over time.

In a perfect quantum computer, the pattern fades. Neighboring spins swap with each other, and the state spreads into a mix of many patterns. A score of 1 means the perfect pattern. The exact physics gives 1.00 at the start, 0.50 at time 1, and 0.37 at time 2. Every setup built circuits that matched those values. This experiment ran only on the free test service, so it has no real measurement.

The toy model leaves a lot out. A real crystal has billions of spins per chain, weak links between chains, and heat. The real crystal settles into an ordered pattern only below about 39 kelvin, because of those links between chains.

### La2CuO4, why some materials refuse to conduct

La2CuO4 is the parent crystal of a family of copper-oxide superconductors. A simple theory of metals says it should conduct electricity. It does not. Its electrons push each other away so strongly that two of them almost never share one copper atom. Physicists call this a Mott insulator.

We asked for the smallest version of this: 2 sites and 2 electrons, with the push between electrons (called U) set to 0, 2, 4, and 8. The key number is how often both electrons sit on the same site. The exact values are 0.250, 0.138, 0.073, and 0.026. As the push grows, the electrons avoid each other more. Every setup found these values in every attempt. This experiment also ran only on the free test service.

Two sites is the smallest possible model. The real material is a flat sheet of copper and oxygen atoms with many electrons, so this experiment shows the effect but cannot simulate the crystal.

### Polyacetylene, a protected state at the end of a chain

Polyacetylene is a plastic. The discovery that it can conduct electricity won the 2000 Nobel Prize in Chemistry. Its chain of carbon atoms alternates strong and weak bonds. A model of this chain predicts something unusual. If the chain ends on a weak bond, an electron placed on the end site stays there. If the chain ends on a strong bond, the electron moves away. Physicists call the first case a topological edge state. The structure of the chain protects it.

This was the one experiment that ran on the real Garnet machine. We used 8 sites, with one qubit for each site.

## The real-hardware test

Before any run, Claude predicted that the edge state would stay clearly visible on real hardware. In numbers, the electron would be found on the end site at least 3 times as often when the chain ends on a weak bond. We also asked IQM's own computer model of Garnet's noise for its forecast. That gave us a second guess to compare against.

The real machine ran the experiment 5 times, once in our own test and once for each setup. Each run used a different set of 8 qubits on the chip.

| | Weak bond at the end | Strong bond at the end | How many times more often |
|---|---|---|---|
| Perfect machine | 0.76 | 0.14 | 5.2 |
| Claude's prediction | 0.60 | 0.15 | 3 or more |
| IQM's noise model | 0.72 | 0.21 | 3.5 |
| Real Garnet, average of 5 runs | 0.69 | 0.24 | 3.3 (middle run 3.6) |

The edge state survived. On average the electron stayed on the end site 3.3 times as often when the chain ended on a weak bond. That meets Claude's call of 3 or more. The result changed a lot with the choice of qubits. The 5 runs gave ratios from 1.8 to 4.5. Our own first test happened to use the worst set of qubits. IQM's noise model came closer than Claude on these probabilities. Claude came closer on a second measure: how many runs kept exactly one electron in the chain.

## How the assistant did

The larger model passed every attempt in all three of its setups, after we fixed one mistake in our checker. The smaller model passed 13 of 15. Both of its misses were small reporting slips: it listed the qubits by local numbers instead of the names on the chip. Its physics was right in both. Every report kept IQM's records straight, and every job the assistant sent showed up in its report.

The setups differed in effort more than in accuracy. With the helper program, the larger model needed a median of 12 steps per experiment. Without any help, it needed 15.

## Why it matters, and what it means

The assistant turned a short request about a real material into a correct quantum experiment, ran it, and explained it without the person ever touching code. That held for three different materials and four setups.

Every experiment here is small enough for a laptop to solve exactly. Our checker did just that for each one. So these runs show no advantage for the quantum computer. They show that the workflow works, and they show how much noise a real machine adds today.

Many physicists expect quantum computers to matter first for materials whose behavior no ordinary computer can calculate. Examples are flat sheets of interacting electrons like the copper-oxide layers in La2CuO4, and how such systems change over long times. Those problems need far more qubits and far less noise than these runs had.

## How far to trust this

- The real-hardware result rests on 5 runs on one machine, on one day, under one calibration.
- Each setup got only 1 real run, so the real runs cannot rank the setups.
- The judge of plain language is itself an AI, and no person has checked its grades.
- Our prompts asked the assistant what the result means for the real material. That question invited the honest limits we were hoping to see, so it does not show what the assistant would say unprompted.

## Sources in this folder

- Prediction, written before the runs: [../predictions/r05.yaml](../predictions/r05.yaml)
- Scores: [../evals/results/r05/r05-scorecard.md](../evals/results/r05/r05-scorecard.md)
- Real runs, credits, and the noise-model baseline: [../evals/harness/ledger.md](../evals/harness/ledger.md)
- Predicted against measured: [../prediction-log.md](../prediction-log.md)
- What went wrong: [../failures.md](../failures.md), entries F23 to F26
