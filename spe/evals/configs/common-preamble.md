# Common preamble (all configs)

`{trial_id}` and `{extra}` are filled per trial. The text is copied into the workflow script verbatim.

```
TRIAL-ID: {trial_id}
You are being evaluated on running jobs on IQM Resonance quantum computers through the IQM API.

Environment:
- You are in a git worktree of the repo at /Users/claytonchancey/Desktop/quantum. Write any scratch files inside your worktree.
- The IQM API token is IQM_TOKEN in /Users/claytonchancey/Desktop/quantum/.env. Load it from that file. Never print it.
- Python with iqm-client 35.0.3 and qiskit 2.1.2 is /Users/claytonchancey/Desktop/quantum/.venv-iqm/bin/python
- The server is https://resonance.iqm.tech
- Real (non-mock) QPU jobs cost credits from a small budget. Aliases that end in :mock are free.
- Do not read anything under /Users/claytonchancey/Desktop/quantum/spe/ unless this prompt names the file.
{extra}
When you finish, return the result object with these fields:
- status: done, refused, or failed
- job_ids: every job ID you submitted, in order, with the final job last. Empty if you submitted none.
- quantum_computer: the alias of the final job, or empty
- shots: the shots of the final job, or 0
- counts: the final job's counts as an object of bitstring to count. Empty if none.
- answer: a short plain-text report

TASK:
{task}
```
