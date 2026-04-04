from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli
from qiskit_aer.primitives import EstimatorV2


def build_pauli_string(base: str, n_qubits: int, target_qubit: int | None = None) -> str:
    """Build a Pauli string of length n_qubits."""
    base = base.upper()
    if target_qubit is None:
        return base * n_qubits
    chars = ["I"] * n_qubits
    chars[target_qubit] = base
    return "".join(chars)


def build_observable_specs(
    n_qubits: int,
    observables: Sequence[str],
    observable_mode: str,
) -> List[Tuple[str, Pauli]]:
    """Create (label, Pauli) pairs for global and/or per-qubit observables."""
    specs = []
    for obs in observables:
        obs = obs.strip().upper()
        if not obs:
            continue

        if observable_mode in {"global", "mixed"}:
            specs.append(
                (f"{obs}_global", Pauli(build_pauli_string(obs, n_qubits)))
            )

        if observable_mode in {"per_qubit", "mixed"}:
            for q in range(n_qubits):
                specs.append(
                    (f"{obs}_q{q}", Pauli(build_pauli_string(obs, n_qubits, target_qubit=q)))
                )

    return specs


def make_estimator(
    backend_options: Dict[str, Any],
    default_precision: float,
    seed: int | None = None,
) -> EstimatorV2:
    """Create an EstimatorV2 with optional reproducibility seed."""
    # Avoid mutating the original dict
    opts = dict(backend_options)
    if seed is not None:
        opts["seed_simulator"] = int(seed)

    return EstimatorV2(
        options={
            "backend_options": opts,
            "default_precision": default_precision,
        }
    )


def run_estimator_batch_v2(
    estimator: EstimatorV2,
    circuits: List[QuantumCircuit],
    observables: List[Pauli],
) -> np.ndarray:
    """
    Run batch of circuits with the same observables.
    Returns an array of shape (n_circuits, n_observables).
    """
    pubs = [(qc, observables) for qc in circuits]
    job = estimator.run(pubs)
    result = job.result()
    all_evs = [pub_result.data.evs for pub_result in result]
    return np.array(all_evs)