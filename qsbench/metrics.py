from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace


def safe_qubit_index(qc: QuantumCircuit, qubit) -> int:
    """Extract the integer index of a Qubit object."""
    try:
        return qc.find_bit(qubit).index
    except Exception:
        try:
            return qubit._index
        except Exception:
            return int(str(qubit).split("q[")[-1].split("]")[0])


def get_adjacency_matrix(qc: QuantumCircuit, n_qubits: int) -> list[list[int]]:
    """Build adjacency matrix from CX gates."""
    adj = np.zeros((n_qubits, n_qubits), dtype=int)

    for instruction in qc.data:
        op = instruction.operation
        if op.name == "cx" and len(instruction.qubits) >= 2:
            q0 = safe_qubit_index(qc, instruction.qubits[0])
            q1 = safe_qubit_index(qc, instruction.qubits[1])
            adj[q0, q1] = 1
            adj[q1, q0] = 1

    return adj.tolist()


def calculate_gate_entropy(qc: QuantumCircuit) -> float:
    """Shannon entropy of gate type distribution."""
    ops = qc.count_ops()
    total = sum(ops.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in ops.values():
        p = count / total
        entropy -= p * math.log2(p)
    return round(float(entropy), 6)


def count_gates(qc: QuantumCircuit) -> dict[str, int]:
    """Count various gate types in the circuit."""
    ops = qc.count_ops()
    total_gates = int(sum(ops.values()))
    single_qubit_gates = int(
        sum(ops.get(g, 0) for g in ["id", "x", "y", "z", "h", "rx", "ry", "rz"])
    )
    two_qubit_gates = int(ops.get("cx", 0))

    return {
        "total_gates": total_gates,
        "single_qubit_gates": single_qubit_gates,
        "two_qubit_gates": two_qubit_gates,
        "cx_count": int(ops.get("cx", 0)),
        "h_count": int(ops.get("h", 0)),
        "rx_count": int(ops.get("rx", 0)),
        "ry_count": int(ops.get("ry", 0)),
        "rz_count": int(ops.get("rz", 0)),
    }


def calculate_meyer_wallach(qc: QuantumCircuit) -> float:
    """
    Compute the Meyer-Wallach entanglement measure.
    Returns -1.0 if computation fails (e.g., too many qubits).
    """
    try:
        if qc.num_qubits > 12:
            return -1.0
        sv = Statevector.from_instruction(qc)
        n = qc.num_qubits
        purities = 0.0
        for i in range(n):
            traced_out = [j for j in range(n) if j != i]
            rho_i = partial_trace(sv, traced_out)
            purities += float(np.real(np.trace(rho_i.data @ rho_i.data)))
        return round(float(2.0 * (1.0 - (purities / n))), 6)
    except Exception:
        return -1.0