# quantum_workflow

This repo evaluates how well a Claude Code agent runs jobs on IQM Resonance quantum computers through the IQM API. The evaluation follows the SPE loop (Specify, Predict, Evaluate). Each round is a series of commits named after its SPE step, and each round ends with a tag (`spe-r01`, `spe-r02`, `spe-r03`).

Start at [spe/README.md](spe/README.md).

| Path | Purpose |
|---|---|
| `spe/` | Spec, predictions, eval harness, graders, results, prediction log, and failure types for each round |
| `scripts/` | Free connection checks for IBM Quantum, IQM Resonance, and D-Wave. None submit jobs |
| `.env.example` | The environment variables the scripts and graders read. Copy it to `.env` and fill in your own tokens |

The internal API docs and account setup runbooks that the agents could read during the rounds are kept locally and are not part of this repo.
