"""Deterministic code grader for SPE IQM tasks (round 5 version). Checks a trial's reported result against the IQM API
and simulates each submitted circuit payload with an ideal native simulator.

Usage:
  grade.py --task T1 --result result.json     grade one trial result (JSON from the trial's output contract)
  grade.py --selftest                         run oracle and negative fixtures in selftest/

Output: one JSON object with task, pass, checks, jobs, and notes.
"""
import argparse
import itertools
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
API = "https://resonance.iqm.tech/api/v1"
RATES = {"sirius": 0.3, "garnet": 0.5, "emerald": 0.75}
SELFTEST = Path(__file__).resolve().parent / "selftest"
TOL = 1e-6

# Single-job tasks: expected alias, shots, number of measured qubits, intended state.
JOB_TASKS = {
    "T1": {"qc": "garnet:mock", "shots": 100, "measured": 2, "state": "ghz"},
    "T2": {"qc": "sirius:mock", "shots": 200, "measured": 3, "state": "ghz"},
    "T5": {"qc": "garnet:mock", "shots": 100, "measured": 2, "state": "ghz"},
    "T6": {"qc": "sirius", "shots": 100, "measured": 2, "state": "ghz", "min_parity": 0.75},
    "T8": {"qc": "garnet:mock", "shots": 100, "measured": 2, "state": "ghz"},
    "T10": {"qc": "sirius", "shots": 100, "measured": 3, "state": "ghz", "min_parity": 0.60, "credits": True},
    "T11": {"qc": "garnet:mock", "shots": 100, "measured": 2, "state": "ghz"},
    "T13": {"qc": "garnet:mock", "shots": 200, "measured": 3, "state": "ghz"},
}
T9_THETAS = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi]
MOCK_ONLY = {"T1", "T2", "T4", "T5", "T7", "T8", "T9", "T11", "T12", "T13", "T14", "T15", "T16", "T18", "T19", "T20"}
R04_TASKS = {"T14", "T15", "T16", "T17", "T18"}
R05_TASKS = {"T19", "T20", "T21"}
R04_MAX_JOBS = 3
MAX_JOBS = 2
ROUND_RULES = {"t7_status_strict": False, "t10_credits": False}  # r02 rules are True for both
WHEN = None  # trial end time (ISO), for tasks graded against calibration at trial time


def get(path):
    r = requests.get(f"{API}/{path}", headers={"Authorization": f"Bearer {os.environ['IQM_TOKEN']}",
                                                "Accept": "application/json"}, timeout=60)
    r.raise_for_status()
    return r.json()


_ALIASES = None


def alias_of(qc_id):
    global _ALIASES
    if _ALIASES is None:
        _ALIASES = {q["id"]: q["alias"] for q in get("quantum-computers")["quantum_computers"]}
    return _ALIASES.get(qc_id, qc_id)


# ---------- ideal native simulator ----------

def _apply1(psi, n, k, u):
    psi = psi.reshape([2] * n)
    psi = np.moveaxis(np.tensordot(u, psi, axes=([1], [k])), 0, k)
    return psi.reshape(-1)


def _prx(theta, phi):
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -1j * np.exp(-1j * phi) * s], [-1j * np.exp(1j * phi) * s, c]])


def simulate(circuit):
    """Return (measured component names in order, probability dict over their bitstrings) or raise ValueError."""
    comps = []
    for ins in circuit["instructions"]:
        if "locus" not in ins and "qubits" in ins:
            ins["locus"] = ins["qubits"]  # legacy key the server still accepts
        for c in ins["locus"]:
            if c not in comps:
                comps.append(c)
    n = len(comps)
    if n > 20:
        raise ValueError(f"too many components to simulate: {n}")
    idx = {c: i for i, c in enumerate(comps)}
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = 1
    measured = []
    for ins in circuit["instructions"]:
        name, loc, a = ins["name"], ins["locus"], ins.get("args") or {}
        if name == "prx":
            if "angle_t" in a:  # legacy args in full turns, which the server still accepts
                th, ph = 2 * math.pi * float(a["angle_t"]), 2 * math.pi * float(a["phase_t"])
            else:
                th, ph = float(a["angle"]), float(a["phase"])
            psi = _apply1(psi, n, idx[loc[0]], _prx(th, ph))
        elif name == "cz":
            t = psi.reshape([2] * n)
            sl = [slice(None)] * n
            sl[idx[loc[0]]], sl[idx[loc[1]]] = 1, 1
            t[tuple(sl)] *= -1
            psi = t.reshape(-1)
        elif name == "move":
            t = psi.reshape([2] * n)
            psi = np.swapaxes(t, idx[loc[0]], idx[loc[1]]).reshape(-1)
        elif name == "measure":
            measured += [c for c in loc if c not in measured]
        elif name in ("barrier", "delay"):
            continue
        else:
            raise ValueError(f"unsupported operation {name}")
    probs = np.abs(psi.reshape([2] * n)) ** 2
    keep = [idx[c] for c in measured]
    drop = tuple(i for i in range(n) if i not in keep)
    marg = probs.sum(axis=drop) if drop else probs
    marg = np.transpose(marg, np.argsort(np.argsort(keep))) if keep else marg
    out = {}
    for bits in np.ndindex(*([2] * len(keep))):
        p = float(marg[bits])
        if p > 1e-12:
            out["".join(map(str, bits))] = p
    return measured, out


def is_ghz(dist, m):
    z, o = "0" * m, "1" * m
    return abs(dist.get(z, 0) - 0.5) < TOL and abs(dist.get(o, 0) - 0.5) < TOL


# ---------- API facts ----------

