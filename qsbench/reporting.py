from __future__ import annotations

from typing import Any

import pandas as pd


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Generate summary statistics from a DataFrame."""
    summary: dict[str, Any] = {
        "rows": len(df),
        "columns": len(df.columns),
    }
    for col in ["ideal_expval_Z_global", "noisy_expval_Z_global", "error_Z_global"]:
        if col in df.columns:
            summary[f"mean_{col}"] = float(df[col].mean())
            summary[f"std_{col}"] = float(df[col].std(ddof=0))
    if "circuit_hash" in df.columns:
        summary["unique_circuits"] = int(df["circuit_hash"].nunique())
    if "circuit_type_resolved" in df.columns:
        summary["families"] = df["circuit_type_resolved"].value_counts().to_dict()
    if "split" in df.columns:
        summary["splits"] = df["split"].value_counts().to_dict()
    return summary


def update_counter(
    counter: dict[str, dict[str, int]], key: str, value: str, amount: int = 1
) -> None:
    """Increment a counter for a given key-value pair."""
    if key not in counter:
        counter[key] = {}
    counter[key][value] = counter[key].get(value, 0) + amount


def build_release_changelog(
    meta: dict[str, Any], report: dict[str, Any], coverage: dict[str, dict[str, int]]
) -> str:
    """Create a CHANGELOG.md entry for the release."""
    group = meta.get("dataset_group", "Custom")
    release_name = meta.get("dataset_name", "QSBench")
    version = meta.get("dataset_version", "v1.0.0")
    samples = int(report.get("rows", meta.get("num_samples", 0)))
    families = report.get("families", {})
    splits = report.get("splits", {})
    families_text = (
        ", ".join([f"{k} ({v})" for k, v in sorted(families.items())])
        if families
        else "n/a"
    )
    splits_text = (
        ", ".join([f"{k} ({v})" for k, v in sorted(splits.items())])
        if splits
        else "n/a"
    )
    lines = [
        f"# {release_name} CHANGELOG",
        "",
        f"## {version}",
        "",
        "### Added",
        f"- {samples:,} generated rows.",
        f"- Release group: {group}.",
        f"- Family coverage: {families_text}.",
        f"- Split coverage: {splits_text}.",
        "",
        "### Included",
        f"- Circuit families tracked in the release: {', '.join(sorted(coverage.get('circuit_type_resolved', {}).keys())) or 'n/a'}.",
        f"- Noise regimes: {', '.join(sorted(coverage.get('noise_type', {}).keys())) or 'n/a'}.",
        f"- Observable modes: {', '.join(sorted(coverage.get('observable_mode', {}).keys())) or 'n/a'}.",
        "",
        "### Notes",
        "- This changelog describes the current public release snapshot.",
        "- Future releases should increment the semantic version and keep previous release folders unchanged.",
    ]
    return "\n".join(lines) + "\n"


def build_data_card(
    *,
    dataset_name: str,
    dataset_version: str,
    total_rows_written: int,
    n_qubits: int,
    depth: int,
    circuit_type: str,
    entanglement: str,
    noise: str,
    noise_prob: float,
    observable_bases: list[str],
    observable_mode: str,
    shots: int,
    use_gpu: bool,
    gpu_available: bool,
    backend_device: str,
    train_frac: float,
    val_frac: float,
    test_frac: float,
    shard_count: int,
    shard_dir_name: str,
    files: list[str],
    report: dict[str, Any] | None = None,
    coverage: dict[str, dict[str, int]] | None = None,
    noise_params: dict | None = None,
) -> str:
    """Build a Markdown data card describing the dataset."""
    report = report or {}
    coverage = coverage or {}
    noise_params = noise_params or {}
    noise_enabled = noise != "none"

    if not noise_enabled:
        benchmark_focus = "clean simulation benchmark"
        noise_line = "No explicit noise model was used in this release."
    elif noise == "depolarizing":
        benchmark_focus = "depolarizing-noise robustness benchmark"
        noise_line = f"Noise model: depolarizing (p={noise_prob})."
    elif noise == "amplitude_damping":
        benchmark_focus = "amplitude-damping robustness benchmark"
        noise_line = f"Noise model: amplitude damping (p={noise_prob})."
    elif noise == "phase_damping":
        benchmark_focus = "phase-damping robustness benchmark"
        noise_line = f"Noise model: phase damping (p={noise_prob})."
    elif noise == "thermal_relaxation":
        benchmark_focus = "thermal-relaxation robustness benchmark"
        noise_line = f"Noise model: thermal relaxation (T1={noise_params.get('t1', 'N/A')}, T2={noise_params.get('t2', 'N/A')})."
    elif noise == "phase_amplitude_damping":
        benchmark_focus = "phase+amplitude damping robustness benchmark"
        noise_line = f"Noise model: phase-amplitude damping (p={noise_prob})."
    elif noise == "readout":
        benchmark_focus = "readout-error robustness benchmark"
        noise_line = f"Noise model: readout error (p0={noise_params.get('p0', noise_prob)}, p1={noise_params.get('p1', noise_prob)})."
    elif noise == "device":
        benchmark_focus = "device-like noise robustness benchmark"
        noise_line = f"Noise model: realistic device-like (GenericBackendV2, {n_qubits} qubits)."
    else:
        benchmark_focus = "noise-aware benchmark"
        noise_line = f"Noise model: {noise} (p={noise_prob})."

    if circuit_type == "mixed":
        circuit_line = "Circuit family: mixed (randomly sampled from the supported family pool)."
    else:
        circuit_line = f"Circuit family: {circuit_type}."

    if observable_mode == "global":
        observable_line = "Observable mode: global only."
    elif observable_mode == "per_qubit":
        observable_line = "Observable mode: per-qubit only."
    else:
        observable_line = "Observable mode: mixed (global + per-qubit)."

    labels_per_base = 0
    if observable_mode in {"global", "mixed"}:
        labels_per_base += 1
    if observable_mode in {"per_qubit", "mixed"}:
        labels_per_base += n_qubits
    total_label_heads = labels_per_base * len(observable_bases)

    split_counts = coverage.get("split", {})
    split_text = (
        ", ".join(f"{name}: {count}" for name, count in split_counts.items())
        if split_counts
        else "not available"
    )

    family_counts = coverage.get("circuit_type_resolved", {})
    family_text = (
        ", ".join(f"{name}: {count}" for name, count in family_counts.items())
        if family_counts
        else circuit_line
    )

    metrics_line_items = []
    if "rows" in report:
        metrics_line_items.append(f"Rows: {report['rows']}")
    if "columns" in report:
        metrics_line_items.append(f"Columns: {report['columns']}")
    if "unique_circuits" in report:
        metrics_line_items.append(f"Unique circuits: {report['unique_circuits']}")
    if "splits" in report:
        metrics_line_items.append(f"Split summary: {report['splits']}")
    metrics_text = (
        " | ".join(metrics_line_items)
        if metrics_line_items
        else "Summary statistics are available in report.json."
    )

    observables_text = ", ".join(observable_bases) if observable_bases else "N/A"
    has_csv = any(name.endswith(".csv") for name in files)

    return f"""
