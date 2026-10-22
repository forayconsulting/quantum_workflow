"""Build, submit, and record the round 6 oracle and negative jobs for T22 and T23, the calibration-product baseline,
and the real Emerald probe.

Usage: r06_oracles.py T22 | T23 [--real] | BASELINE
  T22        oracle and negatives on emerald:mock
  T23        mock job of the oracle circuits. With --real, the same circuits once on real emerald (the probe)
  BASELINE   calibration-product prediction per theta from Emerald's default calibration
Writes result objects to spe/evals/graders/selftest/r06/, which stays untracked until the round ends (failures.md F14).
"""
import json
import math
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "spe" / "evals" / "graders"))
import grade as g  # noqa: E402

OUT = ROOT / "spe" / "evals" / "graders" / "selftest" / "r06"
OUT.mkdir(parents=True, exist_ok=True)
MOCK_NOTE = "The mock returns made-up counts, so the measured values are not physical results."


def arch():
    """Real Emerald qubits and CZ loci in the orientation the architecture lists them."""
    from iqm.iqm_client import IQMClient
    a = IQMClient("https://resonance.iqm.tech", quantum_computer="emerald").get_dynamic_quantum_architecture()
    loci = sorted({tuple(l) for v in a.gates["cz"].implementations.values() for l in v.loci})
    return sorted(a.qubits, key=lambda q: int(q[2:])), loci, str(a.calibration_set_id)


def layers(loci):
    """Greedy edge colouring, so CZs that share no qubit sit in the same layer."""
    out = []
    for e in loci:
        for lay in out:
            if not any(set(e) & set(f) for f in lay):
                lay.append(e)
                break
        else:
            out.append([e])
    return out


def kicked_ising(qubits, loci, theta, steps=g.KI_STEPS, drop=None):
    """Native circuit: per step PRX(theta) on every qubit, then CZ on every coupler. Each RZZ(-pi/2) is a CZ followed by
    S-dagger on both qubits. The S-daggers are virtual: each qubit's frame angle phi moves by -pi/2 per coupler, and later
    PRX phases absorb it (PRX(theta, 0) after RZ(phi) equals RZ(phi) after PRX(theta, -phi)). Z measurement ignores the rest."""
    phi = {q: 0.0 for q in qubits}
    ins = []
    for step in range(steps):
        ins += [{"name": "prx", "locus": [q], "args": {"angle": theta, "phase": (-phi[q]) % (2 * math.pi)}} for q in qubits]
        for k, lay in enumerate(layers(loci)):
            if drop == (step, k):
                continue
            for a, b in lay:
                ins.append({"name": "cz", "locus": [a, b], "args": {}})
                phi[a] -= math.pi / 2
                phi[b] -= math.pi / 2
    ins.append({"name": "measure", "locus": list(qubits), "args": {"key": "m"}})
    return {"name": f"kicked_ising_theta_{theta:.4f}", "instructions": ins}


def submit(qc, circuits, shots):
    hdr = {"Authorization": f"Bearer {g.os.environ['IQM_TOKEN']}", "Content-Type": "application/json"}
    r = requests.post(f"{g.API}/jobs/{qc}/circuit?use_timeslot=false", headers=hdr,
                      json={"circuits": circuits, "shots": shots}, timeout=120)
    if r.status_code >= 300:
        raise SystemExit(f"submit failed: HTTP {r.status_code}: {r.text[:500]}")
    jid = r.json()["id"]
    print("job", jid, qc, flush=True)
    for _ in range(1800):
        st = g.get(f"jobs/{jid}")["status"]
        if st in ("completed", "failed", "cancelled", "aborted"):
            break
        time.sleep(2)
    print("status", st, flush=True)
    return jid


def save(name, task, expect, result):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps({"name": name, "task": task, "expect_pass": expect, "result": result}, indent=1))
    print("wrote", p)


def result_for(jids, qc, labels):
    """A result object built the way the contract asks: payload read back, ideal from light cones, measured from counts."""
    f = g.job_facts(jids[-1])
    obs, cf = [], []
    for i, (c, x) in enumerate(zip(f["circuits"], labels)):
        ops, m = g.native_ops(c)
        ideal = g.cone_mean_z(ops, m)[0]
        meas = g.mean_z(g.norm_counts(f["counts_list"][i]))
        obs.append({"label": f"theta={x}pi", "x": x, "ideal": ideal, "measured": meas})
        cf.append({"label": f"theta={x}pi", "cz_count": len(g.cz_edges(c)), "measured_qubits": m})
    raw = {o["x"]: o["measured"] for o in obs}
    resc = g.rescaled(raw)
    vals = {"rescaled_" + str(x).replace(".", ""): resc[x] for x in (0.2, 0.35, 0.5)}
    return {"status": "done", "job_ids": jids, "quantum_computer": qc, "shots": g.KI_SHOTS, "counts": {},
            "counts_list": [], "billed_seconds_reported": f.get("billed_seconds") or 0, "observables": obs,
            "values": vals, "circuit_facts": cf}, f