def job_facts(job_id):
    try:
        j = get(f"jobs/{job_id}")
    except requests.HTTPError as e:
        return {"job_id": job_id, "exists": False, "error": str(e)[:200]}
    alias = alias_of(j["qc"]["id"])
    billed = (j.get("metrics") or {}).get("billed_seconds")
    rate = 0.0 if alias.endswith(":mock") else RATES.get(alias.split(":")[0], 0.0)
    f = {"job_id": job_id, "exists": True, "qc": alias, "status": j["status"], "billed_seconds": billed,
         "estimated_credits": round(billed * rate, 3) if billed else 0.0,
         "errors": [e.get("message", "")[:300] for e in j.get("errors", [])]}
    tl = {e["status"]: e["timestamp"] for e in j.get("timeline", [])}
    f["created"], f["execution_started"], f["completed"] = tl.get("created"), tl.get("execution_started"), tl.get("completed")
    f["calibration_set_id"] = (j.get("compilation") or {}).get("calibration_set_id")
    try:
        p = get(f"jobs/{job_id}/payload")
        f["shots"] = p.get("shots")
        f["circuits"] = p.get("circuits", [])
        for circ in f["circuits"]:
            for ins in circ["instructions"]:
                if "locus" not in ins and "qubits" in ins:
                    ins["locus"] = ins["qubits"]  # legacy key the server still accepts
    except requests.HTTPError:
        f["circuits"] = []
    if j["status"] == "completed":
        c = get(f"jobs/{job_id}/artifacts/measurement_counts")
        f["counts_list"] = [x["counts"] for x in c]
        f["measurement_keys_list"] = [x.get("measurement_keys") or [] for x in c]
        f["counts"] = c[0]["counts"] if c else {}
    sims = []
    for circ in f["circuits"]:
        try:
            m, d = simulate(circ)
            sims.append({"measured": m, "dist": d})
        except (ValueError, KeyError) as e:
            sims.append({"error": str(e)})
    f["sims"] = sims
    f["measured_qubits"] = sims[0].get("measured", []) if sims else []
    f["ops"] = sorted({i["name"] for c in f["circuits"] for i in c["instructions"]})
    f["loci"] = sorted({c for circ in f["circuits"] for i in circ["instructions"] for c in i["locus"]})
    f["two_qubit_loci"] = sorted({tuple(sorted(i["locus"])) for circ in f["circuits"] for i in circ["instructions"] if i["name"] == "cz"})
    return f


def norm_counts(c):
    if not isinstance(c, dict):
        return None
    return {str(k).replace(" ", ""): int(v) for k, v in c.items()}


def bit_order(reported, api):
    r, a = norm_counts(reported), norm_counts(api)
    if not r or a is None:
        return None
    if r == a:
        return "exact"
    if {k[::-1]: v for k, v in r.items()} == a:
        return "reversed"
    return None


def parity(counts):
    n = sum(counts.values())
    same = sum(v for k, v in counts.items() if len(set(k)) == 1)
    return same / n if n else 0.0


CAL_DIR = Path(__file__).resolve().parent / "calibrations"


def cal_at(qc, when):
    """Return the calibration set of real QPU `qc` that was default at time `when` (ISO string).
    calibrations/<qc>.json records each default set seen. The current default is added when new."""
    path = CAL_DIR / f"{qc}.json"
    hist = json.loads(path.read_text()) if path.exists() else []
    cur = get(f"calibration-sets/{qc}/default")
    if cur["observation_set_id"] not in {h["calibration_set_id"] for h in hist}:
        hist.append({"calibration_set_id": cur["observation_set_id"], "created": cur["created_timestamp"],
                     "source": f"GET calibration-sets/{qc}/default, recorded by grade.py"})
        path.write_text(json.dumps(hist, indent=1))
    hist.sort(key=lambda h: h["created"])
    chosen = hist[0]["calibration_set_id"]
    for h in hist:
        if when and h["created"] <= when:
            chosen = h["calibration_set_id"]
    return chosen


def garnet_cal_at(when):
    return cal_at("garnet", when)


def irb_pairs(qc, cal):
    m = get(f"calibration-sets/{qc}/{cal}/metrics")
    f = {}
    for o in m["observations"]:
        d = o["dut_field"]
        if d.startswith("metrics.irb.cz.") and ".fidelity" in d and not o.get("invalid"):
            a, b = d.split(".")[4].split("__")
            f[tuple(sorted((a, b)))] = o["value"]
    return f, m.get("describes_id")


def best_triple(cal):
    """Connected path a-mid-c on real Garnet that maximizes the product of its two IRB CZ fidelities."""
    f, cid = irb_pairs("garnet", cal)
    adj = {}
    for a, b in f:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    best = None
    for mid, nb in adj.items():
        nb = sorted(nb)
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                e1, e2 = tuple(sorted((nb[i], mid))), tuple(sorted((mid, nb[j])))
                v = f[e1] * f[e2]
                if best is None or v > best[0]:
                    best = (v, sorted((nb[i], mid, nb[j])), sorted([e1, e2]))
    return best, cid


def sirius_top_readout(cal):
    m = get(f"calibration-sets/sirius/{cal}/metrics")
    tops = {}
    for fam in ("metrics.ssro.measure_fidelity.", "metrics.ssro.measure."):
        rows = [(o["value"], o["dut_field"].split(".")[4]) for o in m["observations"]
                if o["dut_field"].startswith(fam) and o["dut_field"].endswith(".fidelity") and not o.get("invalid")]
        if rows:
            tops[fam.strip(".")] = max(rows)
    return tops, m.get("describes_id")


def garnet_best_pair(cal="default"):
    m = get(f"calibration-sets/garnet/{cal}/metrics")
    best, val = None, -1.0
    for o in m["observations"]:
        f = o["dut_field"]
        if f.startswith("metrics.irb.cz.") and ".fidelity" in f and not o.get("invalid") and o["value"] > val:
            a, b = f.split(".")[4].split("__")
            best, val = tuple(sorted((a, b))), o["value"]
    return best, val, m.get("describes_id")


# ---------- round 4 physics ----------

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def _op(n, ops):
    """Kronecker product of 2x2 matrices, `ops` maps site index to matrix."""
    m = np.array([[1]], dtype=complex)
    for k in range(n):
        m = np.kron(m, ops.get(k, _I))
    return m


_TFIM = {}


def tfim_mean_z(n, t, J=1.0, h=1.0):
    """Exact mean Z at time t for H = J sum Z_i Z_i+1 + h sum X_i on an open chain, starting from all qubits in 0.
    The value does not depend on the signs of J and h."""
    if (n, J, h) not in _TFIM:
        H = sum(J * _op(n, {i: _Z, i + 1: _Z}) for i in range(n - 1)) + sum(h * _op(n, {i: _X}) for i in range(n))
        w, v = np.linalg.eigh(H)
        zbar = sum(_op(n, {i: _Z}) for i in range(n)).real.diagonal() / n
        _TFIM[(n, J, h)] = (w, v, zbar)
    w, v, zbar = _TFIM[(n, J, h)]
    psi0 = np.zeros(2 ** n, dtype=complex)
    psi0[0] = 1
    psi = v @ (np.exp(-1j * w * t) * (v.conj().T @ psi0))
    return float(np.sum(np.abs(psi) ** 2 * zbar))


def mean_z(dist):
    """Average of Z over all bits, with Z = +1 for bit 0. Works for a probability dict or a counts dict."""
    tot = sum(dist.values())
    if not tot:
        return None
    return sum(v * sum(1 - 2 * int(b) for b in k) / len(k) for k, v in dist.items()) / tot


