"""Build, submit, and record the round 5 oracle and negative jobs for T19 to T21, and the T21 noise-model baseline.

Usage: r05_oracles.py TASK [--real]     TASK is T19, T20, T21, or FAKE21. --real runs the T21 probe on real garnet.
Writes result objects to spe/evals/graders/selftest/r05/ and prints the job IDs.
That folder stays untracked until the round ends, so trial worktrees cannot see it (failures.md F14).
"""
import json
import math
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "spe" / "evals" / "graders"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade as g  # noqa: E402
from r04_oracles import backend, chain, measured, run, base_result, MOCK_NOTE  # noqa: E402

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import PauliEvolutionGate  # noqa: E402
from qiskit.quantum_info import SparsePauliOp, Statevector  # noqa: E402
from qiskit.synthesis import SuzukiTrotter  # noqa: E402
from iqm.qiskit_iqm import transpile_to_IQM  # noqa: E402

OUT = ROOT / "spe" / "evals" / "graders" / "selftest" / "r05"
OUT.mkdir(parents=True, exist_ok=True)


def save(name, task, expect, result):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps({"name": name, "task": task, "expect_pass": expect, "result": result}, indent=1))
    print("wrote", p)


def facts(jid):
    """circuit_facts read back from the submitted payload, as the contract asks agents to do."""
    f = g.job_facts(jid)
    return [{"label": f"c{i}", "cz_count": len(g.cz_edges(c)), "measured_qubits": s.get("measured", [])}
            for i, (c, s) in enumerate(zip(f["circuits"], f["sims"]))], f


def bits(counts, n):
    """Qiskit counts keyed so that index i is logical qubit i."""
    out = {}
    for k, v in counts.items():
        k = k.replace(" ", "")[::-1][:n]
        out[k] = out.get(k, 0) + v
    return out


# ---------- T19: KCuF3 Neel quench ----------

def heis(n, t, step=0.25):
    H = SparsePauliOp.from_sparse_list([(p + p, [i, i + 1], 0.25) for i in range(n - 1) for p in "XYZ"], n)
    qc = QuantumCircuit(n)
    for i in range(1, n, 2):
        qc.x(i)
    if t > 0:
        qc.append(PauliEvolutionGate(H, time=t, synthesis=SuzukiTrotter(order=2, reps=max(1, math.ceil(t / step)))), range(n))
    return qc


def order_of(p, n):
    return -sum(sum((1 - 2 * int(k[i])) * (1 - 2 * int(k[i + 1])) for i in range(n - 1)) / (n - 1) * v
                for k, v in p.items()) / sum(p.values())


def t19():
    bk = backend("garnet:mock")
    lay = chain(bk, 6)
    times = [0.0, 0.5, 1.0, 1.5, 2.0]
    for name, scale in (("r05 T19 oracle", 1.0), ("r05 T19 time doubled", 2.0)):
        logical = [heis(6, t * scale) for t in times]
        tq = [transpile_to_IQM(measured(c), bk, initial_layout=lay) for c in logical]
        jid, counts = run(bk, tq, 200)
        cf, _ = facts(jid)
        ideal = [order_of(bits(Statevector(c).probabilities_dict(), 6), 6) for c in logical]
        obs = [{"label": f"t={t}", "x": t, "ideal": i, "measured": order_of(bits(cn, 6), 6)} for t, i, cn in zip(times, ideal, counts)]
        r = base_result([jid], "garnet:mock", 200)
        r["observables"], r["circuit_facts"] = obs, cf
        r["answer"] = "Neel order melts from 1 as spin flips spread along the chain. " + MOCK_NOTE
        save(name, "T19", scale == 1.0, r)


# ---------- T20: La2CuO4 Hubbard dimer ----------

def dimer(dbl):
    """Qubits (1 up, 1 down, 2 up, 2 down). P of each doubly occupied configuration is dbl."""
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.ry(2 * math.acos(math.sqrt(2 * dbl)), 1)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.x(2)
    qc.cx(1, 3)
    qc.x(3)
    return qc


def dbl_of(p):
    """Per-site double occupancy from every shot: site 1 is qubits 0 and 1, site 2 is qubits 2 and 3."""
    tot = sum(p.values())
    return (sum(v for k, v in p.items() if k[0] == k[1] == "1") + sum(v for k, v in p.items() if k[2] == k[3] == "1")) / 2 / tot


