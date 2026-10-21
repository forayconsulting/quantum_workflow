"""IQM Resonance helper for agents. Run with the .venv-iqm Python.

Subcommands:
  list                         QPU aliases, health, queue length
  arch QC                      qubits, resonators, cz and move loci
  calib QC [--top N]           IRB CZ fidelity per pair, best first
  run QC --qasm FILE --shots N [--allow-real]
                               transpile an OpenQASM 2 circuit for QC (MOVE-aware) and submit it
  submit QC --json FILE --shots N [--allow-real]
                               submit IQM native circuit JSON (one circuit or a list)
  status JOB                   job status, QPU alias, billed seconds
  result JOB                   counts, QPU alias, shots, billed seconds, estimated credits
  cancel JOB                   cancel a job

Guards: real (non-mock) QPUs need --allow-real. Shots are capped at 1000.
Credit estimate = billed_seconds x the QPU rate (sirius 0.3, garnet 0.5, emerald 0.75 per second).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path("/Users/claytonchancey/Desktop/quantum")
load_dotenv(ROOT / ".env")
BASE = "https://resonance.iqm.tech"
API = f"{BASE}/api/v1"
RATES = {"sirius": 0.3, "garnet": 0.5, "emerald": 0.75}
MAX_SHOTS = 1000
LOG = ROOT / "spe" / "agent-tools" / "calls.log.jsonl"


def headers():
    return {"Authorization": f"Bearer {os.environ['IQM_TOKEN']}", "Accept": "application/json"}


def get(path):
    r = requests.get(f"{API}/{path}", headers=headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def aliases_by_id():
    return {q["id"]: q["alias"] for q in get("quantum-computers")["quantum_computers"]}


def out(obj):
    print(json.dumps(obj, indent=1))


def log(cmd, data):
    try:
        with LOG.open("a") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cmd": cmd, **data}) + "\n")
    except OSError:
        pass


def guard(qc, shots, allow_real):
    if shots < 1 or shots > MAX_SHOTS:
        sys.exit(f"Refused: shots must be 1..{MAX_SHOTS}.")
    if not qc.endswith(":mock") and not allow_real:
        sys.exit(f"Refused: {qc} is real hardware and costs credits. Test on {qc}:mock first, then pass --allow-real.")


def cmd_list(a):
    out([{"alias": q["alias"], "healthy": q["health"]["healthy"], "status": q["operational_status"],
          "queue_length": q["queue_length"]} for q in get("quantum-computers")["quantum_computers"]])


def cmd_arch(a):
    d = get(f"calibration-sets/{a.qc}/default/dynamic-quantum-architecture")
    gates = {}
    for g in ("cz", "move"):
        if g in d["gates"]:
            gi = d["gates"][g]
            gates[g] = gi["implementations"][gi["default_implementation"]]["loci"]
    out({"qc": a.qc, "calibration_set_id": d["calibration_set_id"], "num_qubits": len(d["qubits"]),
         "qubits": d["qubits"], "resonators": d.get("computational_resonators", []), "loci": gates})


def cmd_calib(a):
    m = get(f"calibration-sets/{a.qc}/default/metrics")
    rows = []
    for o in m["observations"]:
        f = o["dut_field"]
        if f.startswith("metrics.irb.cz.") and ".fidelity" in f and not o.get("invalid"):
            rows.append({"pair": f.split(".")[4].replace("__", "-"), "irb_cz_fidelity": o["value"],
                         "uncertainty": o.get("uncertainty"), "field": f})
    rows.sort(key=lambda r: -r["irb_cz_fidelity"])
    out({"qc": a.qc, "calibration_set_id": m.get("describes_id"), "pairs": rows[: a.top]})


def submit_body(qc, body):
    r = requests.post(f"{API}/jobs/{qc}/circuit?use_timeslot=false",
                      headers={**headers(), "Content-Type": "application/json"}, json=body, timeout=120)
    if r.status_code >= 300:
        sys.exit(f"Submit failed: HTTP {r.status_code}: {r.text[:500]}")
    return r.json()["id"]


def cmd_submit(a):
    guard(a.qc, a.shots, a.allow_real)
    circuits = json.loads(Path(a.json).read_text())
    if isinstance(circuits, dict):
        circuits = [circuits]
    job_id = submit_body(a.qc, {"circuits": circuits, "shots": a.shots})
    log("submit", {"qc": a.qc, "shots": a.shots, "job_id": job_id})
    out({"job_id": job_id, "qc": a.qc, "shots": a.shots})


def cmd_run(a):
    guard(a.qc, a.shots, a.allow_real)
    from qiskit import qasm2
    from iqm.qiskit_iqm import IQMProvider, transpile_to_IQM

    circ = qasm2.loads(Path(a.qasm).read_text())
    backend = IQMProvider(BASE, quantum_computer=a.qc).get_backend()
    if circ.num_qubits > backend.num_qubits:
        sys.exit(f"Refused: circuit needs {circ.num_qubits} qubits but {a.qc} has {backend.num_qubits}.")
    tq = transpile_to_IQM(circ, backend)
    job = backend.run(tq, shots=a.shots)
    log("run", {"qc": a.qc, "shots": a.shots, "job_id": job.job_id()})
    out({"job_id": job.job_id(), "qc": a.qc, "shots": a.shots,
         "transpiled_ops": {k: int(v) for k, v in tq.count_ops().items()}})


def job_summary(job_id):
    j = get(f"jobs/{job_id}")
    alias = aliases_by_id().get(j["qc"]["id"], j["qc"]["id"])
    billed = (j.get("metrics") or {}).get("billed_seconds")
    rate = 0.0 if alias.endswith(":mock") else RATES.get(alias.split(":")[0], 0.0)
    return j, {"job_id": job_id, "qc": alias, "status": j["status"], "billed_seconds": billed,
               "estimated_credits": round(billed * rate, 3) if billed is not None else None,
               "errors": j.get("errors", [])}


def cmd_status(a):
    out(job_summary(a.job)[1])


def cmd_result(a):
    for _ in range(a.wait):
        j, s = job_summary(a.job)
        if s["status"] in ("completed", "failed", "cancelled"):
            break
        time.sleep(2)
    if s["status"] == "completed":
        s["shots"] = get(f"jobs/{a.job}/payload").get("shots")
        s["counts"] = get(f"jobs/{a.job}/artifacts/measurement_counts")
    out(s)


def cmd_cancel(a):
    r = requests.post(f"{API}/jobs/{a.job}/cancel", headers=headers(), timeout=60)
    log("cancel", {"job_id": a.job, "http": r.status_code})
    out({"job_id": a.job, "http": r.status_code})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("list").set_defaults(f=cmd_list)
    x = s.add_parser("arch"); x.add_argument("qc"); x.set_defaults(f=cmd_arch)
    x = s.add_parser("calib"); x.add_argument("qc"); x.add_argument("--top", type=int, default=10); x.set_defaults(f=cmd_calib)
    for name, f, src in (("run", cmd_run, "--qasm"), ("submit", cmd_submit, "--json")):
        x = s.add_parser(name); x.add_argument("qc"); x.add_argument(src, required=True)
        x.add_argument("--shots", type=int, required=True); x.add_argument("--allow-real", action="store_true")
        x.set_defaults(f=f)
    x = s.add_parser("status"); x.add_argument("job"); x.set_defaults(f=cmd_status)
    x = s.add_parser("result"); x.add_argument("job"); x.add_argument("--wait", type=int, default=600, help="polls, 2 s apart"); x.set_defaults(f=cmd_result)
    x = s.add_parser("cancel"); x.add_argument("job"); x.set_defaults(f=cmd_cancel)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
