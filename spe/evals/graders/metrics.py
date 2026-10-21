"""Transcript metrics for one Claude Code subagent trial.

Usage:
  metrics.py --trial-id r01-C-T1-1      find the trial transcript by its "TRIAL-ID: <id>" marker and measure it
  metrics.py --transcript PATH          measure a given agent-<id>.jsonl

Output: one JSON object with tokens, tool calls, tool errors, wall time, tools used, and peek flags.
"""
import argparse
import collections
import json
import sys
from datetime import datetime
from pathlib import Path

SESSIONS = Path.home() / ".claude/projects/-Users-claytonchancey-Desktop-quantum"
PEEK = ("spe/evals", "spe/predictions", "spe/prediction-log", "spe/failures", "spe/spec")


def find(trial_id):
    marker = f"TRIAL-ID: {trial_id}\n"
    hits = []
    for p in SESSIONS.glob("*/subagents/workflows/*/agent-*.jsonl"):
        with p.open() as f:
            for i, line in enumerate(f):
                if i > 3:
                    break
                if marker in line or marker.replace("\n", "\\n") in line:
                    hits.append(p)
                    break
    return sorted(hits, key=lambda p: p.stat().st_mtime)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def measure(path):
    usage, seen = collections.Counter(), set()
    tools, errors, peeks, times = collections.Counter(), 0, [], []
    bash_cmds, files_read = [], []
    model = None
    for line in path.open():
        o = json.loads(line)
        if o.get("timestamp"):
            times.append(ts(o["timestamp"]))
        m = o.get("message")
        if not isinstance(m, dict):
            continue
        if o.get("type") == "assistant":
            model = m.get("model") or model
            mid = m.get("id") or o.get("requestId")
            if m.get("usage") and mid not in seen:
                seen.add(mid)
                u = m["usage"]
                for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                    usage[k] += u.get(k) or 0
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools[b["name"]] += 1
                    inp = json.dumps(b.get("input", {}))
                    if b["name"] == "Bash":
                        bash_cmds.append(b["input"].get("command", "")[:300])
                    if b["name"] == "Read":
                        files_read.append(b["input"].get("file_path", ""))
                    if any(k in inp for k in PEEK):
                        peeks.append(inp[:200])
        if o.get("type") == "user":
            for b in m.get("content") if isinstance(m.get("content"), list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                    errors += 1
    total = sum(usage.values())
    return {
        "transcript": str(path),
        "model": model,
        "wall_seconds": round((max(times) - min(times)).total_seconds(), 1) if times else None,
        "api_calls": len(seen),
        "tokens": {**usage, "total": total},
        "tool_calls": sum(tools.values()),
        "tool_errors": errors,
        "tools": dict(tools),
        "used_helper": any("iqm_run.py" in c for c in bash_cmds),
        "read_docs": sorted({f for f in files_read if "/docs/" in f} | {c for c in bash_cmds if "docs/iqm" in c and "cat " in c}),
        "peeked": bool(peeks),
        "peek_evidence": peeks[:5],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--trial-id")
    p.add_argument("--transcript")
    a = p.parse_args()
    if a.transcript:
        path = Path(a.transcript)
    else:
        hits = find(a.trial_id)
        if not hits:
            print(json.dumps({"trial_id": a.trial_id, "error": "transcript not found"}))
            sys.exit(1)
        path = hits[-1]
    r = measure(path)
    r["trial_id"] = a.trial_id
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