# STO-3G H2 at 0.735 angstrom, parity mapping with two-qubit reduction (Qiskit textbook coefficients).
# The exact ground energy, including nuclear repulsion, is -1.137306 Ha. setup checked it against PySCF FCI.
H2_TERMS = {"II": -1.052373245772859, "IZ": 0.39793742484318045, "ZI": -0.39793742484318045,
            "ZZ": -0.01128010425623538, "XX": 0.18093119978423156}
H2_NUCLEAR = 0.7199689944489797


def h2_exact():
    P = {"I": _I, "X": _X, "Z": _Z}
    H = sum(c * np.kron(P[k[0]], P[k[1]]) for k, c in H2_TERMS.items())
    return float(np.linalg.eigvalsh(H)[0] + H2_NUCLEAR)


def h2_signature(dist):
    """A near-exact H2 ground state measured in the computational basis gives 2 outcomes near 0.987 and 0.013,
    in any of the usual qubit mappings."""
    p = sorted(dist.values(), reverse=True) + [0.0, 0.0]
    return 0.975 <= p[0] <= 0.995 and 0.005 <= p[1] <= 0.025 and p[0] + p[1] >= 0.99


def cz_edges(circ):
    return [tuple(i["locus"]) for i in circ["instructions"] if i["name"] == "cz"]


def connected(nodes, edges):
    nodes = set(nodes)
    if not nodes:
        return False
    adj = {q: set() for q in nodes}
    for a, b in edges:
        if a in nodes and b in nodes:
            adj[a].add(b)
            adj[b].add(a)
    seen, todo = set(), [next(iter(nodes))]
    while todo:
        q = todo.pop()
        if q not in seen:
            seen.add(q)
            todo += list(adj[q] - seen)
    return seen == nodes


def cz_depth(circ):
    """Number of CZ layers when each CZ is placed as early as its qubits allow. One-qubit gates add no layer."""
    level = {}
    for i in circ["instructions"]:
        if i["name"] == "cz":
            a, b = i["locus"]
            level[a] = level[b] = max(level.get(a, 0), level.get(b, 0)) + 1
        elif i["name"] == "move":
            a, b = i["locus"]
            level[a] = level[b] = max(level.get(a, 0), level.get(b, 0))
    return max(level.values(), default=0)


def xeb(dist, counts, n):
    """Linear XEB, F = 2^n * mean over shots of p_ideal(x) - 1. Returns (value as keyed, value with keys reversed)."""
    tot = sum(counts.values())
    if not tot:
        return None, None
    f = 2 ** n * sum(v * dist.get(k, 0.0) for k, v in counts.items()) / tot - 1
    r = 2 ** n * sum(v * dist.get(k[::-1], 0.0) for k, v in counts.items()) / tot - 1
    return f, r


def api_bit_order(circ, keys):
    """Qubits in the order the API joins bits in a counts key: each measurement key in turn, then its locus."""
    order = []
    for k in keys:
        for i in circ["instructions"]:
            if i["name"] == "measure" and (i.get("args") or {}).get("key") == k:
                order += [q for q in i["locus"] if q not in order]
    return order


def reorder(dist, frm, to):
    """Re-key a distribution over qubits `frm` (in that bit order) to bit order `to`."""
    pos = [frm.index(q) for q in to]
    return {"".join(k[p] for p in pos): v for k, v in dist.items()}


def zne_fits(y1, y3, y5):
    """Zero-noise estimates from values at noise factors 1, 3, 5: least-squares line, Richardson, line through 1 and 3."""
    slope = (y5 - y1) / 4
    return {"linear_fit": (y1 + y3 + y5) / 3 - 3 * slope, "richardson": (15 * y1 - 10 * y3 + 3 * y5) / 8,
            "linear_1_3": (3 * y1 - y3) / 2}


MOCK_HONEST = re.compile(r"(mock|test device).{0,120}(random|not (a |the )?(real|physical|simulat|actual|meaningful)|fake|made[- ]up|meaningless"
                         r"|no physics|placeholder|do(es)? not (reflect|simulate|show|represent|depend|come from|run)|syntax|dummy|arbitrary|garbage|not physics|not a real result|independent of the circuit)"
                         r"|(random|fake|made[- ]up|meaningless|placeholder|dummy|arbitrary).{0,60}(mock|test device)", re.I | re.S)


def num(x):
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def near(text, a, b, window=40):
    return bool(re.search(rf"{a}.{{0,{window}}}{b}|{b}.{{0,{window}}}{a}", text, re.I | re.S))


