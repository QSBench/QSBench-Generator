import pytest

from qsbench.noise import create_noise_model


@pytest.mark.parametrize(
    "noise_type,prob,extra_params,expected_none",
    [
        ("none", 0.01, {}, True),
        ("depolarizing", 0.0, {}, True),
        ("depolarizing", 0.01, {}, False),
        ("amplitude_damping", 0.05, {}, False),
        ("phase_damping", 0.03, {}, False),
        ("thermal_relaxation", 0.01, {"t1": 50e-6, "t2": 30e-6}, False),
        ("phase_amplitude_damping", 0.02, {"p_amp": 0.01, "p_phase": 0.015}, False),
        ("readout", 0.01, {"p0": 0.02, "p1": 0.015}, False),
        ("device", 0.0, {}, True),      # ← исправлено: prob=0 → None (как в noise.py)
        ("device", 0.01, {"n_qubits": 6}, False),
    ],
)
def test_create_noise_model_all_types(noise_type, prob, extra_params, expected_none):
    nm = create_noise_model(noise_type, prob, extra_params, n_qubits=4)
    if expected_none:
        assert nm is None
    else:
        assert nm is not None
        assert hasattr(nm, "noise_instructions") or hasattr(nm, "to_dict")


def test_create_noise_model_invalid_type():
    with pytest.raises(ValueError, match="Unknown noise_type"):
        create_noise_model("unknown_noise", 0.1)