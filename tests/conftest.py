import pytest


@pytest.fixture(scope="session")
def small_circuit():
    """A simple 2-qubit circuit for all tests"""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


@pytest.fixture(scope="session")
def n_qubits_small():
    return 2
