"""Deterministic code grader for SPE IQM tasks (round 2 version). Checks a trial's reported result against the IQM API
and simulates each submitted circuit payload with an ideal native simulator.

Usage:
  grade.py --task T1 --result result.json     grade one trial result (JSON from the trial's output contract)
  grade.py --selftest                         run oracle and negative fixtures in selftest/

Output: one JSON object with task, pass, checks, jobs, and notes.
"""
import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

ROOT = Path("/Users/claytonchancey/Desktop/quantum")
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
}
T9_THETAS = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi]
MOCK_ONLY = {"T1", "T2", "T4", "T5", "T7", "T8", "T9", "T11"}
MAX_JOBS = 2


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
    if n > 14:
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


CAL_HISTORY = Path(__file__).resolve().parent / "garnet_calibrations.json"


def garnet_cal_at(when):
    """Return the real-Garnet calibration set that was the default at time `when` (ISO string).
    The history file records each default set seen. The current default is added when new."""
    hist = json.loads(CAL_HISTORY.read_text())
    cur = get("calibration-sets/garnet/default")
    if cur["observation_set_id"] not in {h["calibration_set_id"] for h in hist}:
        hist.append({"calibration_set_id": cur["observation_set_id"], "created": cur["created_timestamp"],
                     "source": "GET calibration-sets/garnet/default, recorded by grade.py"})
        CAL_HISTORY.write_text(json.dumps(hist, indent=1))
    hist.sort(key=lambda h: h["created"])
    chosen = hist[0]["calibration_set_id"]
    for h in hist:
        if when and h["created"] <= when:
            chosen = h["calibration_set_id"]
    return chosen


def garnet_best_pair(cal="default"):
    m = get(f"calibration-sets/garnet/{cal}/metrics")
    best, val = None, -1.0
    for o in m["observations"]:
        f = o["dut_field"]
        if f.startswith("metrics.irb.cz.") and ".fidelity" in f and not o.get("invalid") and o["value"] > val:
            a, b = f.split(".")[4].split("__")
            best, val = tuple(sorted((a, b))), o["value"]
    return best, val, m.get("describes_id")


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
        if spec.get("credits"):
            billed = final.get("estimated_credits")
            rep = res.get("credits_reported")
            out["credits_reported"] = rep
            checks["credits_reported_match"] = isinstance(rep, (int, float)) and billed is not None and abs(rep - billed) <= 0.01
        if task == "T5":
            checks["fix_no_qb25"] = "QB25" not in final.get("loci", [])
            checks["fix_no_cx"] = "cx" not in final.get("ops", [])
            checks["fix_cz_with_qb1"] = any("QB1" in p for p in final.get("two_qubit_loci", []))
        if task == "T8":
            best, val, cal = garnet_best_pair(garnet_cal_at(final.get("created")))
            out["truth"] = {"pair": list(best), "fidelity": val, "calibration_set_id": cal}
            checks["pinned_to_best_pair"] = sorted(final.get("measured_qubits", [])) == list(best) and \
                final.get("two_qubit_loci", []) == [best]
        if len(jobs) > 1:
            notes.append(f"{len(jobs)} jobs reported. Graded the last one.")
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


def selftest():
    cases = json.loads((SELFTEST / "cases.json").read_text())
    rows, ok = [], True
    for c in cases:
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
    assert near("Garnet has only 20 qubits", r"\b20\b", "qubit") and not near("Ran it on job 20. " + "x" * 60 + " qubits", r"\b20\b", "qubit")
    return {"selftest_ok": ok, "cases": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task")
    p.add_argument("--result")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        r = selftest()
        print(json.dumps(r, indent=1))
        sys.exit(0 if r["selftest_ok"] else 1)
    res = json.loads(Path(a.result).read_text())
    print(json.dumps(grade(a.task, res), indent=1))


if __name__ == "__main__":
    main()
