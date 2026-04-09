"""
QSBench v5.1.0 — modular release generator with versioned output folders,
metadata, schema, coverage, manifest, report, changelog, and data card.
"""

from __future__ import annotations

import argparse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSBench v5.1.0")
    parser.add_argument("--n-qubits", type=int, default=14)
    parser.add_argument("--depth", type=int, default=10)
    parser.add_argument("--n-samples", type=int, default=1000)
    parser.add_argument(
        "--circuit-type",
        choices=["random", "hea", "efficient", "real_amplitudes", "qft", "mixed"],
        default="mixed",
    )
    parser.add_argument(
        "--entanglement",
        choices=["linear", "full", "circular", "sca"],
        default="full",
    )
    parser.add_argument(
        "--noise",
        choices=[
            "none",
            "depolarizing",
            "amplitude_damping",
            "phase_damping",
            "thermal_relaxation",
            "phase_amplitude_damping",
            "readout",
            "device",
        ],
        default="none",
    )
    parser.add_argument("--noise-prob", type=float, default=0.01)
    parser.add_argument(
        "--noise-params",
        type=str,
        default="{}",
        help='JSON string with additional noise parameters (e.g. {"t1": 50e-6, "t2": 30e-6, "p0": 0.01})',
    )
    parser.add_argument("--observable", default="Z,X,Y")
    parser.add_argument(
        "--observable-mode",
        choices=["global", "per_qubit", "mixed"],
        default="mixed",
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=4096,
        help="Number of samples for noisy estimation; affects accuracy",
    )
    parser.add_argument("--use-gpu", type=str, default="True")
    parser.add_argument(
        "--output",
        "--output-root",
        dest="output_root",
        type=str,
        default="out",
        help="Root folder where released dataset folders are created",
    )
    parser.add_argument("--dataset-family", type=str, default="QSBench")
    parser.add_argument("--dataset-group", type=str, default="Core")
    parser.add_argument("--dataset-version", type=str, default="1.1.0")
    parser.add_argument(
        "--dataset-name",
        type=str,
        default=None,
        help="Optional explicit release name; overrides family/group/version naming",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=128)
    parser.add_argument("--train-frac", type=float, default=0.80)
    parser.add_argument("--val-frac", type=float, default=0.10)
    parser.add_argument("--test-frac", type=float, default=0.10)
    parser.add_argument("--write-csv", action="store_true", help="Write CSV copies alongside parquet shards")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    from qsbench.generator import DatasetGenerator
    generator = DatasetGenerator(args)
    generator.run()


if __name__ == "__main__":
    main()