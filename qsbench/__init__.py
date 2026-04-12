"""
QSBench — Synthetic Quantum Dataset Generator for QML Research
Public API
"""

__version__ = "5.3.0"

# Core functionality
# Circuit metrics (convenience import)
from .circuit.metrics import (
    calculate_gate_entropy,
    calculate_meyer_wallach,
    count_gates,
    get_adjacency_matrix,
)

# Exceptions
from .exceptions import (
    CircuitGenerationError,
    ExportError,
    InvalidNoiseModel,
    QSBenchError,
    SchemaValidationError,
)
from .generator import DatasetGenerator

# Noise models
from .noise.core import NOISE_MODELS, create_noise_model

# Storage
from .storage.parquet import write_parquet_shard

__all__ = [
    "NOISE_MODELS",
    "CircuitGenerationError",
    "DatasetGenerator",
    "ExportError",
    "InvalidNoiseModel",
    "QSBenchError",
    "SchemaValidationError",
    "calculate_gate_entropy",
    "calculate_meyer_wallach",
    "count_gates",
    "create_noise_model",
    "get_adjacency_matrix",
    "write_parquet_shard",
]
