import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from qsbench.config import parse_arguments
from qsbench.generator import DatasetGenerator


def test_dataset_generator_small_run():
    """End-to-end test"""
    with tempfile.TemporaryDirectory() as tmp:
        args = parse_arguments()
        args.n_qubits = 4
        args.depth = 3
        args.n_samples = 16
        args.circuit_type = "mixed"
        args.entanglement = "full"
        args.noise = "depolarizing"
        args.noise_prob = 0.01
        args.observable = "Z"
        args.observable_mode = "global"
        args.shots = 1024
        args.use_gpu = "False"
        args.output_root = tmp
        args.dataset_name = "test_small_run"
        args.seed = 42
        args.shard_size = 8
        args.train_frac = 0.8
        args.val_frac = 0.1
        args.test_frac = 0.1
        args.write_csv = True

        generator = DatasetGenerator(args)
        generator.run()

        release_dir = Path(tmp) / "test_small_run"
        assert release_dir.exists()
        shards = list((release_dir / "shards").glob("*.parquet"))
        total_rows = sum(pd.read_parquet(p).shape[0] for p in shards)
        assert total_rows == 16


def test_generator_init_simulator_exception_coverage():
    """Covering the _init_simulator except block"""
    with patch("qsbench.generator.AerSimulator") as mock_aer:
        mock_aer.side_effect = Exception("Sim failed")
        args = parse_arguments()
        args.use_gpu = "True"
        args.dataset_name = "test_exception"
        gen = DatasetGenerator(args)
        assert gen.gpu_available is False
        assert gen.available_devices == ["CPU"]