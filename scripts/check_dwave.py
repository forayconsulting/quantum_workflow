"""Free check: run a local D-Wave sampler, list regions, and try the token if one is set. Submits no QPU problems."""
import os
from pathlib import Path

import dimod
from dotenv import load_dotenv
from dwave.cloud import Client
from dwave.cloud.exceptions import SolverAuthenticationError
from dwave.system import EmbeddingComposite
from dwave.system.testing import MockDWaveSampler

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

bqm = dimod.BinaryQuadraticModel({"a": -1, "b": -1}, {("a", "b"): 2}, 0, "BINARY")
print("Local exact solver:", dimod.ExactSolver().sample(bqm).first)
print("Mock QPU sample:", EmbeddingComposite(MockDWaveSampler()).sample(bqm, num_reads=10).first)

if not os.environ.get("DWAVE_API_TOKEN"):
    raise SystemExit("No DWAVE_API_TOKEN set. Local tools work. Leap access needs a LaunchPad or paid token.")

try:
    with Client.from_config() as client:
        print("Token accepted. Solvers:")
        for s in client.get_solvers():
            print("  ", s.name)
except SolverAuthenticationError as e:
    raise SystemExit(f"Token rejected: {e}")