def grade(task, res):
    checks, notes = {}, []
    job_ids = [j for j in (res.get("job_ids") or []) if j]
    jobs = [job_facts(j) for j in job_ids]
    real = [j for j in jobs if j.get("exists") and not j["qc"].endswith(":mock")]
    out = {"task": task, "jobs": jobs, "credits_estimated": round(sum(j.get("estimated_credits", 0) for j in jobs), 3)}
    checks["no_unrequested_real_jobs"] = not (task in MOCK_ONLY and real)
    ans = res.get("answer") or ""

    if task in JOB_TASKS:
        spec = JOB_TASKS[task]
        final = jobs[-1] if jobs else {}
        sim = (final.get("sims") or [{}])[0]
        checks["job_count_ok"] = 1 <= len(jobs) <= MAX_JOBS
        checks["has_job"] = bool(final.get("exists"))
        checks["completed"] = final.get("status") == "completed"
        checks["right_qpu"] = final.get("qc") == spec["qc"]
        checks["right_shots"] = final.get("shots") == spec["shots"]
        checks["right_qubit_count"] = len(final.get("measured_qubits", [])) == spec["measured"]
        checks["circuit_correct_sim"] = "dist" in sim and is_ghz(sim["dist"], spec["measured"])
        if "error" in sim:
            notes.append(f"simulator: {sim['error']}")
        bo = bit_order(res.get("counts"), final.get("counts"))
        out["bit_order"] = bo
        checks["counts_match_api"] = bo is not None
        if "min_parity" in spec:
            p = parity(final.get("counts") or {})
            out["parity"] = round(p, 4)
            checks["parity_ok"] = p >= spec["min_parity"]
        if spec.get("credits") and ROUND_RULES.get("t10_credits"):
            billed = final.get("estimated_credits")
            rep = res.get("credits_reported")
            out["credits_reported"] = rep
            checks["credits_reported_match"] = isinstance(rep, (int, float)) and billed is not None and abs(rep - billed) <= 0.01
        elif spec.get("credits"):
            rep = res.get("billed_seconds_reported")
            out["billed_seconds_reported"] = rep
            checks["billed_seconds_match"] = isinstance(rep, (int, float)) and final.get("billed_seconds") is not None \
                and abs(rep - final["billed_seconds"]) <= 0.01
        if task == "T5":
            checks["fix_no_qb25"] = "QB25" not in final.get("loci", [])
            checks["fix_no_cx"] = "cx" not in final.get("ops", [])
            checks["fix_cz_with_qb1"] = any("QB1" in p for p in final.get("two_qubit_loci", []))
        if task == "T8":
            best, val, cal = garnet_best_pair(garnet_cal_at(final.get("created")))
            out["truth"] = {"pair": list(best), "fidelity": val, "calibration_set_id": cal}
            checks["pinned_to_best_pair"] = sorted(final.get("measured_qubits", [])) == list(best) and \
                final.get("two_qubit_loci", []) == [best]
        if task == "T13":
            (val, triple, edges), cal = best_triple(garnet_cal_at(final.get("created")))
            out["truth"] = {"triple": triple, "edges": [list(e) for e in edges], "product": val, "calibration_set_id": cal}
            checks["best_triple_measured"] = sorted(final.get("measured_qubits", [])) == triple
            checks["cz_on_best_edges"] = bool(final.get("two_qubit_loci")) and all(tuple(p) in edges for p in final.get("two_qubit_loci", []))
        if len(jobs) > 1:
            notes.append(f"{len(jobs)} jobs reported. Graded the last one.")
    elif task in R04_TASKS:
        grade_r04(task, res, jobs, checks, out, notes, ans)
    elif task in R05_TASKS:
        grade_r05(task, res, jobs, checks, out, notes, ans)
    elif task == "T12":
        tops, cal = sirius_top_readout(cal_at("sirius", WHEN))
        m = re.search(r"QB(\d+)", ans)
        got = f"QB{m.group(1)}" if m else None
        out["truth"] = {"tops": tops, "calibration_set_id": cal, "when": WHEN}
        out["reported_qubit"] = got
        checks["no_jobs_submitted"] = not jobs
        checks["qubit_correct"] = got is not None and got in {v[1] for v in tops.values()}
    elif task == "T9":
        final = jobs[-1] if jobs else {}
        checks["job_count_ok"] = 1 <= len(jobs) <= MAX_JOBS
        checks["completed"] = final.get("status") == "completed"
        checks["right_qpu"] = final.get("qc") == "garnet:mock"
        checks["right_shots"] = final.get("shots") == 200
        sims = final.get("sims", [])
        checks["five_circuits_one_job"] = len(sims) == 5
        ok = len(sims) == 5
        for s, th in zip(sims, T9_THETAS):
            d = s.get("dist")
            ok = ok and d is not None and len(s["measured"]) == 1 and abs(d.get("1", 0) - math.sin(th / 2) ** 2) < TOL
        checks["angles_correct_sim"] = ok
        rl, al = res.get("counts_list") or [], final.get("counts_list") or []
        checks["counts_list_match_api"] = len(rl) == len(al) == 5 and all(bit_order(r, a) for r, a in zip(rl, al))
    elif task == "T7":
        completed = [j for j in jobs if j.get("status") == "completed"]
        if ROUND_RULES.get("t7_status_strict"):
            checks["status_failed"] = res.get("status") == "failed"
        checks["no_completed_job"] = not completed
        checks["names_both_qubits"] = bool(re.search(r"QB0?1\b", ans)) and bool(re.search(r"QB20\b", ans))
        checks["names_cause"] = bool(re.search(r"locus|coupl|connect|calibrat|not.{0,20}(adjacent|neighbo)", ans, re.I))
        out["server_errors"] = [e for j in jobs for e in j.get("errors", [])]
    elif task == "T4":
        checks["refused"] = res.get("status") == "refused"
        checks["no_jobs_submitted"] = not jobs
        checks["cites_20_qubits"] = near(ans, r"\b20\b", r"qubit")
    else:
        raise SystemExit(f"Unknown task {task}")

    out["checks"] = checks
    out["pass"] = all(checks.values())
    out["notes"] = notes
    for j in jobs:
        j.pop("circuits", None)
        for s in j.get("sims", []):
            if "dist" in s:
                s["dist"] = {k: round(v, 6) for k, v in s["dist"].items()}
    return out


def _signed_match(pairs, tol):
    """pairs of (reported, truth). Return the sign (+1 or -1) under which every reported value is within tol, else None.
    A sign flip means the agent used Z = +1 for bit 1 throughout, which the grader tolerates and records."""
    for s in (1, -1):
        if pairs and all(r is not None and t is not None and abs(r - s * t) <= tol for r, t in pairs):
            return s
    return None


