# quantum_workflow

This project asks two simple questions.

1. Can an AI assistant run real quantum experiments for someone who knows nothing about quantum computing?
2. When will a quantum computer first beat an ordinary computer at something useful?

## Start here

[Can an AI assistant run materials experiments on a quantum computer?](spe/knowledge/quantum-materials-explainer.md) is a plain-language write-up of the latest round. It needs no background in AI tools or quantum computing.

## Where this is going

In our view, the first real wins for quantum computers will come from simulating nature, such as new materials and molecules. That is where our recent tests focus.

Next, we plan to:

- Make the experiments bigger and harder
- Put each quantum result next to the best ordinary-computer answer, with the time and cost of each
- Repeat the same tests over time, so the record shows when quantum computers start to win, if they do

## Methodology

We use the SPE loop: Specify, Predict, Evaluate. Each pass through the loop is one round.

1. **Specify.** We write down what the round should test. Each requirement says where it came from, such as a user request or a failure from the last round.
2. **Predict.** Before anything runs, we commit a prediction with numbers, such as how often each agent setup will pass each task. From round 2 on, git shows that each prediction came before its run.
3. **Evaluate.** One workflow runs every trial. Several agent setups get the same tasks. Code graders check each result against the quantum computer's own records and a simulation of the submitted circuit. An LLM judge describes how well the agent worked and explained itself, but the code graders decide pass or fail.
4. **Learn.** We compare each prediction with what happened, and with the simple guess "same as last round." We log every new type of failure, including our own grader mistakes. Then we propose changes for the next round and tag the round in git.

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
