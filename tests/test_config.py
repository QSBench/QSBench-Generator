import sys
from unittest.mock import patch

from qsbench.config import parse_arguments


def test_parse_arguments_defaults():
    with patch.object(sys, "argv", ["qsbench"]):
        args = parse_arguments()
        assert args.n_qubits == 14
        assert args.depth == 10
        assert args.n_samples == 1000
        assert args.circuit_type == "mixed"
        assert args.noise == "none"


def test_parse_arguments_custom_values():
    with patch.object(sys, "argv", [
        "qsbench",
        "--n-qubits", "6",
        "--depth", "4",
        "--n-samples", "32",
        "--circuit-type", "hea",
        "--noise", "thermal_relaxation",
        "--noise-prob", "0.02",
        "--observable", "X,Y",
        "--observable-mode", "per_qubit",
        "--shots", "2048",
        "--use-gpu", "False",
        "--dataset-name", "test_config",
    ]):
        args = parse_arguments()
        assert args.n_qubits == 6
        assert args.circuit_type == "hea"
        assert args.noise == "thermal_relaxation"
        assert args.observable_mode == "per_qubit"
        assert args.dataset_name == "test_config"


def test_parse_arguments_main_call():
    """if __name__ == "__main__" in config.py without running the actual generator"""
    with patch("qsbench.generator.DatasetGenerator") as mock_gen:
        with patch.object(sys, "argv", ["qsbench"]):
            from qsbench.config import main
            main()
            mock_gen.assert_called_once()