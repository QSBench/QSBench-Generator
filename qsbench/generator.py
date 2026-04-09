from __future__ import annotations

import json
import math
import multiprocessing
import platform
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from .config import parse_arguments
from .estimation import build_observable_specs, make_estimator, run_estimator_batch_v2
from .generation import generate_circuit, transpile_for_dataset
from .metrics import (
    calculate_gate_entropy,
    calculate_meyer_wallach,
    count_gates,
    get_adjacency_matrix,
)
from .noise import create_noise_model
from .reporting import build_data_card, build_release_changelog, summarize_dataframe, update_counter
from .storage import write_parquet_shard
from .utils import (
    NumpyEncoder,
    hash_circuit,
    package_version,
    parse_bool,
    safe_qasm_dump,
    split_name_from_hash,
)

console = Console()


class DatasetGenerator:
    """Main dataset generation orchestrator."""

    def __init__(self, args=None):
        if args is None:
            args = parse_arguments()
        self.args = args
        if not getattr(self.args, "dataset_name", None):
            raise ValueError("--dataset-name is required")
        self.dataset_name = self.args.dataset_name
        self.dataset_version = getattr(self.args, "dataset_version", "v5.2.0")
        self.use_gpu = parse_bool(self.args.use_gpu)
        self._init_simulator()
        if not math.isclose(
            self.args.train_frac + self.args.val_frac + self.args.test_frac,
            1.0,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise ValueError("train_frac + val_frac + test_frac must sum to 1.0")

    def _init_simulator(self):
        """Detect GPU availability and set precision mode."""
        try:
            sim = AerSimulator()
            self.gpu_available = (
                "gpu" in sim.available_devices() or "GPU" in sim.available_devices()
            )
            self.available_devices = sim.available_devices()
        except Exception:
            self.gpu_available = False
            self.available_devices = ["CPU"]
        self.precision_mode = "double"

    def _generate_single_circuit(self, seed: int) -> tuple[str, QuantumCircuit]:
        """Generate a single circuit (used in parallel)."""
        resolved_type, qc = generate_circuit(
            c_type=self.args.circuit_type,
            n_qubits=self.args.n_qubits,
            depth=self.args.depth,
            entanglement=self.args.entanglement,
            seed=seed,
        )
        return resolved_type, qc

    def run(self) -> None:
        """Run the full dataset generation pipeline."""
        if self.args.seed is None:
            self.args.seed = int(np.random.default_rng().integers(0, 2**32 - 1))
        np.random.seed(self.args.seed)

        observable_bases = [
            obs.strip().upper() for obs in self.args.observable.split(",") if obs.strip()
        ]
        noise_str = (
            f"{self.args.noise}({self.args.noise_prob})"
            if self.args.noise != "none"
            else "none(0.0)"
        )

        console.print(f"[bold cyan]🚀 QSBench {self.dataset_version}[/bold cyan]")
        console.print(
            f"Qubits: {self.args.n_qubits} | Depth: {self.args.depth} | Type: {self.args.circuit_type} "
            f"({self.args.entanglement}) | Samples: {self.args.n_samples:,} | Noise: {noise_str} | "
            f"Observable: {self.args.observable} | Mode: {self.args.observable_mode} | "
            f"Shots: {self.args.shots} | Device: {'GPU' if self.use_gpu else 'CPU'}"
        )

        ideal_backend_options = {
            "method": "statevector",
            "device": "GPU" if self.use_gpu else "CPU",
            "precision": self.precision_mode,
        }
        noisy_backend_options = {
            "method": "statevector",
            "device": "GPU" if self.use_gpu else "CPU",
            "precision": self.precision_mode,
        }

        noise_params_dict = {}
        if (
            hasattr(self.args, "noise_params")
            and self.args.noise_params
            and self.args.noise_params != "{}"
        ):
            try:
                noise_params_dict = json.loads(self.args.noise_params)
            except Exception:
                noise_params_dict = {}

        noise_model = create_noise_model(
            self.args.noise,
            self.args.noise_prob,
            noise_params=noise_params_dict,
            n_qubits=self.args.n_qubits,
        )
        if noise_model is not None:
            noisy_backend_options["noise_model"] = noise_model

        ideal_estimator = make_estimator(
            ideal_backend_options, default_precision=0.0, seed=self.args.seed
        )
        noisy_default_precision = (
            0.0 if self.args.shots is None else 1.0 / math.sqrt(self.args.shots)
        )
        noisy_estimator = make_estimator(
            noisy_backend_options,
            default_precision=noisy_default_precision,
            seed=self.args.seed + 99991,
        )

        observable_specs = build_observable_specs(
            self.args.n_qubits, observable_bases, self.args.observable_mode
        )
        paulis = [spec[1] for spec in observable_specs]

        output_root = Path(getattr(self.args, "output_root", "out"))
        release_dir = output_root / self.dataset_name
        shards_dir = release_dir / "shards"
        release_dir.mkdir(parents=True, exist_ok=True)
        shards_dir.mkdir(parents=True, exist_ok=True)

        meta_path = release_dir / "meta.json"
        schema_path = release_dir / "schema.json"
        coverage_path = release_dir / "coverage.json"
        manifest_path = release_dir / "manifest.json"
        report_path = release_dir / "report.json"
        data_card_path = release_dir / "data_card.md"
        changelog_path = release_dir / "CHANGELOG.md"
        log_path = release_dir / "generation_log.json"

        total_rows_written = 0
        shard_manifest: list[dict[str, Any]] = []
        coverage: dict[str, dict[str, int]] = {
            "split": {},
            "circuit_type_resolved": {},
            "circuit_type_requested": {},
            "noise_type": {},
            "entanglement": {},
            "backend_device": {},
            "precision_mode": {},
            "observable_mode": {},
        }
        all_sample_summaries: list[dict[str, Any]] = []

        batch_size = max(1, self.args.shard_size)

        for shard_index, start in enumerate(
            tqdm(range(0, self.args.n_samples, batch_size), desc="Generating dataset")
        ):
            end = min(start + batch_size, self.args.n_samples)
            seeds_i = [self.args.seed + i for i in range(start, end)]

            with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                futures = [executor.submit(self._generate_single_circuit, seed) for seed in seeds_i]
                batch_raw_results = [f.result() for f in futures]

            qc_list_transpiled = []
            batch_meta = []

            for idx, (resolved_type, qc) in enumerate(batch_raw_results):
                seed_i = seeds_i[idx]
                qc_t = transpile_for_dataset(qc, seed=seed_i)
                gate_stats = count_gates(qc_t)
                raw_qasm = safe_qasm_dump(qc)
                transpiled_qasm = safe_qasm_dump(qc_t)
                circuit_signature = transpiled_qasm or raw_qasm or repr(qc_t)
                circuit_hash = hash_circuit(
                    circuit_signature, seed_i, resolved_type, self.args.depth, self.args.n_qubits
                )
                split = split_name_from_hash(circuit_hash, self.args.train_frac, self.args.val_frac)

                meta = {
                    "sample_id": start + idx,
                    "sample_seed": seed_i,
                    "circuit_hash": circuit_hash,
                    "split": split,
                    "circuit_type_resolved": resolved_type,
                    "circuit_type_requested": self.args.circuit_type,
                    "n_qubits": self.args.n_qubits,
                    "depth": self.args.depth,
                    "entanglement": (
                        self.args.entanglement
                        if resolved_type in {"hea", "efficient", "real_amplitudes"}
                        else None
                    ),
                    "qasm_raw": raw_qasm,
                    "qasm_transpiled": transpiled_qasm,
                    "adjacency": get_adjacency_matrix(qc_t, self.args.n_qubits),
                    "gate_entropy": calculate_gate_entropy(qc_t),
                    "meyer_wallach": calculate_meyer_wallach(qc),
                    "noise_type": self.args.noise if self.args.noise != "none" else "none",
                    "noise_prob": self.args.noise_prob if self.args.noise != "none" else 0.0,
                    "observable_bases": self.args.observable,
                    "observable_mode": self.args.observable_mode,
                    "shots": self.args.shots,
                    "gpu_requested": self.use_gpu,
                    "gpu_available": self.gpu_available,
                    "backend_device": "GPU" if self.use_gpu else "CPU",
                    "precision_mode": self.precision_mode,
                    "circuit_signature": circuit_signature,
                }
                meta.update(gate_stats)
                batch_meta.append(meta)
                qc_list_transpiled.append(qc_t)

            ideal_matrix = run_estimator_batch_v2(ideal_estimator, qc_list_transpiled, paulis)
            noisy_matrix = run_estimator_batch_v2(noisy_estimator, qc_list_transpiled, paulis)

            rows = []
            for i, meta in enumerate(batch_meta):
                row = dict(meta)
                for obs_idx, (label, _) in enumerate(observable_specs):
                    ideal = ideal_matrix[i][obs_idx]
                    noisy = noisy_matrix[i][obs_idx]
                    row[f"ideal_expval_{label}"] = round(float(ideal), 8)
                    row[f"noisy_expval_{label}"] = round(float(noisy), 8)
                    row[f"error_{label}"] = round(float(ideal - noisy), 8)
                    row[f"sign_ideal_{label}"] = int(ideal >= 0)
                    row[f"sign_noisy_{label}"] = int(noisy >= 0)
                rows.append(row)

            # Collect statistics for report
            for row in rows:
                summary_entry = {
                    "sample_id": row["sample_id"],
                    "split": row["split"],
                    "circuit_hash": row["circuit_hash"],
                    "circuit_type_resolved": row["circuit_type_resolved"],
                    "noise_type": row["noise_type"],
                    "meyer_wallach": row["meyer_wallach"],
                    "gate_entropy": row["gate_entropy"],
                }
                if "ideal_expval_Z_global" in row:
                    summary_entry["ideal_expval_Z_global"] = row["ideal_expval_Z_global"]
                    summary_entry["noisy_expval_Z_global"] = row["noisy_expval_Z_global"]
                all_sample_summaries.append(summary_entry)

                update_counter(coverage, "split", row["split"])
                update_counter(coverage, "circuit_type_resolved", row["circuit_type_resolved"])
                update_counter(coverage, "circuit_type_requested", row["circuit_type_requested"])
                update_counter(coverage, "noise_type", row["noise_type"])
                update_counter(coverage, "entanglement", str(row.get("entanglement")))
                update_counter(coverage, "backend_device", row["backend_device"])
                update_counter(coverage, "precision_mode", row["precision_mode"])
                update_counter(coverage, "observable_mode", row["observable_mode"])

            shard_df = pd.DataFrame(rows)
            shard_name = f"{self.dataset_name}_shard{shard_index:05d}.parquet"
            shard_path = shards_dir / shard_name
            shard_info = write_parquet_shard(
                shard_df, shard_path, write_csv=bool(self.args.write_csv)
            )
            shard_info.update(
                {"shard_index": shard_index, "start": start, "end": start + len(rows)}
            )
            shard_manifest.append(shard_info)
            total_rows_written += len(shard_df)

        df_preview = pd.DataFrame(all_sample_summaries)

        report: dict[str, Any] = (
            summarize_dataframe(df_preview) if not df_preview.empty else {"rows": 0}
        )
        report["dataset_version"] = self.dataset_version
        report["shards"] = len(shard_manifest)
        report["total_rows_written"] = total_rows_written
        report["coverage"] = coverage

        meta = {
            "generator_version": "v5.2.0",
            "dataset_version": self.dataset_version,
            "parameters": {
                "n_qubits": self.args.n_qubits,
                "depth": self.args.depth,
                "n_samples": self.args.n_samples,
                "circuit_type": self.args.circuit_type,
                "entanglement": self.args.entanglement,
                "noise": self.args.noise,
                "noise_prob": self.args.noise_prob,
                "noise_params": noise_params_dict,
                "observable": self.args.observable,
                "observable_mode": self.args.observable_mode,
                "shots": self.args.shots,
                "use_gpu": self.use_gpu,
                "seed": self.args.seed,
                "output_root": str(output_root),
                "shard_size": self.args.shard_size,
                "train_frac": self.args.train_frac,
                "val_frac": self.args.val_frac,
                "test_frac": self.args.test_frac,
                "write_csv": self.args.write_csv,
            },
            "seed": self.args.seed,
            "num_samples": int(total_rows_written),
            "observables": observable_bases,
            "observable_mode": self.args.observable_mode,
            "gpu_available": self.gpu_available,
            "gpu_requested": self.use_gpu,
            "backend_device": "GPU" if self.use_gpu else "CPU",
            "precision_mode": self.precision_mode,
            "available_devices": self.available_devices,
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "qiskit": package_version("qiskit"),
                "qiskit-aer": package_version("qiskit-aer"),
                "numpy": package_version("numpy"),
                "pandas": package_version("pandas"),
                "tqdm": package_version("tqdm"),
                "rich": package_version("rich"),
            },
            "generated_at": pd.Timestamp.now().isoformat(),
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        schema = {
            "dataset_version": self.dataset_version,
            "core_columns": [
                "sample_id",
                "sample_seed",
                "circuit_hash",
                "split",
                "circuit_type_resolved",
                "circuit_type_requested",
                "n_qubits",
                "depth",
                "entanglement",
                "qasm_raw",
                "qasm_transpiled",
                "adjacency",
                "gate_entropy",
                "meyer_wallach",
                "noise_type",
                "noise_prob",
                "observable_bases",
                "observable_mode",
                "shots",
                "gpu_requested",
                "gpu_available",
                "backend_device",
                "precision_mode",
                "total_gates",
                "single_qubit_gates",
                "two_qubit_gates",
                "cx_count",
                "h_count",
                "rx_count",
                "ry_count",
                "rz_count",
            ],
            "label_prefixes": [
                "ideal_expval_",
                "noisy_expval_",
                "error_",
                "sign_ideal_",
                "sign_noisy_",
            ],
            "observable_mode": self.args.observable_mode,
            "observable_bases": observable_bases,
            "gate_basis": ["id", "x", "y", "z", "h", "rx", "ry", "rz", "cx"],
            "split_strategy": {
                "type": "hash_mod",
                "train_frac": self.args.train_frac,
                "val_frac": self.args.val_frac,
                "test_frac": self.args.test_frac,
            },
        }

        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        report = summarize_dataframe(df_preview) if not df_preview.empty else {"rows": 0}
        report["dataset_version"] = self.dataset_version
        report["shards"] = len(shard_manifest)
        report["total_rows_written"] = total_rows_written
        report["coverage"] = coverage

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        with open(coverage_path, "w", encoding="utf-8") as f:
            json.dump(coverage, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "release_dir": str(release_dir),
                    "shards_dir": str(shards_dir),
                    "shards": shard_manifest,
                },
                f,
                indent=2,
                ensure_ascii=False,
                cls=NumpyEncoder,
            )

        changelog = build_release_changelog(meta, report, coverage)
        changelog_path.write_text(changelog, encoding="utf-8")

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "status": "success",
                    "num_samples": total_rows_written,
                    "num_shards": len(shard_manifest),
                    "backend_device": "GPU" if self.use_gpu else "CPU",
                    "gpu_available": self.gpu_available,
                    "gpu_requested": self.use_gpu,
                    "dataset_version": self.dataset_version,
                },
                f,
                indent=2,
                ensure_ascii=False,
                cls=NumpyEncoder,
            )

        data_card = build_data_card(
            dataset_name=self.dataset_name,
            dataset_version=self.dataset_version,
            total_rows_written=total_rows_written,
            n_qubits=self.args.n_qubits,
            depth=self.args.depth,
            circuit_type=self.args.circuit_type,
            entanglement=self.args.entanglement,
            noise=self.args.noise,
            noise_prob=self.args.noise_prob if self.args.noise != "none" else 0.0,
            observable_bases=observable_bases,
            observable_mode=self.args.observable_mode,
            shots=self.args.shots,
            use_gpu=self.use_gpu,
            gpu_available=self.gpu_available,
            backend_device="GPU" if self.use_gpu else "CPU",
            train_frac=self.args.train_frac,
            val_frac=self.args.val_frac,
            test_frac=self.args.test_frac,
            shard_count=len(shard_manifest),
            shard_dir_name=shards_dir.name,
            files=[
                meta_path.name,
                schema_path.name,
                coverage_path.name,
                manifest_path.name,
                report_path.name,
                data_card_path.name,
                changelog_path.name,
                log_path.name,
            ],
            report=report,
            coverage=coverage,
            noise_params=noise_params_dict,
        )
        data_card_path.write_text(data_card, encoding="utf-8")

        console.print(
            f"[bold green]✅ Dataset successfully created: {total_rows_written:,} rows[/bold green]"
        )
        table = Table(title="✅ Dataset successfully created")
        table.add_column("File", style="cyan")
        table.add_column("Rows", style="green")
        table.add_row(str(meta_path), "1")
        table.add_row(str(schema_path), "1")
        table.add_row(str(coverage_path), "1")
        table.add_row(str(manifest_path), "1")
        table.add_row(str(report_path), "1")
        table.add_row(str(data_card_path), "1")
        table.add_row(str(changelog_path), "1")
        table.add_row(str(log_path), "1")
        table.add_row(str(shards_dir), f"{len(shard_manifest)} shards")
        table.add_row("Rows", f"{total_rows_written:,}")
        console.print(table)

        console.print(f"[bold green]Metadata:[/bold green] {meta_path}")
        console.print(f"[bold green]Schema:[/bold green] {schema_path}")
        console.print(f"[bold green]Coverage:[/bold green] {coverage_path}")
        console.print(f"[bold green]Manifest:[/bold green] {manifest_path}")
        console.print(f"[bold green]Data card:[/bold green] {data_card_path}")
        console.print(f"[bold green]Changelog:[/bold green] {changelog_path}")


if __name__ == "__main__":
    DatasetGenerator().run()