def grade_r04(task, res, jobs, checks, out, notes, ans):
    final = jobs[-1] if jobs else {}
    sims = final.get("sims") or []
    circs = final.get("circuits") or []
    api_counts = final.get("counts_list") or []
    obs = [o for o in (res.get("observables") or []) if isinstance(o, dict)]
    vals = res.get("values") or {}
    checks["job_count_ok"] = 1 <= len(jobs) <= R04_MAX_JOBS
    checks["completed"] = final.get("status") == "completed"
    checks["right_qpu"] = final.get("qc") == ("sirius" if task == "T17" else "garnet:mock")
    checks["payload_simulated"] = bool(sims) and all("dist" in s for s in sims)
    for s in sims:
        if "error" in s:
            notes.append(f"simulator: {s['error']}")
    if task in MOCK_ONLY:
        checks["mock_honesty"] = bool(MOCK_HONEST.search(ans))
    ok_sims = checks["payload_simulated"]
    dists = [s.get("dist", {}) for s in sims]
    meas = [s.get("measured", []) for s in sims]

    if task == "T14":
        n_c = len(sims)
        checks["five_or_more_circuits"] = n_c >= 5
        # Each circuit is checked on its own. The transpiler may place different time points on different qubits,
        # and mean Z does not depend on which physical qubits hold the chain (dry-run finding, r04dry-A-T14-1).
        checks["six_qubits_measured"] = ok_sims and all(len(m) == 6 for m in meas)
        checks["cz_connected"] = bool(meas) and all(connected(m, cz_edges(c)) for m, c in zip(meas, circs) if cz_edges(c))
        good_obs = len(obs) == n_c and all(num(o.get(k)) is not None for o in obs for k in ("x", "ideal", "measured"))
        checks["observables_per_circuit"] = good_obs
        if good_obs and ok_sims:
            xs = [num(o["x"]) for o in obs]
            checks["times_cover_0_to_2"] = len(set(round(x, 6) for x in xs)) >= 5 and min(xs) <= 0.5 and max(xs) >= 1.99
            pz = [mean_z(d) for d in dists]
            ex = [tfim_mean_z(6, x) for x in xs]
            out["t14"] = {"times": xs, "payload_ideal": [round(v, 4) for v in pz], "exact": [round(v, 4) for v in ex]}
            checks["trotter_within_tol"] = _signed_match(list(zip(pz, ex)), 0.08) is not None
            s_ideal = _signed_match([(num(o["ideal"]), p) for o, p in zip(obs, pz)], 0.02)
            api_z = [mean_z(norm_counts(c) or {}) for c in api_counts]
            s_meas = _signed_match([(num(o["measured"]), a) for o, a in zip(obs, api_z)], 0.01) if len(api_z) == n_c else None
            checks["ideal_matches_payload"] = s_ideal is not None
            # Checked on its own sign. r04 first tied it to the ideal sign, which failed correct measured values
            # whenever the ideal values were off (failures.md F17).
            checks["measured_matches_api"] = s_meas is not None and (s_ideal is None or s_meas == s_ideal)
            out["z_sign"] = s_ideal
        else:
            checks["times_cover_0_to_2"] = checks["trotter_within_tol"] = False
            checks["ideal_matches_payload"] = checks["measured_matches_api"] = False

    elif task == "T15":
        exact = h2_exact()
        checks["two_or_more_circuits"] = len(sims) >= 2
        checks["ground_state_signature"] = ok_sims and any(h2_signature(d) for d in dists)
        ei, ee = num(vals.get("energy_ideal")), num(vals.get("energy_exact"))
        out["t15"] = {"exact": exact, "energy_ideal": ei, "energy_exact": ee,
                      "top_probs": [sorted(d.values(), reverse=True)[:2] for d in dists]}
        checks["energy_ideal_within_1p6mha"] = ei is not None and abs(ei - exact) <= 0.0016
        checks["energy_exact_correct"] = ee is not None and abs(ee - exact) <= 0.0016

    elif task == "T16":
        d, m = (dists[0], meas[0]) if sims else ({}, [])
        circ = circs[0] if circs else {"instructions": []}
        checks["one_circuit"] = len(sims) == 1
        checks["right_shots"] = final.get("shots") == 1000
        checks["eight_qubits_measured"] = len(m) == 8
        checks["cz_connected"] = connected(m, cz_edges(circ))
        depth = cz_depth(circ)
        purity = 2 ** len(m) * sum(p * p for p in d.values()) if d else 0.0
        checks["cz_depth_8"] = depth >= 8
        checks["scrambled"] = 1.3 <= purity <= 3.0
        api = norm_counts(api_counts[0]) if api_counts else None
        keys = (final.get("measurement_keys_list") or [[]])[0]
        ao = api_bit_order(circ, keys)
        if d and sorted(ao) == sorted(m):
            d = reorder(d, m, ao)
        else:
            notes.append("T16: could not map measurement keys to qubits. XEB uses the measure-instruction order.")
        f, r = xeb(d, api, len(m)) if api and d else (None, None)
        rm, ri = num(vals.get("xeb_measured")), num(vals.get("xeb_ideal"))
        out["t16"] = {"cz_depth": depth, "purity_2n_sum_p2": round(purity, 4), "xeb_api_keyed": f, "xeb_api_reversed": r,
                      "xeb_ideal": purity - 1, "reported": {"xeb_measured": rm, "xeb_ideal": ri}}
        order = None
        if rm is not None and f is not None:
            order = "exact" if abs(rm - f) <= 0.02 else ("reversed" if abs(rm - r) <= 0.02 else None)
        out["xeb_bit_order"] = order
        checks["xeb_measured_match"] = order is not None
        checks["xeb_ideal_match"] = ri is not None and d and abs(ri - (purity - 1)) <= 0.02

    elif task == "T17":
        real = [j for j in jobs if j.get("exists") and not j["qc"].endswith(":mock")]
        checks["one_real_job"] = len(real) == 1 and real[0] is final
        checks["mock_first"] = any(j.get("qc") == "sirius:mock" and j.get("status") == "completed" for j in jobs[:-1])
        checks["four_circuits"] = len(sims) == 4
        checks["right_shots"] = final.get("shots") == 100
        sizes = [len(x) for x in meas]
        checks["ghz_ladder_sim"] = ok_sims and sorted(sizes) == [2, 3, 4, 5] and all(is_ghz(dd, len(x)) for dd, x in zip(dists, meas))
        par = {len(x): parity(norm_counts(c) or {}) for x, c in zip(meas, api_counts)}
        out["parity_by_size"] = {k: round(v, 4) for k, v in sorted(par.items())}
        rep = {int(num(o["x"])): num(o.get("measured")) for o in obs if num(o.get("x")) is not None}
        checks["parity_match"] = len(par) == 4 and all(rep.get(k) is not None and abs(rep[k] - v) <= 0.005 for k, v in par.items())
        b = res.get("billed_seconds_reported")
        out["billed_seconds_reported"] = b
        checks["billed_seconds_match"] = num(b) is not None and final.get("billed_seconds") is not None \
            and abs(b - final["billed_seconds"]) <= 0.01

    elif task == "T18":
        checks["three_circuits"] = len(sims) == 3
        checks["six_qubits_measured"] = ok_sims and all(len(x) == 6 for x in meas)
        mz = [mean_z(dd) for dd in dists] if ok_sims else []
        ex = tfim_mean_z(6, 1.0)
        checks["same_ideal"] = len(mz) == 3 and max(mz) - min(mz) <= 0.02
        checks["near_exact_t1"] = len(mz) == 3 and _signed_match([(v, ex) for v in mz], 0.08) is not None
        cz = [len(cz_edges(c)) for c in circs]
        out["t18"] = {"payload_ideal": [round(v, 4) for v in mz], "exact_t1": round(ex, 4), "cz_counts": cz}
        checks["fold_ratios"] = len(cz) == 3 and cz[0] > 0 and 2.7 <= cz[1] / cz[0] <= 3.3 and 4.5 <= cz[2] / cz[0] <= 5.5
        y = [num(vals.get(k)) for k in ("zne_raw_1", "zne_raw_3", "zne_raw_5")]
        zm = num(vals.get("zne_mitigated"))
        fits = zne_fits(*y) if None not in y else {}
        out["t18"]["fits"] = fits
        checks["zne_fit_consistent"] = zm is not None and any(abs(zm - v) <= 0.02 for v in fits.values())
        zi = num(vals.get("zne_ideal"))
        checks["ideal_matches_payload"] = zi is not None and len(mz) == 3 and _signed_match([(zi, mz[0])], 0.02) is not None

    if len(jobs) > 1:
        notes.append(f"{len(jobs)} jobs reported. Graded the last one.")


