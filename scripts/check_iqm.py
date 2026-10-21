"""Free check: reach IQM Resonance and list the QPUs this token can see. Submits no jobs."""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
BASE = "https://resonance.iqm.tech"

about = requests.get(f"{BASE}/about", timeout=30)
about.raise_for_status()
print("Server reachable. Version:", about.json().get("server_version"))

token = os.environ.get("IQM_TOKEN")
if not token:
    raise SystemExit("Set IQM_TOKEN in .env to check the token.")

r = requests.get(
    f"{BASE}/api/v1/quantum-computers",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    timeout=30,
)
if r.status_code == 401:
    raise SystemExit(f"Token rejected: {r.text[:300]}")
r.raise_for_status()
print("Token accepted. Quantum computers:")
for qc in r.json()["quantum_computers"]:
    print(f"  {qc['alias']:12} {qc['display_name']}")
