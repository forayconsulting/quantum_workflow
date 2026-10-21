"""Build, submit, and record the round 4 oracle and negative jobs for T14 to T18.

Usage: r04_oracles.py TASK [--real]     TASK is T14, T15, T16, T17, or T18. --real runs the T17 probe on real sirius.
Writes result objects to spe/evals/graders/selftest/r04/ and prints the job IDs.
This file stays untracked until the round ends, so trial worktrees cannot see it (failures.md F14).
"""
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "spe" / "evals" / "graders"))
import grade as g  # noqa: E402

from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit.library import PauliEvolutionGate  # noqa: E402
from qiskit.quantum_info import SparsePauliOp, Statevector  # noqa: E402
from qiskit.synthesis import SuzukiTrotter  # noqa: E402
from iqm.qiskit_iqm import IQMProvider, transpile_to_IQM  # noqa: E402

BASE = "https://resonance.iqm.tech"
OUT = ROOT / "spe" / "evals" / "graders" / "selftest" / "r04"
OUT.mkdir(parents=True, exist_ok=True)
MOCK_NOTE = "The mock returns made-up counts, so the measured values are not physical results."


def backend(qc):
    return IQMProvider(BASE, quantum_computer=qc).get_backend()


def chain(bk, n):
    """A simple path of n physical qubits in the backend's coupling map."""
    adj = {}
    for a, b in bk.coupling_map.get_edges():
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    def dfs(path):
        if len(path) == n:
            return path
        for q in sorted(adj.get(path[-1], ())):
            if q not in path:
                r = dfs(path + [q])
                if r:
                    return r
        return None

    for s in sorted(adj):
        r = dfs([s])
        if r:
            return r
    raise SystemExit("no chain")


def tfim(n, t, step=0.25):
    H = SparsePauliOp.from_sparse_list([("ZZ", [i, i + 1], 1.0) for i in range(n - 1)] + [("X", [i], 1.0) for i in range(n)], n)
    qc = QuantumCircuit(n)
    if t > 0:
        qc.append(PauliEvolutionGate(H, time=t, synthesis=SuzukiTrotter(order=2, reps=max(1, math.ceil(t / step)))), range(n))
    return qc


def mean_z_sv(qc):
    p = Statevector(qc).probabilities_dict()
    return g.mean_z({k: v for k, v in p.items()})


def measured(qc):
    m = qc.copy()
    m.measure_all()
    return m


def run(bk, circs, shots):
    job = bk.run(circs, shots=shots)
    jid = job.job_id()
    print("job", jid, flush=True)
    res = job.result()
    return jid, [res.get_counts(i) for i in range(len(circs))]


def save(name, task, expect, result):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps({"name": name, "task": task, "expect_pass": expect, "result": result}, indent=1))
    print("wrote", p)


def base_result(jids, qc, shots):
    return {"status": "done", "job_ids": jids, "quantum_computer": qc, "shots": shots, "counts": {}, "counts_list": [],
            "billed_seconds_reported": 0, "observables": [], "values": {}}


def t14():
    bk = backend("garnet:mock")
    lay = chain(bk, 6)
    for name, scale in (("r04 T14 oracle", 1.0), ("r04 T14 wrong time units", 2.0)):
        times = [0.0, 0.5, 1.0, 1.5, 2.0]
        logical = [tfim(6, t * scale) for t in times]
        tq = [transpile_to_IQM(measured(c), bk, initial_layout=lay) for c in logical]
        jid, counts = run(bk, tq, 200)
        obs = [{"label": f"t={t}", "x": t, "ideal": mean_z_sv(c), "measured": g.mean_z(cn)} for t, c, cn in zip(times, logical, counts)]
        r = base_result([jid], "garnet:mock", 200)
        r["observables"] = obs
        r["answer"] = "Magnetization falls from 1 toward 0 as the spins dephase. " + MOCK_NOTE
        save(name, "T14", scale == 1.0, r)


