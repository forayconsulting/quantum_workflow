# quantum_workflow

Quantum computers are a new kind of computer. Today they are small, and they make a lot of errors. Someday they may solve a few kinds of problems that ordinary computers cannot.

This project asks two simple questions.

1. Can an AI assistant run real quantum experiments for someone who knows nothing about quantum computing?
2. When will a quantum computer first beat an ordinary computer at something useful?

## What we do

A person asks for an experiment in plain English. For example: "Show me how a tiny magnet behaves," or "Find the energy of a hydrogen molecule." An AI assistant (Claude) designs the experiment and runs it on real quantum computers in the cloud. The computers belong to a company called IQM. The assistant then explains the result in plain words.

We never take the assistant's word for it. A separate program checks every result.

Before each round of tests, we write down what we expect to happen. After the round, we compare our guesses with what really happened. This keeps us honest about what we know.

## What we have seen so far

We have run 4 rounds of tests.

- The assistant usually gets these experiments right. In the latest round, 2 of the 4 versions we tested got every task right.
- A smaller, faster version made more mistakes on the hardest task. Sometimes it described what it meant to do instead of what it actually did.
- Today's quantum computers are noisy. The more pieces we linked together, the more errors crept in.
- Everything we ran is small enough for a laptop to do the same math. Nothing here beats an ordinary computer yet.
- Our own guesses were usually too gloomy. The assistant did better than we expected.

## Where this is going

In our view, the first real wins for quantum computers will come from simulating nature, such as new materials and molecules. That is where our recent tests focus.

Next, we plan to:

- Make the experiments bigger and harder
- Put each quantum result next to the best ordinary-computer answer, with the time and cost of each
- Repeat the same tests over time, so the record shows when quantum computers start to win, if they do

## For technical readers

- [spe/README.md](spe/README.md) explains the test setup and each round
- [spe/prediction-log.md](spe/prediction-log.md) shows every guess next to the result
- [spe/failures.md](spe/failures.md) lists every mistake we found, including our own
- `git log --oneline --decorate` shows each round as a series of commits

To check your own connection to IQM:

```bash
cp .env.example .env        # add your own tokens
python3.12 -m venv .venv-iqm
.venv-iqm/bin/pip install "iqm-client[qiskit]==35.0.3" requests python-dotenv
.venv-iqm/bin/python scripts/check_iqm.py
```