Release overview

Dataset name: {dataset_name}
Release version: {dataset_version}
Benchmark focus: {benchmark_focus}
Total rows: {total_rows_written}
Shards: {shard_count}
Storage format: Parquet shards{' + CSV exports' if has_csv else ''}
Backend device: {backend_device}
GPU requested: {use_gpu}
GPU available: {gpu_available}

What is inside this release?
This release is a synthetic quantum benchmark dataset for:

- expectation value regression
- circuit family classification
- noise robustness analysis
- circuit structure and complexity analysis
- hybrid quantum-classical experimentation

Generation profile

Qubits: {n_qubits}
Depth: {depth}
Circuit family request: {circuit_type}
{circuit_line}
Entanglement: {entanglement}
{noise_line}
Shots: {shots}
Observable bases: {observables_text}
{observable_line}
Approximate label heads: {total_label_heads}

Why this release is useful
This dataset is designed for:

- supervised learning on ideal and noisy expectation values
- benchmarking models across multiple circuit families
- robustness testing under configurable noise settings
- circuit-structure analysis using gate and connectivity metrics
- reproducible train/validation/test splits

Split policy

Train: {train_frac}
Validation: {val_frac}
Test: {test_frac}
Split distribution: {split_text}

Summary statistics
{metrics_text}

Family coverage
{family_text}

Files in the release

{chr(10).join(f"- {name}" for name in files)}

Important notes

- split is assigned deterministically from circuit_hash.
- ideal_expval_* values come from clean simulation.
- noisy_expval_* values come from the selected noise model.
- error_* is the difference between ideal and noisy expectation values.
- The exact column layout is described in schema.json.
- The exact shard inventory is described in manifest.json.

Loading guidance

Use the Parquet shards for production workflows. CSV copies, when enabled, are provided for portability and quick inspection.
"""