# qsbench/exceptions.py
"""Custom exceptions for QSBench."""


class QSBenchError(Exception):
    """Base exception for all QSBench errors."""

    pass


class InvalidNoiseModel(QSBenchError):
    """Raised when an unknown or invalid noise model is specified."""

    pass


class SchemaValidationError(QSBenchError):
    """Raised when schema validation fails."""

    pass


class ExportError(QSBenchError):
    """Raised when export (Parquet, HDF5, etc.) fails."""

    pass


class CircuitGenerationError(QSBenchError):
    """Raised when circuit generation fails."""

    pass
