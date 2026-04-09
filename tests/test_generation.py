from qiskit import QuantumCircuit

from qsbench.generation import (
    generate_circuit,
    generate_hea_circuit,
    generate_qft_circuit,
    generate_random_circuit,
    generate_real_amplitudes_circuit,
    transpile_for_dataset,
)


def test_generate_random_circuit():
    qc = generate_random_circuit(3, 4, seed=42)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 3


def test_generate_qft_circuit():
    qc = generate_qft_circuit(4, seed=42)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 4


def test_generate_hea_circuit():
    qc = generate_hea_circuit(3, 6, "full", seed=42)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 3


def test_generate_real_amplitudes_circuit():
    qc = generate_real_amplitudes_circuit(3, 6, "linear", seed=42)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 3


def test_generate_circuit_mixed():
    resolved, qc = generate_circuit("mixed", 2, 4, "full", seed=42)
    assert resolved in {"hea", "efficient", "real_amplitudes", "qft", "random"}
    assert isinstance(qc, QuantumCircuit)


def test_transpile_for_dataset(small_circuit):
    qc = transpile_for_dataset(small_circuit, seed=42)
    assert isinstance(qc, QuantumCircuit)
    # basis gates from generation.py
    assert qc.num_qubits == small_circuit.num_qubits