H2 = SparsePauliOp.from_list([(k, v) for k, v in g.H2_TERMS.items()])


def h2_state(theta):
    qc = QuantumCircuit(2)
    qc.ry(theta, 0)
    qc.x(1)
    qc.cx(0, 1)
    return qc


def t15():
    from scipy.optimize import minimize_scalar
    e = lambda th: float(Statevector(h2_state(th)).expectation_value(H2).real) + g.H2_NUCLEAR  # noqa: E731
    best = minimize_scalar(e, bounds=(-math.pi, math.pi), method="bounded").x
    bk = backend("garnet:mock")
    for name, th, ok in (("r04 T15 oracle", best, True), ("r04 T15 wrong determinant", 0.0, False)):
        zc = measured(h2_state(th))
        xc = h2_state(th)
        xc.h([0, 1])
        xc = measured(xc)
        tq = [transpile_to_IQM(c, bk) for c in (zc, xc)]
        jid, counts = run(bk, tq, 500)
        r = base_result([jid], "garnet:mock", 500)
        r["values"] = {"energy_ideal": e(th), "energy_exact": g.h2_exact(), "energy_measured": 0.0}
        r["answer"] = "The variational energy matches the exact value within chemical accuracy. " + MOCK_NOTE
        save(name, "T15", ok, r)


def dqa_cz(qc):
    d = requests.get(f"{BASE}/api/v1/calibration-sets/{qc}/default/dynamic-quantum-architecture",
                     headers={"Authorization": f"Bearer {__import__('os').environ['IQM_TOKEN']}"}, timeout=60).json()
    gi = d["gates"]["cz"]
    return [tuple(x) for x in gi["implementations"][gi["default_implementation"]]["loci"]]


def submit_native(qc, circuits, shots):
    import os
    r = requests.post(f"{BASE}/api/v1/jobs/{qc}/circuit?use_timeslot=false",
                      headers={"Authorization": f"Bearer {os.environ['IQM_TOKEN']}", "Content-Type": "application/json"},
                      json={"circuits": circuits, "shots": shots}, timeout=120)
    r.raise_for_status()
    jid = r.json()["id"]
    print("job", jid, flush=True)
    return jid


def wait_counts(jid):
    import os, time
    h = {"Authorization": f"Bearer {os.environ['IQM_TOKEN']}"}
    for _ in range(300):
        s = requests.get(f"{BASE}/api/v1/jobs/{jid}", headers=h, timeout=60).json()["status"]
        if s in ("completed", "failed", "cancelled"):
            break
        time.sleep(2)
    return requests.get(f"{BASE}/api/v1/jobs/{jid}/artifacts/measurement_counts", headers=h, timeout=60).json()


def rcs_circuit(qubits, edges, layers, seed):
    rng = random.Random(seed)
    ins = []
    phases = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]
    for layer in range(layers):
        for q in qubits:
            ins.append({"name": "prx", "locus": [q], "args": {"angle": math.pi / 2, "phase": rng.choice(phases)}})
        used, pairs = set(), []
        es = edges[:]
        rng.shuffle(es)
        for a, b in es:
            if a not in used and b not in used:
                pairs.append((a, b))
                used |= {a, b}
        for a, b in pairs:
            ins.append({"name": "cz", "locus": [a, b], "args": {}})
    for q in qubits:
        ins.append({"name": "prx", "locus": [q], "args": {"angle": math.pi / 2, "phase": rng.choice(phases)}})
    ins.append({"name": "measure", "locus": qubits, "args": {"key": "m"}})
    return {"name": "rcs", "instructions": ins}


