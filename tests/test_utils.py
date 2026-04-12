import json

import numpy as np

from qsbench.utils import (
    NumpyEncoder,
    build_dataset_name,
    hash_circuit,
    parse_bool,
    sanitize_slug,
    split_name_from_hash,
)


def test_sanitize_slug_edge_cases():
    assert sanitize_slug("") == "dataset"
    assert sanitize_slug("   My  Dataset!!!   ") == "My-Dataset"
    assert sanitize_slug("invalid@#$%^&*name") == "invalid-name"


def test_build_dataset_name_custom_and_version():
    name = build_dataset_name("QSBench", "Core", "1.2.3", "my-custom-name")
    assert name == "my-custom-name"

    default_name = build_dataset_name("QSBench", "Core", "1.2.3")
    assert default_name.startswith("QSBench-Core-v1.2.3")


def test_hash_circuit_and_split_deterministic():
    h = hash_circuit("sig", 42, "hea", 10, 8)
    assert len(h) == 16 and h.isalnum()

    split = split_name_from_hash(h, 0.8, 0.1)
    assert split in {"train", "val", "test"}


def test_parse_bool_all_variants():
    true_values = ["1", "true", "yes", "y", "on", "True", "YES"]
    false_values = ["0", "false", "no", "n", "off", "False", "NO", ""]
    for v in true_values:
        assert parse_bool(v) is True
    for v in false_values:
        assert parse_bool(v) is False


def test_numpy_encoder():
    data = {"int": np.int64(42), "float": np.float64(3.14), "array": np.array([1, 2, 3])}
    encoded = json.dumps(data, cls=NumpyEncoder)
    loaded = json.loads(encoded)
    assert loaded["int"] == 42
    assert loaded["float"] == 3.14
    assert loaded["array"] == [1, 2, 3]
