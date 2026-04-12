"""Circuit-related functionality."""

from .metrics import (
    calculate_gate_entropy,
    calculate_meyer_wallach,
    count_gates,
    get_adjacency_matrix,
    safe_qubit_index,
)

__all__: list[str] = [
    "calculate_gate_entropy",
    "calculate_meyer_wallach",
    "count_gates",
    "get_adjacency_matrix",
    "safe_qubit_index",
]
