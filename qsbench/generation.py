from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT, RealAmplitudes, efficient_su2
from qiskit.circuit.random import random_circuit

BASIS_GATES = ["id", "x", "y", "z", "h", "rx", "ry", "rz", "cx"]


def generate_random_circuit(n_qubits: int, depth: int, seed: int | None = None) -> QuantumCircuit:
    """Generate a random circuit with up to 2-qubit gates."""
    return random_circuit(n_qubits, depth, max_operands=2, seed=seed)


def generate_qft_circuit(n_qubits: int, seed: int | None = None) -> QuantumCircuit:
    """Generate a QFT circuit with random initial rotations."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_qubits, name="qft_mix")
    for i in range(n_qubits):
        qc.rx(rng.uniform(-np.pi, np.pi), i)
        qc.rz(rng.uniform(-np.pi, np.pi), i)
    qc.compose(QFT(num_qubits=n_qubits, do_swaps=False), inplace=True)
    return qc


def generate_hea_circuit(
    n_qubits: int, depth: int, entanglement: str, seed: int | None = None
) -> QuantumCircuit:
    """Generate an efficient SU2 circuit with random parameters."""
    rng = np.random.default_rng(seed)
    reps = max(1, depth // 2)
    qc = efficient_su2(num_qubits=n_qubits, reps=reps, entanglement=entanglement)
    return qc.assign_parameters(rng.uniform(-np.pi, np.pi, qc.num_parameters))


def generate_real_amplitudes_circuit(
    n_qubits: int, depth: int, entanglement: str, seed: int | None = None
) -> QuantumCircuit:
    """Generate a RealAmplitudes circuit with random parameters."""
    rng = np.random.default_rng(seed)
    reps = max(1, depth // 2)
    qc = RealAmplitudes(num_qubits=n_qubits, reps=reps, entanglement=entanglement)
    return qc.assign_parameters(rng.uniform(-np.pi, np.pi, qc.num_parameters))


def generate_circuit(
    c_type: str, n_qubits: int, depth: int, entanglement: str, seed: int
) -> tuple[str, QuantumCircuit]:
    """Generate a circuit of the specified type, handling 'mixed' by random choice."""
    rng = np.random.default_rng(seed)
    if c_type == "mixed":
        pool = ["hea", "efficient", "real_amplitudes", "qft", "random"]
        c_type = pool[int(rng.integers(0, len(pool)))]

    if c_type == "random":
        return c_type, generate_random_circuit(n_qubits, depth, seed=seed)
    if c_type in {"hea", "efficient"}:
        return c_type, generate_hea_circuit(n_qubits, depth, entanglement, seed=seed)
    if c_type == "real_amplitudes":
        return c_type, generate_real_amplitudes_circuit(n_qubits, depth, entanglement, seed=seed)
    if c_type == "qft":
        return c_type, generate_qft_circuit(n_qubits, seed=seed)
    raise ValueError(f"Unsupported circuit_type: {c_type}")


def transpile_for_dataset(qc: QuantumCircuit, seed: int | None = None) -> QuantumCircuit:
    """Transpile circuit to basis gates with fixed seed for reproducibility."""
    return transpile(qc, basis_gates=BASIS_GATES, optimization_level=1, seed_transpiler=seed)
