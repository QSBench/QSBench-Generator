from qiskit import QuantumCircuit

from qsbench.circuit.metrics import (
    calculate_gate_entropy,
    calculate_meyer_wallach,
    count_gates,
    get_adjacency_matrix,
    safe_qubit_index,
)


def test_safe_qubit_index_all_fallbacks(small_circuit):
    qc = small_circuit
    q0 = qc.qubits[0]
    assert safe_qubit_index(qc, q0) == 0

    class DummyQubit:
        _index = 1

    assert safe_qubit_index(qc, DummyQubit()) == 1


def test_get_adjacency_matrix_empty_circuit():
    qc = QuantumCircuit(3)
    adj = get_adjacency_matrix(qc, 3)
    assert adj == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def test_calculate_gate_entropy_empty():
    qc = QuantumCircuit(2)
    assert calculate_gate_entropy(qc) == 0.0


def test_count_gates_various():
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.rx(0.1, 2)
    stats = count_gates(qc)
    assert stats["total_gates"] == 3
    assert stats["single_qubit_gates"] == 2
    assert stats["cx_count"] == 1
    assert stats["rx_count"] == 1


def test_calculate_meyer_wallach_large_and_fail():
    qc = QuantumCircuit(14)
    assert calculate_meyer_wallach(qc) == -1.0

    qc_empty = QuantumCircuit(2)
    assert calculate_meyer_wallach(qc_empty) == 0.0
