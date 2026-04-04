"""Utility functions for hashing, naming, serialization, and path handling."""

from __future__ import annotations

import hashlib
import json
import re
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Tuple

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder for NumPy types."""

    def default(self, obj: Any):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def package_version(name: str) -> str:
    """Return the installed version of a package."""
    try:
        return importlib_metadata.version(name)
    except Exception:
        return "unknown"


def parse_bool(value: str) -> bool:
    """Convert a string to a boolean (case-insensitive)."""
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def sanitize_slug(value: str) -> str:
    """Convert a string to a safe filesystem slug."""
    value = str(value).strip()
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-._") or "dataset"


def build_dataset_name(
    dataset_family: str,
    dataset_group: str,
    dataset_version: str,
    dataset_name: str | None = None,
) -> str:
    """Construct a dataset release name from components."""
    if dataset_name and str(dataset_name).strip():
        return sanitize_slug(dataset_name)

    family = sanitize_slug(dataset_family)
    group = sanitize_slug(dataset_group)
    version = sanitize_slug(dataset_version)
    if not version.startswith("v"):
        version = f"v{version}"
    return f"{family}-{group}-{version}"


def build_release_paths(output_root: str | Path, dataset_name: str) -> Tuple[Path, Path]:
    """Return (release_dir, shards_dir) paths."""
    root = Path(output_root)
    release_dir = root / "releases" / dataset_name
    shards_dir = release_dir / "shards"
    return release_dir, shards_dir


def hash_circuit(
    circuit_signature: str, seed: int, circuit_type: str, depth: int, n_qubits: int
) -> str:
    """Generate a short SHA-256 hash of circuit parameters."""
    payload = f"{n_qubits}|{depth}|{circuit_type}|{seed}|{circuit_signature}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def split_name_from_hash(circuit_hash: str, train_frac: float, val_frac: float) -> str:
    """Assign a deterministic split based on hash prefix."""
    bucket = int(circuit_hash[:8], 16) % 1000
    train_cut = int(train_frac * 1000)
    val_cut = int((train_frac + val_frac) * 1000)
    if bucket < train_cut:
        return "train"
    if bucket < val_cut:
        return "val"
    return "test"


def safe_qasm_dump(qc) -> str | None:
    """Dump circuit to QASM string, return None on failure."""
    from qiskit import qasm2

    try:
        return qasm2.dumps(qc)
    except Exception:
        return None