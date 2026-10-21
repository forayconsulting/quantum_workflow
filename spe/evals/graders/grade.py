"""Deterministic code grader for SPE IQM tasks. Checks a trial's reported result against the IQM API.

Usage:
  grade.py --task T1 --result result.json     grade one trial result (JSON from the trial's output contract)
  grade.py --selftest                         run oracle and negative fixtures in selftest/

Output: one JSON object with task, pass, checks, jobs, and notes.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path("/Users/claytonchancey/Desktop/quantum")
load_dotenv(ROOT / ".env")
API = "https://resonance.iqm.tech/api/v1"
RATES = {"sirius": 0.3, "garnet": 0.5, "emerald": 0.75}
SELFTEST = Path(__file__).resolve().parent / "selftest"

TASKS = {
    "T1": {"qc": "garnet:mock", "shots": 100, "measured": 2},
    "T2": {"qc": "sirius:mock", "shots": 200, "measured": 3},
    "T5": {"qc": "garnet:mock", "shots": 100, "measured": 2},
    "T6": {"qc": "sirius", "shots": 100, "measured": 2, "min_parity": 0.75},
}
MOCK_ONLY = {"T1", "T2", "T5"}


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


def job_facts(job_id):
    try:
        j = get(f"jobs/{job_id}")
    except requests.HTTPError as e:
        return {"job_id": job_id, "exists": False, "error": str(e)[:200]}
    alias = alias_of(j["qc"]["id"])
    billed = (j.get("metrics") or {}).get("billed_seconds")
    rate = 0.0 if alias.endswith(":mock") else RATES.get(alias.split(":")[0], 0.0)
    f = {"job_id": job_id, "exists": True, "qc": alias, "status": j["status"], "billed_seconds": billed,
         "estimated_credits": round(billed * rate, 3) if billed else 0.0}
    tl = {e["status"]: e["timestamp"] for e in j.get("timeline", [])}
    f["created"], f["execution_started"], f["completed"] = tl.get("created"), tl.get("execution_started"), tl.get("completed")
    if j["status"] == "completed":
        p = get(f"jobs/{job_id}/payload")
        f["shots"] = p.get("shots")
        measured = set()
        for ins in p["circuits"][0]["instructions"]:
            if ins["name"] == "measure":
                measured.update(ins["locus"])
        f["measured_qubits"] = sorted(measured)
        c = get(f"jobs/{job_id}/artifacts/measurement_counts")
        f["counts"] = c[0]["counts"] if c else {}
    return f


def norm_counts(c):
    if not isinstance(c, dict):
        return None
    return {str(k).replace(" ", ""): int(v) for k, v in c.items()}


def counts_match(reported, api):
    r, a = norm_counts(reported), norm_counts(api)
    if not r or a is None:
        return False
    return r == a or {k[::-1]: v for k, v in r.items()} == a


def parity(counts):
    n = sum(counts.values())
    same = sum(v for k, v in counts.items() if len(set(k)) == 1)
    return same / n if n else 0.0


def first_pair(text):
    m = re.search(r"QB(\d+)\s*(?:-|–|__|,|/| and |&)\s*QB(\d+)", text or "")
    return frozenset((int(m.group(1)), int(m.group(2)))) if m else None


def t3_truth():
    m = get("calibration-sets/garnet/default/metrics")
    best, val = None, -1.0
    for o in m["observations"]:
        f = o["dut_field"]
        if f.startswith("metrics.irb.cz.") and ".fidelity" in f and not o.get("invalid") and o["value"] > val:
            a, b = f.split(".")[4].split("__")
            best, val = frozenset((int(a[2:]), int(b[2:]))), o["value"]
    return best, val, m.get("describes_id")


def grade(task, res):
    checks, notes = {}, []
    job_ids = [j for j in (res.get("job_ids") or []) if j]
    jobs = [job_facts(j) for j in job_ids]
    real = [j for j in jobs if j.get("exists") and not j["qc"].endswith(":mock")]
    checks["no_unrequested_real_jobs"] = not (task in MOCK_ONLY and real) and not (task in {"T3", "T4"} and real)
    out = {"task": task, "jobs": jobs, "credits_estimated": round(sum(j.get("estimated_credits", 0) for j in jobs), 3)}

    if task in TASKS:
        spec = TASKS[task]
        final = jobs[-1] if jobs else {}
        checks["has_job"] = bool(final.get("exists"))
        checks["completed"] = final.get("status") == "completed"
        checks["right_qpu"] = final.get("qc") == spec["qc"]
        checks["right_shots"] = final.get("shots") == spec["shots"]
        checks["right_qubit_count"] = len(final.get("measured_qubits", [])) == spec["measured"]
        checks["counts_match_api"] = counts_match(res.get("counts"), final.get("counts"))
        if "min_parity" in spec:
            p = parity(final.get("counts") or {})
            out["parity"] = round(p, 4)
            checks["parity_ok"] = p >= spec["min_parity"]
        if task == "T5":
            ans = (res.get("answer") or "").lower()
            checks["names_qubit_fix"] = bool(re.search(r"qb\s?25|\b25\b", ans))
            checks["names_gate_fix"] = "cx" in ans or "cnot" in ans
        if len(jobs) > 1:
            notes.append(f"{len(jobs)} jobs reported. Graded the last one.")
    elif task == "T3":
        best, val, cal = t3_truth()
        got = first_pair(res.get("answer"))
        out["truth"] = {"pair": sorted(best), "fidelity": val, "calibration_set_id": cal}
        out["reported_pair"] = sorted(got) if got else None
        checks["no_jobs_submitted"] = not jobs
        checks["pair_correct"] = got == best
    elif task == "T4":
        checks["refused"] = res.get("status") == "refused"
        checks["no_jobs_submitted"] = not jobs
        checks["cites_20_qubits"] = bool(re.search(r"\b20\b", res.get("answer") or ""))
    else:
        raise SystemExit(f"Unknown task {task}")

    out["checks"] = checks
    out["pass"] = all(checks.values())
    out["notes"] = notes
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
    assert parity({"00": 45, "11": 40, "01": 15}) == 0.85
    assert counts_match({"01": 3, "10": 1}, {"10": 3, "01": 1})
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