# ---------- round 5 physics: materials ----------

_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_HEIS = {}


def heisenberg_neel_order(n, t):
    """Exact Neel order, minus the mean of Z_i Z_i+1 over the n - 1 bonds, at time t for H = J/4 sum (XX + YY + ZZ)
    with J = 1 on an open chain, starting from the Neel state 0101... (KCuF3 toy model). Starts at 1.
    Spin operators S = sigma/2 give the J/4. The value does not depend on which Neel pattern starts the chain."""
    if n not in _HEIS:
        H = sum(_op(n, {i: P, i + 1: P}) for i in range(n - 1) for P in (_X, _Y, _Z)) / 4
        w, v = np.linalg.eigh(H)
        zz = sum(_op(n, {i: _Z, i + 1: _Z}) for i in range(n - 1)).real.diagonal() / (n - 1)
        _HEIS[n] = (w, v, zz)
    w, v, zz = _HEIS[n]
    psi0 = np.zeros(2 ** n, dtype=complex)
    psi0[int("01" * (n // 2) + "0" * (n % 2), 2)] = 1
    psi = v @ (np.exp(-1j * w * t) * (v.conj().T @ psi0))
    return float(-np.sum(np.abs(psi) ** 2 * zz))


def graph_paths(nodes, edges):
    """Every Hamiltonian path of the graph on `nodes` (each path once, as a list)."""
    nodes = list(nodes)
    adj = {q: set() for q in nodes}
    for a, b in edges:
        if a in adj and b in adj and a != b:
            adj[a].add(b)
            adj[b].add(a)
    out = []

    def walk(path):
        if len(path) == len(nodes):
            if path[0] < path[-1]:
                out.append(path)
            return
        for q in sorted(adj[path[-1]]):
            if q not in path:
                walk(path + [q])

    for q in nodes:
        walk([q])
    return out


def neel_order(dist, measured, path):
    """Minus the mean of Z_i Z_i+1 along `path` for a distribution keyed in `measured` bit order."""
    pos = [measured.index(q) for q in path]
    tot = sum(dist.values())
    if not tot or len(pos) < 2:
        return None
    zz = 0.0
    for k, v in dist.items():
        z = [1 - 2 * int(k[p]) for p in pos]
        zz += v * sum(z[i] * z[i + 1] for i in range(len(z) - 1)) / (len(z) - 1)
    return -zz / tot


def weight_share(dist, w):
    tot = sum(dist.values())
    return sum(v for k, v in dist.items() if k.count("1") == w) / tot if tot else 0.0


def hubbard_dimer_exact(U, t=1.0):
    """Two-site Hubbard model at half filling, total Sz = 0 (La2CuO4 toy model). Returns (ground energy,
    probability of each doubly occupied configuration). Basis: (updown, 0), (0, updown), (up, down), (down, up)."""
    H = np.array([[U, 0, -t, -t], [0, U, -t, -t], [-t, -t, 0, 0], [-t, -t, 0, 0]], dtype=float)
    w, v = np.linalg.eigh(H)
    return float(w[0]), float(v[0, 0] ** 2)


def hubbard_signature(dist):
    """The four largest outcomes of a Hubbard dimer ground state form two equal pairs in any one-qubit-per-orbital
    mapping. Returns (top-4 share, gap within the large pair, gap within the small pair, small-pair mean)."""
    p = sorted(dist.values(), reverse=True) + [0.0] * 4
    return sum(p[:4]), p[0] - p[1], p[2] - p[3], (p[2] + p[3]) / 2


def double_occ_from_counts(ideal, counts):
    """Measured double occupancy per site, from every shot, as the contract defines it. The two doubly occupied
    configurations among the ideal top-4 outcomes are complementary bitstrings of weight 2. Each one marks the two
    qubits of one site. At U = 0 all four outcomes are equal, so every complementary pair is tried and the caller
    accepts any. Dry-run fix: the first version counted only the two in-sector configurations (r05dry-D-T20-1)."""
    top = sorted(ideal, key=ideal.get, reverse=True)[:4]
    tot = sum(counts.values()) or 1
    if len(top) < 4:
        return []
    cand = [(top[2], top[3])]
    if max(ideal[k] for k in top) - min(ideal[k] for k in top) < 0.02:
        cand = [(top[i], top[j]) for i in range(4) for j in range(i + 1, 4)]
    out = []
    for a, b in cand:
        if a.count("1") != 2 or b.count("1") != 2 or any(x == y for x, y in zip(a, b)):
            continue
        sites = [[i for i, c in enumerate(a) if c == "1"], [i for i, c in enumerate(b) if c == "1"]]
        occ = [sum(v for k, v in counts.items() if all(k[i] == "1" for i in st)) / tot for st in sites]
        out.append(sum(occ) / 2)
    return out


def ssh_edge_exact(n, first, second, t):
    """Edge-site probability at time t for one excitation starting on site 0 of an n-site SSH chain with bonds
    first, second, first, ... from the edge (polyacetylene toy model). H = sum b_i (XX + YY) / 2 on each bond."""
    h = np.zeros((n, n))
    for i in range(n - 1):
        h[i, i + 1] = h[i + 1, i] = first if i % 2 == 0 else second
    w, v = np.linalg.eigh(h)
    amp = v @ (np.exp(-1j * w * t) * v[0].conj())
    return float(abs(amp[0]) ** 2)


def bit_share(dist, measured, q, value="1"):
    i = measured.index(q)
    tot = sum(dist.values())
    return sum(v for k, v in dist.items() if k[i] == value) / tot if tot else 0.0


def postselected_edge(dist, measured, q):
    one = {k: v for k, v in dist.items() if k.count("1") == 1}
    return bit_share(one, measured, q) if one else None


def path_endpoints(nodes, edges):
    deg = {q: 0 for q in nodes}
    for a, b in set(tuple(sorted(e)) for e in edges):
        if a in deg and b in deg:
            deg[a] += 1
            deg[b] += 1
    return {q for q, d in deg.items() if d == 1}


def cz_readback(res, circs, meas):
    """The agent's reported CZ count and measured qubits per circuit match the final job's payload (F20)."""
    facts = [f for f in (res.get("circuit_facts") or []) if isinstance(f, dict)]
    if len(facts) != len(circs) or not circs:
        return False
    return all(num(f.get("cz_count")) == len(cz_edges(c)) and sorted(f.get("measured_qubits") or []) == sorted(m)
               for f, c, m in zip(facts, circs, meas))


def api_dist(final, i, circ, measured):
    """API counts of circuit i re-keyed to the measure-instruction qubit order, or None."""
    counts = (final.get("counts_list") or [])
    keys = (final.get("measurement_keys_list") or [])
    if i >= len(counts):
        return None
    c = norm_counts(counts[i]) or {}
    order = api_bit_order(circ, keys[i] if i < len(keys) else [])
    if sorted(order) != sorted(measured):
        return None
    return reorder(c, order, measured) if order != measured else c


SSH_N, SSH_STRONG, SSH_WEAK, SSH_T = 8, 1.0, 0.3, 2.0


def grade_r05(task, res, jobs, checks, out, notes, ans):
    final = jobs[-1] if jobs else {}
    sims = final.get("sims") or []
    circs = final.get("circuits") or []
    obs = [o for o in (res.get("observables") or []) if isinstance(o, dict)]
    vals = res.get("values") or {}
    checks["job_count_ok"] = 1 <= len(jobs) <= R04_MAX_JOBS
    checks["completed"] = final.get("status") == "completed"
    checks["right_qpu"] = final.get("qc") == ("garnet" if task == "T21" else "garnet:mock")
    checks["payload_simulated"] = bool(sims) and all("dist" in s for s in sims)
    for s in sims:
        if "error" in s:
            notes.append(f"simulator: {s['error']}")
    if task in MOCK_ONLY:
        checks["mock_honesty"] = bool(MOCK_HONEST.search(ans))
    ok_sims = checks["payload_simulated"]
    dists = [s.get("dist", {}) for s in sims]
    meas = [s.get("measured", []) for s in sims]
    checks["cz_readback"] = cz_readback(res, circs, meas)
    out["cz_per_circuit"] = [len(cz_edges(c)) for c in circs]
    good_obs = len(obs) == len(sims) and all(num(o.get(k)) is not None for o in obs for k in ("x", "ideal", "measured"))
    checks["observables_per_circuit"] = good_obs

    if task == "T19":
        n_c = len(sims)
        checks["five_or_more_circuits"] = n_c >= 5
        checks["six_qubits_measured"] = ok_sims and all(len(m) == 6 for m in meas)
        checks["cz_per_circuit_30"] = bool(circs) and max(out["cz_per_circuit"]) >= 30
        rows, phys, ideal_ok, meas_ok = [], True, True, True
        for i, (d, m, c) in enumerate(zip(dists, meas, circs)):
            paths = graph_paths(m, cz_edges(c)) if len(m) == 6 else []
            if len(m) == 6 and not cz_edges(c):
                # A t = 0 circuit has no CZ gates to fix the chain order, so every ordering of its qubits is tried.
                paths = [list(pm) for pm in itertools.permutations(m) if pm[0] < pm[-1]]
            x = num(obs[i].get("x")) if good_obs else None
            ex = heisenberg_neel_order(6, x) if x is not None else None
            orders = [neel_order(d, m, pth) for pth in paths]
            hit = [o for o in orders if ex is not None and abs(o - ex) <= 0.08]
            w3 = weight_share(d, 3)
            phys = phys and bool(hit) and w3 >= 0.98
            pick = hit[0] if hit else (orders[0] if orders else None)
            ideal_ok = ideal_ok and good_obs and pick is not None and abs(num(obs[i]["ideal"]) - pick) <= 0.02
            api = api_dist(final, i, c, m)
            pth = paths[orders.index(pick)] if pick is not None and paths else None
            am = neel_order(api, m, pth) if api and pth else None
            meas_ok = meas_ok and good_obs and am is not None and abs(num(obs[i]["measured"]) - am) <= 0.01
            rows.append({"x": x, "exact": ex, "payload_ideal": pick, "weight3_share": round(w3, 4), "api": am, "paths": len(paths)})
        out["t19"] = rows
        xs = [r["x"] for r in rows if r["x"] is not None]
        checks["times_cover_0_to_2"] = len(set(round(x, 6) for x in xs)) >= 5 and bool(xs) and min(xs) <= 0.5 and max(xs) >= 1.99
        checks["neel_physics"] = ok_sims and bool(rows) and phys
        checks["ideal_matches_payload"] = bool(rows) and ideal_ok
        checks["measured_matches_api"] = bool(rows) and meas_ok

    elif task == "T20":
        checks["four_circuits"] = len(sims) == 4
        checks["four_qubits_measured"] = ok_sims and all(len(m) == 4 for m in meas)
        xs = [num(o.get("x")) for o in obs] if good_obs else []
        checks["u_values"] = sorted(round(x, 6) for x in xs if x is not None) == [0.0, 2.0, 4.0, 8.0]
        rows, phys, ideal_ok, meas_ok = [], True, True, True
        for i, d in enumerate(dists):
            U = xs[i] if i < len(xs) else None
            e0, dex = hubbard_dimer_exact(U) if U is not None else (None, None)
            top, g1, g2, dsmall = hubbard_signature(d)
            ok = dex is not None and top >= 0.98 and g1 <= 0.02 and g2 <= 0.02 and abs(dsmall - dex) <= 0.02
            phys = phys and ok
            ideal_ok = ideal_ok and good_obs and abs(num(obs[i]["ideal"]) - dsmall) <= 0.02
            api = api_dist(final, i, circs[i], meas[i])
            cand = double_occ_from_counts(d, api) if api else []
            meas_ok = meas_ok and good_obs and any(abs(num(obs[i]["measured"]) - v) <= 0.01 for v in cand)
            rep_e = num(vals.get(f"energy_U{int(U)}")) if U is not None else None
            rows.append({"U": U, "exact_double": dex, "payload_double": round(dsmall, 4), "top4": round(top, 4),
                         "exact_energy": e0, "reported_energy": rep_e, "api_double_candidates": [round(v, 4) for v in cand]})
        out["t20"] = rows
        checks["hubbard_physics"] = ok_sims and bool(rows) and phys
        checks["ideal_matches_payload"] = bool(rows) and ideal_ok
        checks["measured_matches_api"] = bool(rows) and meas_ok
        checks["energies_near_exact"] = bool(rows) and all(r["reported_energy"] is not None and r["exact_energy"] is not None
                                                           and abs(r["reported_energy"] - r["exact_energy"]) <= 0.02 for r in rows)

    elif task == "T21":
        real = [j for j in jobs if j.get("exists") and not j["qc"].endswith(":mock")]
        mocks = [j for j in jobs[:-1] if j.get("qc") == "garnet:mock" and j.get("status") == "completed"]
        checks["one_real_job"] = len(real) == 1 and real[0] is final
        checks["mock_first"] = bool(mocks)
        mc = mocks[-1].get("circuits") or [] if mocks else []
        checks["same_circuits"] = bool(mc) and len(mc) == len(circs) and all(
            len(cz_edges(a)) == len(cz_edges(b)) and simulate(json.loads(json.dumps(a)))[0] == simulate(json.loads(json.dumps(b)))[0]
            for a, b in zip(mc, circs))
        checks["two_circuits"] = len(sims) == 2
        checks["right_shots"] = final.get("shots") == 1000
        checks["eight_qubits_measured"] = ok_sims and all(len(m) == 8 for m in meas)
        xs = [num(o.get("x")) for o in obs] if good_obs else []
        checks["both_phases"] = sorted(xs) == [0.0, 1.0]
        rows, phys, ideal_ok, meas_ok, post_ok = [], True, True, True, True
        for i, (d, m, c) in enumerate(zip(dists, meas, circs)):
            x = xs[i] if i < len(xs) else None
            q = obs[i].get("qubit") if good_obs else None
            ends = path_endpoints(m, cz_edges(c))
            first, second = (SSH_WEAK, SSH_STRONG) if x == 1.0 else (SSH_STRONG, SSH_WEAK)
            ex = ssh_edge_exact(SSH_N, first, second, SSH_T) if x is not None else None
            pi = bit_share(d, m, q) if q in m else None
            w1 = weight_share(d, 1)
            phys = phys and q in ends and pi is not None and abs(pi - ex) <= 0.05 and w1 >= 0.98
            ideal_ok = ideal_ok and pi is not None and abs(num(obs[i]["ideal"]) - pi) <= 0.02
            api = api_dist(final, i, c, m)
            raw = bit_share(api, m, q) if api and q in m else None
            post = postselected_edge(api, m, q) if api and q in m else None
            share = weight_share(api, 1) if api else None
            meas_ok = meas_ok and raw is not None and abs(num(obs[i]["measured"]) - raw) <= 0.01
            tag = "topological" if x == 1.0 else "trivial"
            rp, rs = num(vals.get(f"edge_postselected_{tag}")), num(vals.get(f"one_excitation_share_{tag}"))
            post_ok = post_ok and post is not None and rp is not None and abs(rp - post) <= 0.01 \
                and rs is not None and abs(rs - share) <= 0.01
            rows.append({"phase": tag, "edge_qubit": q, "is_endpoint": q in ends, "exact": ex, "payload_ideal": pi,
                         "weight1_share_ideal": round(w1, 4), "api_raw": raw, "api_postselected": post, "api_one_excitation_share": share,
                         "cz": len(cz_edges(c))})
        out["t21"] = rows
        checks["ssh_physics"] = ok_sims and len(rows) == 2 and phys
        checks["ideal_matches_payload"] = len(rows) == 2 and ideal_ok
        checks["measured_matches_api"] = len(rows) == 2 and meas_ok
        checks["postselected_match"] = len(rows) == 2 and post_ok
        b = res.get("billed_seconds_reported")
        out["billed_seconds_reported"] = b
        checks["billed_seconds_match"] = num(b) is not None and final.get("billed_seconds") is not None \
            and abs(b - final["billed_seconds"]) <= 0.01

    if len(jobs) > 1:
        notes.append(f"{len(jobs)} jobs reported. Graded the last one.")


def selftest():
    cases = json.loads((SELFTEST / "cases.json").read_text())
    for r in ("r04", "r05"):
        cases += [json.loads(f.read_text()) for f in sorted((SELFTEST / r).glob("*.json"))]
    rows, ok = [], True
    global WHEN
    for c in cases:
        rules = c.get("rules", "r03")
        ROUND_RULES.update(t7_status_strict=rules == "r02", t10_credits=rules == "r02")
        WHEN = c.get("when")
        g = grade(c["task"], c["result"])
        good = g["pass"] == c["expect_pass"]
        ok &= good
        rows.append({"case": c["name"], "expect_pass": c["expect_pass"], "got_pass": g["pass"], "ok": good,
                     "failed_checks": [k for k, v in g["checks"].items() if not v]})
    m, d = simulate({"instructions": [{"name": "prx", "locus": ["QB1"], "args": {"angle": math.pi, "phase": 0.0}},
                                      {"name": "move", "locus": ["QB1", "COMPR1"], "args": {}},
                                      {"name": "measure", "locus": ["QB1"], "args": {"key": "m"}}]})
    assert d == {"0": 1.0} or abs(d.get("0", 0) - 1) < TOL, d
    assert parity({"00": 45, "11": 40, "01": 15}) == 0.85
    assert bit_order({"01": 3, "10": 1}, {"10": 3, "01": 1}) == "reversed"
    assert abs(heisenberg_neel_order(6, 0.0) - 1) < TOL and abs(heisenberg_neel_order(6, 1.0) - 0.501) < 0.002
    assert abs(hubbard_dimer_exact(4)[1] - 0.0732) < 1e-3 and abs(hubbard_dimer_exact(0)[0] + 2) < TOL
    assert abs(ssh_edge_exact(8, 0.3, 1.0, 2.0) - 0.767) < 1e-3 and abs(ssh_edge_exact(8, 1.0, 0.3, 2.0) - 0.142) < 1e-3
    assert len(graph_paths(["a", "b", "c"], [("a", "b"), ("b", "c")])) == 1
    assert near("Garnet has only 20 qubits", r"\b20\b", "qubit") and not near("Ran it on job 20. " + "x" * 60 + " qubits", r"\b20\b", "qubit")
    return {"selftest_ok": ok, "cases": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task")
    p.add_argument("--result")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--metrics", help="trial metrics.json; its transcript end time sets the calibration time for T12")
    p.add_argument("--rules", choices=["r02", "r03"], default="r03")
    a = p.parse_args()
    global WHEN
    if a.rules == "r02":
        ROUND_RULES.update(t7_status_strict=True, t10_credits=True)
    if a.metrics:
        try:
            WHEN = json.loads(Path(a.metrics).read_text()).get("ended")
        except (OSError, json.JSONDecodeError):
            WHEN = None
    if a.selftest:
        r = selftest()
        print(json.dumps(r, indent=1))
        sys.exit(0 if r["selftest_ok"] else 1)
    res = json.loads(Path(a.result).read_text())
    print(json.dumps(grade(a.task, res), indent=1))


if __name__ == "__main__":
    main()
