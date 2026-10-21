"""Free check: authenticate to IBM Quantum Platform and list visible QPUs. Submits no jobs."""
import os
from pathlib import Path

from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

token = os.environ.get("QISKIT_IBM_TOKEN")
instance = os.environ.get("QISKIT_IBM_INSTANCE")
if not token or not instance:
    raise SystemExit("Set QISKIT_IBM_TOKEN and QISKIT_IBM_INSTANCE in .env first.")

service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
print("Authenticated. Backends visible to this instance:")
for b in service.backends():
    status = b.status()
    print(f"  {b.name:20} qubits={b.num_qubits:4} operational={status.operational} pending_jobs={status.pending_jobs}")
print("Least busy:", service.least_busy(operational=True, simulator=False).name)
