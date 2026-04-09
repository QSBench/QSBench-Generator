from qsbench.estimation import (
    build_pauli_string,
    build_observable_specs,
    make_estimator,
    run_estimator_batch_v2,
)
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli
from qiskit_aer.primitives import EstimatorV2


def test_build_pauli_string():
    assert build_pauli_string("X", 3) == "XXX"
    assert build_pauli_string("Z", 4, None) == "ZZZZ"
    assert build_pauli_string("Y", 3, 1) == "IYI"
    assert build_pauli_string("I", 2, 0) == "II"


def test_build_observable_specs():
    specs = build_observable_specs(2, ["Z", "X"], "mixed")
    assert len(specs) == 6  # 2 global + 4 per-qubit
    labels = [label for label, _ in specs]
    assert "Z_global" in labels
    assert "X_global" in labels
    assert "Z_q0" in labels
    assert "Z_q1" in labels
    assert "X_q0" in labels
    assert "X_q1" in labels

    # only global
    specs_global = build_observable_specs(2, ["Z"], "global")
    assert len(specs_global) == 1


def test_make_estimator():
    opts = {"method": "statevector", "device": "CPU"}
    estimator = make_estimator(opts, default_precision=0.0, seed=42)
    assert isinstance(estimator, EstimatorV2)

    backend_options = getattr(estimator.options, "backend_options", {})
    if isinstance(backend_options, dict):
        seed_value = backend_options.get("seed_simulator")
    else:
        seed_value = getattr(backend_options, "seed_simulator", None)

    assert seed_value == 42


def test_run_estimator_batch_v2(small_circuit):
    qc = small_circuit
    estimator = make_estimator(
        {"method": "statevector", "device": "CPU"},
        default_precision=0.0,
        seed=42,
    )
    obs = [Pauli("ZZ")]
    circuits = [qc]
    evs = run_estimator_batch_v2(estimator, circuits, obs)
    assert isinstance(evs, np.ndarray)
    assert evs.shape == (1, 1)
    assert -1.0 <= evs[0, 0] <= 1.0