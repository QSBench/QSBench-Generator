"""
QSBench — Synthetic Quantum Dataset Generator for QML
Public API
"""

__version__ = "5.3.0"

# Public API
from .exceptions import (
    CircuitGenerationError,
    ExportError,
    InvalidNoiseModel,
    QSBenchError,
    SchemaValidationError,
)
from .generator import DatasetGenerator
from .noise.core import create_noise_model

__all__ = [
    "CircuitGenerationError",
    "DatasetGenerator",
    "ExportError",
    "InvalidNoiseModel",
    "QSBenchError",
    "SchemaValidationError",
    "create_noise_model",
]