def t20():
    bk = backend("garnet:mock")
    Us = [0.0, 2.0, 4.0, 8.0]
    for name, labels in (("r05 T20 oracle", Us), ("r05 T20 U swapped", [8.0, 4.0, 2.0, 0.0])):
        circs = [dimer(g.hubbard_dimer_exact(U)[1]) for U in Us]
        tq = [transpile_to_IQM(measured(c), bk) for c in circs]
        jid, counts = run(bk, tq, 500)
        cf, _ = facts(jid)
        obs = [{"label": f"U={u}", "x": u, "ideal": g.hubbard_dimer_exact(U)[1], "measured": dbl_of(bits(cn, 4))}
               for u, U, cn in zip(labels, Us, counts)]
        r = base_result([jid], "garnet:mock", 500)
        r["observables"], r["circuit_facts"] = obs, cf
        r["values"] = {f"energy_U{int(u)}": g.hubbard_dimer_exact(u)[0] for u in Us}
        r["answer"] = "Repulsion U pushes double occupancy from 0.25 toward 0, the start of a Mott insulator. " + MOCK_NOTE
        save(name, "T20", name.endswith("oracle"), r)


# ---------- T21: polyacetylene SSH edge state ----------

def ssh(first, second, n=8, t=2.0, steps=3):
    qc = QuantumCircuit(n)
    qc.x(0)
    dt = t / steps
    for _ in range(steps):
        for par in (0, 1):
            for i in range(par, n - 1, 2):
                b = first if i % 2 == 0 else second
                qc.append(PauliEvolutionGate(SparsePauliOp(["XX", "YY"], [b / 2, b / 2]), time=dt), [i, i + 1])
    return qc


PHASES = (("topological", 1.0, g.SSH_WEAK, g.SSH_STRONG), ("trivial", 0.0, g.SSH_STRONG, g.SSH_WEAK))


def ssh_stats(c8):
    raw = sum(v for k, v in c8.items() if k[0] == "1") / sum(c8.values())
    one = {k: v for k, v in c8.items() if k.count("1") == 1}
    post = sum(v for k, v in one.items() if k[0] == "1") / sum(one.values()) if one else None
    return raw, post, sum(one.values()) / sum(c8.values())


def ssh_circuits(bk, lay):
    return [transpile_to_IQM(measured(ssh(a, b)), bk, initial_layout=lay) for _, _, a, b in PHASES]


def t21(real):
    mock = backend("garnet:mock")
    lay = chain(mock, 8)
    edge = mock.index_to_qubit_name(lay[0])
    mjid, _ = run(mock, ssh_circuits(mock, lay), 1000)
    if not real:
        print("mock only, edge qubit", edge, ". Pass --real to spend credits on the probe.")
        return
    bk = backend("garnet")
    jid, counts = run(bk, ssh_circuits(bk, lay), 1000)
    cf, f = facts(jid)
    billed = f.get("billed_seconds")
    print("billed_seconds", billed, "estimated credits", f.get("estimated_credits"), "calibration", f.get("calibration_set_id"))
    r = base_result([mjid, jid], "garnet", 1000)
    r["billed_seconds_reported"], r["circuit_facts"] = billed, cf
    obs = []
    for (tag, x, a, b), cn in zip(PHASES, counts):
        raw, post, share = ssh_stats(bits(cn, 8))
        ideal = sum(v for k, v in bits(Statevector(ssh(a, b)).probabilities_dict(), 8).items() if k[0] == "1")
        obs.append({"label": tag, "x": x, "qubit": edge, "ideal": ideal, "measured": raw})
        r["values"][f"edge_postselected_{tag}"] = post
        r["values"][f"one_excitation_share_{tag}"] = share
        print(tag, {"ideal": round(ideal, 4), "raw": round(raw, 4), "postselected": round(post, 4), "one_excitation_share": round(share, 4)})
    r["observables"] = obs
    r["answer"] = "On real Garnet the electron stays at the edge far more often when the chain ends on a weak bond."
    save("r05 T21 oracle (real probe)", "T21", True, r)
    save("r05 T21 no mock test first", "T21", False, dict(r, job_ids=[jid]))
    swapped = json.loads(json.dumps(r))
    for o in swapped["observables"]:
        o["x"] = 1.0 - o["x"]
    save("r05 T21 phases swapped", "T21", False, swapped)


def fake21():
    """IQM's noise model baseline: IQMFakeGarnet on the T21 oracle circuits, 4000 shots, fixed seed."""
    from iqm.qiskit_iqm.fake_backends.fake_garnet import IQMFakeGarnet
    fake = IQMFakeGarnet()
    lay = chain(fake, 8)
    out = {}
    for tag, _, a, b in PHASES:
        # Same transpiler as the real probe, so the noise model sees the same 42-CZ circuit.
        fc = transpile_to_IQM(measured(ssh(a, b)), fake, initial_layout=lay)
        cn = fake.run(fc, shots=4000, seed_simulator=5).result().get_counts()
        raw, post, share = ssh_stats(bits(cn, 8))
        out[tag] = {"raw_edge": round(raw, 4), "postselected_edge": round(post, 4), "one_excitation_share": round(share, 4),
                    "cz": fc.count_ops().get("cz", 0)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    task = sys.argv[1]
    {"T19": t19, "T20": t20, "FAKE21": fake21}.get(task, lambda: t21("--real" in sys.argv))()
