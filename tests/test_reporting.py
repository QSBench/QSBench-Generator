import pandas as pd
import pytest
from qsbench.reporting import summarize_dataframe, build_release_changelog, build_data_card


def test_summarize_dataframe():
    df = pd.DataFrame({
        "ideal_expval_Z_global": [0.5, 0.6, -0.1],
        "noisy_expval_Z_global": [0.4, 0.55, -0.05],
        "error_Z_global": [0.1, 0.05, -0.05],
        "circuit_hash": ["a", "b", "c"],
        "circuit_type_resolved": ["hea", "hea", "qft"],
        "split": ["train", "val", "test"],
    })
    summary = summarize_dataframe(df)
    assert summary["rows"] == 3
    assert summary["columns"] == 6
    assert "mean_ideal_expval_Z_global" in summary
    assert "std_ideal_expval_Z_global" in summary
    assert summary["unique_circuits"] == 3
    assert "families" in summary
    assert "splits" in summary


def test_build_release_changelog():
    meta = {"dataset_group": "Core", "dataset_name": "QSBench", "dataset_version": "1.2.3"}
    report = {"rows": 100, "families": {"hea": 60, "qft": 40}, "splits": {"train": 80}}
    coverage = {"circuit_type_resolved": {"hea": 60}, "noise_type": {"depolarizing": 100}}
    changelog = build_release_changelog(meta, report, coverage)
    assert "QSBench CHANGELOG" in changelog
    assert "1.2.3" in changelog
    assert "100 generated rows" in changelog


@pytest.mark.parametrize(
    "noise,noise_prob,noise_params,expected_focus",
    [
        ("none", 0.0, {}, "clean simulation benchmark"),
        ("depolarizing", 0.01, {}, "depolarizing-noise robustness benchmark"),
        ("amplitude_damping", 0.02, {}, "amplitude-damping robustness benchmark"),
        ("phase_damping", 0.03, {}, "phase-damping robustness benchmark"),
        ("thermal_relaxation", 0.01, {"t1": 50e-6, "t2": 30e-6}, "thermal-relaxation robustness benchmark"),
        ("phase_amplitude_damping", 0.01, {}, "phase+amplitude damping robustness benchmark"),
        ("readout", 0.01, {"p0": 0.02, "p1": 0.015}, "readout-error robustness benchmark"),
        ("device", 0.0, {}, "device-like noise robustness benchmark"),
    ],
)
def test_build_data_card_all_noise_types(noise, noise_prob, noise_params, expected_focus):
    card = build_data_card(
        dataset_name="test",
        dataset_version="1.0.0",
        total_rows_written=100,
        n_qubits=4,
        depth=5,
        circuit_type="mixed",
        entanglement="full",
        noise=noise,
        noise_prob=noise_prob,
        observable_bases=["Z"],
        observable_mode="mixed",
        shots=1024,
        use_gpu=False,
        gpu_available=False,
        backend_device="CPU",
        train_frac=0.8,
        val_frac=0.1,
        test_frac=0.1,
        shard_count=2,
        shard_dir_name="shards",
        files=["meta.json"],
        report={"rows": 100},
        coverage={"split": {"train": 80}},
        noise_params=noise_params,
    )
    assert expected_focus in card
    assert "Qubits: 4" in card
    assert "Shards: 2" in card