def oracle_circuits(qubits, loci, scale=1.0, drop=None):
    return [kicked_ising(qubits, loci, math.pi * x * scale, drop=drop) for x in g.KI_THETAS]


def t22():
    qubits, loci, cal = arch()
    print("calibration", cal, "couplers", len(loci), "layers", len(layers(loci)))
    for name, kw in (("r06 T22 oracle", {}), ("r06 T22 theta doubled", {"scale": 2.0}),
                     ("r06 T22 missing CZ layer", {"drop": (1, 0)})):
        jid = submit("emerald:mock", oracle_circuits(qubits, loci, **kw), g.KI_SHOTS)
        r, _ = result_for([jid], "emerald:mock", g.KI_THETAS)
        r["answer"] = "The magnetization falls as the field angle grows, from 1 at zero field to 0 at the Clifford point. " + MOCK_NOTE
        save(name, "T22", name.endswith("oracle"), r)
    empty = {"status": "failed", "job_ids": [], "quantum_computer": "", "shots": 0, "counts": {}, "answer": ""}
    save("r06 T22 empty", "T22", False, empty)


def t23(real):
    qubits, loci, cal = arch()
    circs = oracle_circuits(qubits, loci)
    mjid = submit("emerald:mock", circs, g.KI_SHOTS)
    if not real:
        print("mock only. Pass --real to spend credits on the probe.")
        return
    jid = submit("emerald", circs, g.KI_SHOTS)
    r, f = result_for([mjid, jid], "emerald", g.KI_THETAS)
    print("billed_seconds", f.get("billed_seconds"), "estimated credits", f.get("estimated_credits"),
          "calibration", f.get("calibration_set_id"), "default calibration at build", cal)
    for o in r["observables"]:
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items()}))
    print("rescaled", {k: round(v, 4) for k, v in r["values"].items()})
    r["answer"] = ("On real Emerald the magnetization kept its shape. A laptop computed the exact values with light cones, "
                   "so this is not a quantum advantage.")
    save("r06 T23 oracle (real probe)", "T23", True, r)
    save("r06 T23 no mock test first", "T23", False, dict(r, job_ids=[jid]))
    bad = json.loads(json.dumps(r))
    bad["values"] = {k: v * 0.8 for k, v in bad["values"].items()}
    save("r06 T23 rescaled wrong", "T23", False, bad)


def baseline():
    """Per qubit: exact <Z> times the product of IRB CZ fidelities in its light cone times (1 - 2 x readout error).
    Readout error is the calibration's assignment_error."""
    qubits, loci, _ = arch()
    m = g.get("calibration-sets/emerald/default/metrics")
    cal = m.get("describes_id")
    fid, ro = {}, {}
    for o in m["observations"]:
        d = o["dut_field"]
        if o.get("invalid"):
            continue
        if d.startswith("metrics.irb.cz.") and ".fidelity" in d:
            a, b = d.split(".")[4].split("__")
            fid[tuple(sorted((a, b)))] = o["value"]
        if d.startswith("metrics.ssro.measure.constant.") and d.endswith(".assignment_error"):
            ro[d.split(".")[4]] = o["value"]
    out = {"calibration_set_id": cal, "rows": []}
    for x in g.KI_THETAS:
        ops = g.native_ops(kicked_ising(qubits, loci, math.pi * x))[0]
        vals = []
        for q in qubits:
            z, _ = g.cone_z(ops, q)
            _, kept = g.light_cone(ops, q)
            f = 1.0
            for kind, loc, _m in kept:
                if kind == "d2":
                    f *= fid.get(tuple(sorted(loc)), 0.995)
            vals.append(z * f * (1 - 2 * ro.get(q, 0.02)))
        exact = g.kicked_ising_exact(*g.emerald_graphs()[0], math.pi * x)[0]
        out["rows"].append({"theta_over_pi": x, "exact": round(exact, 4), "calibration_product": round(sum(vals) / len(vals), 4)})
    out["median_readout_error"] = sorted(ro.values())[len(ro) // 2]
    out["median_irb_cz_fidelity"] = sorted(fid.values())[len(fid) // 2]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    task = sys.argv[1]
    {"T22": t22, "BASELINE": baseline}.get(task, lambda: t23("--real" in sys.argv))()
