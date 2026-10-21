"""Build rNN.json, the scorecard, and the offline dashboard from per-trial files and the workflow output.

Usage: build_results.py --round r01 --workflow-output PATH
The per-trial grade and metrics files in evals/results/<round>/trials/ are the source of truth.
The workflow output adds the trial result objects and judge verdicts.
"""
import argparse
import html
import json
import math
import statistics as st
from pathlib import Path

SPE = Path("/Users/claytonchancey/Desktop/quantum/spe")
CONFIGS = ["A", "B", "C", "D"]
TASKS = ["T1", "T2", "T3", "T4", "T5", "T6"]
CHECKS = ["tool_choice", "arguments", "when_to_call", "when_not_to_call", "multi_step", "efficiency", "honesty"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def load_workflow(path):
    raw = Path(path).read_text()
    i = raw.find("{")
    data = json.loads(raw[i:raw.rfind("}") + 1])
    return data.get("result", data) if isinstance(data.get("result", data), dict) else json.loads(data["result"])


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--round", required=True)
    a.add_argument("--workflow-output", required=True)
    args = a.parse_args()
    rnd = args.round
    tdir = SPE / f"evals/results/{rnd}/trials"
    wf = load_workflow(args.workflow_output)
    by_id = {t["id"]: t for t in wf["trials"]}

    rows = []
    for g in sorted(tdir.glob("*.grade.json")):
        tid = g.name.replace(".grade.json", "")
        _, cfg, task, n = tid.split("-")
        mpath = tdir / f"{tid}.metrics.json"
        try:
            grade = json.loads(g.read_text())
        except json.JSONDecodeError:
            grade = {"pass": False, "checks": {}, "error": "grade file unreadable"}
        try:
            metrics = json.loads(mpath.read_text()) if mpath.exists() else {"error": "missing"}
        except json.JSONDecodeError:
            metrics = {"error": "metrics file unreadable"}
        w = by_id.get(tid, {})
        status = "COMPLETE"
        if "error" in metrics or "error" in grade:
            status = "INCOMPLETE"
        elif metrics.get("peeked"):
            status = "PEEKED"
        rows.append({"id": tid, "config": cfg, "task": task, "n": int(n), "status": status,
                     "pass": bool(grade.get("pass")) if status == "COMPLETE" else None,
                     "failed_checks": [k for k, v in grade.get("checks", {}).items() if not v],
                     "grade": grade, "metrics": metrics, "result": w.get("result"), "judge": w.get("judge")})

    scored = [r for r in rows if r["status"] == "COMPLETE"]
    per_cfg = {}
    for c in CONFIGS:
        rs = [r for r in scored if r["config"] == c]
        mock = [r for r in rs if r["task"] != "T6"]
        k = sum(r["pass"] for r in mock)
        cells = {}
        for t in TASKS:
            ct = [r for r in rs if r["task"] == t]
            first3 = [r for r in ct if r["n"] <= 3]
            cells[t] = {"n": len(ct), "pass": sum(r["pass"] for r in ct),
                        "pass3": len(first3) == 3 and all(r["pass"] for r in first3)}
        judge_rates = {}
        for ch in CHECKS:
            vs = [r["judge"][ch]["verdict"] for r in rs if r.get("judge") and ch in r["judge"]]
            judge_rates[ch] = round(vs.count("PASS") / len(vs), 2) if vs else None
        per_cfg[c] = {
            "trials_scored": len(rs),
            "pass_at_1_T1_T5": round(k / len(mock), 3) if mock else None,
            "pass_at_1_T1_T5_ci95": wilson(k, len(mock)),
            "pass3_cells_T1_T5": sum(cells[t]["pass3"] for t in TASKS[:5]),
            "T6_passes": f'{cells["T6"]["pass"]} of {cells["T6"]["n"]}',
            "median_tool_calls": med([r["metrics"].get("tool_calls") for r in rs]),
            "median_total_tokens": med([r["metrics"].get("tokens", {}).get("total") for r in rs]),
            "median_output_tokens": med([r["metrics"].get("tokens", {}).get("output_tokens") for r in rs]),
            "median_wall_minutes": med([(r["metrics"].get("wall_seconds") or 0) / 60 for r in rs]),
            "tool_errors_total": sum(r["metrics"].get("tool_errors", 0) for r in rs),
            "cells": cells,
            "judge_pass_rate": judge_rates,
        }

    t6 = []
    for r in scored:
        if r["task"] == "T6" and r["grade"].get("jobs"):
            j = r["grade"]["jobs"][-1]
            t6.append({"id": r["id"], "parity": r["grade"].get("parity"), "qc": j.get("qc"),
                       "credits_estimated": r["grade"].get("credits_estimated"),
                       "created": j.get("created"), "execution_started": j.get("execution_started")})

    out = {"round": rnd, "trials": rows, "per_config": per_cfg, "t6": t6,
           "counts": {s: sum(r["status"] == s for r in rows) for s in ("COMPLETE", "INCOMPLETE", "PEEKED")},
           "credits_estimated_total": round(sum(r["grade"].get("credits_estimated", 0) or 0 for r in rows), 3),
           "workflow": {k: wf.get(k) for k in ("unstable", "skipped_real", "credits_estimated")},
           "analysis": wf.get("analysis"), "critic": wf.get("critic")}
    res = SPE / f"evals/results/{rnd}"
    (res / f"{rnd}.json").write_text(json.dumps(out, indent=1))

    # Scorecard
    L = [f"# Scorecard, round {rnd}", "",
         f"Trials: {out['counts']['COMPLETE']} complete, {out['counts']['INCOMPLETE']} incomplete, {out['counts']['PEEKED']} peeked. "
         f"Estimated real-QPU credits: {out['credits_estimated_total']}.", "",
         "| Config | pass@1 T1-T5 (95% CI) | pass^3 cells of 5 | T6 | Median tool calls | Median total tokens | Median output tokens | Median wall min | Tool errors |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c, p in per_cfg.items():
        ci = p["pass_at_1_T1_T5_ci95"]
        L.append(f"| {c} | {p['pass_at_1_T1_T5']} ({ci[0]} to {ci[1]}) | {p['pass3_cells_T1_T5']} | {p['T6_passes']} | "
                 f"{p['median_tool_calls']} | {p['median_total_tokens']} | {p['median_output_tokens']} | {p['median_wall_minutes']} | {p['tool_errors_total']} |")
    L += ["", "## Passes per cell (pass of n)", "", "| Config | " + " | ".join(TASKS) + " |", "|---" * (len(TASKS) + 1) + "|"]
    for c, p in per_cfg.items():
        L.append(f"| {c} | " + " | ".join(f"{p['cells'][t]['pass']} of {p['cells'][t]['n']}" for t in TASKS) + " |")
    L += ["", "## Judge PASS rate per check (descriptive, unvalidated)", "", "| Config | " + " | ".join(CHECKS) + " |", "|---" * (len(CHECKS) + 1) + "|"]
    for c, p in per_cfg.items():
        L.append(f"| {c} | " + " | ".join(str(p["judge_pass_rate"][ch]) for ch in CHECKS) + " |")
    L += ["", "## T6 real-hardware jobs", "", "| Trial | QPU | P(00)+P(11) | Est. credits | Created | Execution started |", "|---|---|---|---|---|---|"]
    for t in t6:
        L.append(f"| {t['id']} | {t['qc']} | {t['parity']} | {t['credits_estimated']} | {t['created']} | {t['execution_started']} |")
    L += ["", "## Failed trials", "", "| Trial | Failed checks | Judge summary |", "|---|---|---|"]
    for r in rows:
        if r["status"] != "COMPLETE" or not r["pass"]:
            js = (r.get("judge") or {}).get("summary", "")
            L.append(f"| {r['id']} ({r['status']}) | {', '.join(r['failed_checks']) or '-'} | {js} |")
    (res / f"{rnd}-scorecard.md").write_text("\n".join(L) + "\n")

    # Offline dashboard: inline SVG bars, no external assets
    bars = []
    for i, (c, p) in enumerate(per_cfg.items()):
        v = p["pass_at_1_T1_T5"] or 0
        lo, hi = p["pass_at_1_T1_T5_ci95"]
        x = 60 + i * 110
        h = v * 200
        bars.append(f'<rect x="{x}" y="{230 - h}" width="60" height="{h}" fill="var(--bar)"/>'
                    f'<line x1="{x+30}" x2="{x+30}" y1="{230 - (hi or 0)*200}" y2="{230 - (lo or 0)*200}" stroke="var(--fg)" stroke-width="2"/>'
                    f'<text x="{x+30}" y="250" text-anchor="middle">{c}</text>'
                    f'<text x="{x+30}" y="{224 - h}" text-anchor="middle">{v:.2f}</text>')
    table = "".join(f"<tr><td>{c}</td><td>{p['pass_at_1_T1_T5']}</td><td>{p['pass3_cells_T1_T5']}</td><td>{p['T6_passes']}</td>"
                    f"<td>{p['median_tool_calls']}</td><td>{p['median_total_tokens']}</td><td>{p['median_wall_minutes']}</td></tr>"
                    for c, p in per_cfg.items())
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPE {rnd} dashboard</title><style>
:root{{--bg:#fff;--fg:#1a1a1a;--bar:#3b6ea8;--line:#ddd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181c;--fg:#e8e8e8;--bar:#6c9bd2;--line:#333}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:760px;padding:16px}}
svg text{{fill:var(--fg);font-size:13px}} table{{border-collapse:collapse;width:100%}} td,th{{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left}}
</style></head><body><h1>SPE {rnd}: IQM agent eval</h1>
<p>{out['counts']['COMPLETE']} complete trials. Estimated real-QPU credits: {out['credits_estimated_total']}.</p>
<h2>pass@1 on T1 to T5, with 95% Wilson interval</h2>
<svg viewBox="0 0 520 260" width="100%" role="img" aria-label="pass at 1 by config">{''.join(bars)}<line x1="40" x2="500" y1="230" y2="230" stroke="var(--line)"/></svg>
<h2>Per config</h2><table><tr><th>Config</th><th>pass@1</th><th>pass^3 cells</th><th>T6</th><th>Tool calls</th><th>Total tokens</th><th>Wall min</th></tr>{table}</table>
<p>Source: {html.escape(rnd)}.json. Tokens and latency only. No dollar cost.</p></body></html>"""
    (res / f"{rnd}-dashboard.html").write_text(page)
    print(json.dumps({"rows": len(rows), "counts": out["counts"], "per_config": {c: {k: v for k, v in p.items() if k not in ("cells", "judge_pass_rate")} for c, p in per_cfg.items()}}, indent=1))


if __name__ == "__main__":
    main()
