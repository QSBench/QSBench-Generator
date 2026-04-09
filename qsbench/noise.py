from __future__ import annotations

from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    amplitude_damping_error,
    depolarizing_error,
    phase_amplitude_damping_error,
    phase_damping_error,
    thermal_relaxation_error,
)


def create_noise_model(
    noise_type: str,
    prob: float,
    noise_params: dict | None = None,
    n_qubits: int | None = None,
) -> NoiseModel | None:
    """
    Create a noise model for quantum circuit simulation.

    Returns None if noise_type is 'none' or prob <= 0.
    For 'device' returns a GenericBackendV2 noise model.
    """
    if noise_type == "none" or prob <= 0.0:
        return None

    if noise_params is None:
        noise_params = {}

    p1 = min(max(prob, 0.0), 0.999999)
    p2 = min(max(prob * 1.5, 0.0), 0.999999)
    nm = NoiseModel()

    if noise_type == "depolarizing":
        error1 = depolarizing_error(p1, 1)
        error2 = depolarizing_error(p2, 2)
        nm.add_all_qubit_quantum_error(error1, ["id", "h", "rx", "ry", "rz", "x", "y", "z"])
        nm.add_all_qubit_quantum_error(error2, ["cx"])

    elif noise_type == "amplitude_damping":
        error1 = amplitude_damping_error(p1)
        nm.add_all_qubit_quantum_error(error1, ["id", "h", "rx", "ry", "rz", "x", "y", "z"])

    elif noise_type == "phase_damping":
        error1 = phase_damping_error(p1)
        nm.add_all_qubit_quantum_error(error1, ["id", "h", "rx", "ry", "rz", "x", "y", "z"])

    elif noise_type == "thermal_relaxation":
        t1 = noise_params.get("t1", 50e-6)
        t2 = noise_params.get("t2", 30e-6)
        gate_time_1q = noise_params.get("gate_time_1q", 3.5e-8)
        error1 = thermal_relaxation_error(t1, t2, gate_time_1q)
        nm.add_all_qubit_quantum_error(error1, ["id", "h", "rx", "ry", "rz", "x", "y", "z"])

    elif noise_type == "phase_amplitude_damping":
        p_amp = noise_params.get("p_amp", p1)
        p_phase = noise_params.get("p_phase", p1)
        error1 = phase_amplitude_damping_error(p_amp, p_phase)
        nm.add_all_qubit_quantum_error(error1, ["id", "h", "rx", "ry", "rz", "x", "y", "z"])

    elif noise_type == "readout":
        p0 = noise_params.get("p0", prob)
        p1_readout = noise_params.get("p1", prob)
        readout_error = ReadoutError([[1 - p0, p0], [p1_readout, 1 - p1_readout]])
        nm.add_all_qubit_readout_error(readout_error)

    elif noise_type == "device":
        if n_qubits is None:
            n_qubits = 14
        backend = GenericBackendV2(num_qubits=n_qubits)
        try:
            nm = backend.noise_model
        except AttributeError:
            nm = NoiseModel.from_backend(backend)
        return nm

    else:
        raise ValueError(f"Unknown noise_type: {noise_type}")

    return nm