def t16():
    loci = dqa_cz("garnet")
    adj = {}
    for a, b in loci:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    start = sorted(adj)[0]
    qubits, todo = [], [start]
    while todo and len(qubits) < 8:
        q = todo.pop(0)
        if q not in qubits:
            qubits.append(q)
            todo += sorted(adj[q] - set(qubits))
    edges = [e for e in loci if e[0] in qubits and e[1] in qubits]
    for name, layers, ok in (("r04 T16 oracle", 10, True), ("r04 T16 too shallow", 3, False)):
        circ = rcs_circuit(qubits, edges, layers, seed=4)
        jid = submit_native("garnet:mock", [circ], 1000)
        c = wait_counts(jid)
        m, d = g.simulate(json.loads(json.dumps(circ)))
        order = g.api_bit_order(circ, c[0]["measurement_keys"])
        f, _ = g.xeb(g.reorder(d, m, order), c[0]["counts"], 8)
        r = base_result([jid], "garnet:mock", 1000)
        r["values"] = {"xeb_measured": f, "xeb_ideal": 2 ** 8 * sum(p * p for p in d.values()) - 1}
        r["answer"] = "An ideal device gives XEB near 1. " + MOCK_NOTE
        save(name, "T16", ok, r)


def ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return measured(qc)


def t17(real):
    mock = backend("sirius:mock")
    tq = [transpile_to_IQM(ghz(n), mock) for n in (2, 3, 4, 5)]
    mjid, _ = run(mock, tq, 100)
    if not real:
        print("mock only. Pass --real to spend credits on the probe.")
        return
    bk = backend("sirius")
    tq = [transpile_to_IQM(ghz(n), bk) for n in (2, 3, 4, 5)]
    jid, counts = run(bk, tq, 100)
    import os
    j = requests.get(f"{BASE}/api/v1/jobs/{jid}", headers={"Authorization": f"Bearer {os.environ['IQM_TOKEN']}"}, timeout=60).json()
    billed = (j.get("metrics") or {}).get("billed_seconds")
    print("billed_seconds", billed)
    obs = [{"label": f"GHZ-{n}", "x": n, "ideal": 1.0, "measured": g.parity(c)} for n, c in zip((2, 3, 4, 5), counts)]
    r = base_result([mjid, jid], "sirius", 100)
    r["observables"], r["billed_seconds_reported"] = obs, billed
    r["answer"] = "Agreement falls as the GHZ state grows, because each added qubit adds noise."
    save("r04 T17 oracle (real probe)", "T17", True, r)
    bad = dict(r, job_ids=[jid])
    save("r04 T17 no mock test first", "T17", False, bad)


def fold(tq, k):
    out = tq.copy_empty_like()
    for ins in tq.data:
        out.append(ins)
        if ins.operation.name == "cz":
            for _ in range(k - 1):
                out.append(ins)
    return out


def t18():
    from iqm.qiskit_iqm.fake_backends.fake_garnet import IQMFakeGarnet
    bk = backend("garnet:mock")
    fake = IQMFakeGarnet()
    lay = chain(bk, 6)
    logical = tfim(6, 1.0)
    base = transpile_to_IQM(measured(logical), bk, initial_layout=lay)
    for name, ks, ok in (("r04 T18 oracle", (1, 3, 5), True), ("r04 T18 no folding", (1, 1, 1), False)):
        circs = [fold(base, k) for k in ks]
        jid, _ = run(bk, circs, 200)
        raw = []
        for c in circs:
            fc = transpile(c, fake, optimization_level=0)
            raw.append(g.mean_z(fake.run(fc, shots=4000).result().get_counts()))
        r = base_result([jid], "garnet:mock", 200)
        fits = g.zne_fits(*raw)
        r["values"] = {"zne_raw_1": raw[0], "zne_raw_3": raw[1], "zne_raw_5": raw[2], "zne_mitigated": fits["richardson"],
                       "zne_ideal": mean_z_sv(logical)}
        r["answer"] = "Zero-noise extrapolation moves the noisy value toward the ideal one. " + MOCK_NOTE
        print(name, r["values"])
        save(name, "T18", ok, r)


if __name__ == "__main__":
    task = sys.argv[1]
    {"T14": t14, "T15": t15, "T16": t16, "T18": t18}.get(task, lambda: t17("--real" in sys.argv))()
