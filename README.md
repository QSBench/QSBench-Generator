# QSBench

**QSBench** is a modern open-source synthetic quantum dataset generator designed for Quantum Machine Learning (QML), quantum benchmarking, noise robustness studies, and sim-to-real research.

It generates high-quality, reproducible datasets with **ideal vs noisy** expectation values, rich circuit metrics, deterministic train/val/test splits, and advanced noise models — all in Parquet format with comprehensive metadata.

---

## Key Features

- Multiple circuit families (HEA, RealAmplitudes, QFT, random, mixed)

- **Advanced realistic noise models** (including thermal relaxation, readout error and device-like noise)

- Rich circuit metrics (gate entropy, Meyer-Wallach entanglement, adjacency matrix, etc.)

- Deterministic train/val/test splits based on circuit hash

- GPU-accelerated generation via Qiskit Aer

- Full metadata and documentation for every release

---

## Quick Start (Docker)

```bash
# 1. Clone and build
git clone https://github.com/QSBench/QSBench-Generator.git
cd QSBench-Generator
docker compose build --no-cache

# 2. Generate a test dataset
docker compose run --rm quantum-gen \
  python3 generate.py \
  --n-qubits 8 \
  --depth 6 \
  --n-samples 512 \
  --circuit-type mixed \
  --entanglement full \
  --noise thermal_relaxation \
  --noise-params '{"t1": 50e-6, "t2": 30e-6}' \
  --observable "Z,X,Y" \
  --observable-mode mixed \
  --shots 1024 \
  --use-gpu True \
  --dataset-name qsb_core_test_v5.1 \
  --output-root /app/out
```

Results will appear in `./out/qsb_core_test_v5.1/`.

---

## Release Structure

Every release is stored in a clean, versioned folder:

```text
out/
└── qsb_core_test_v5.1/
    ├── meta.json
    ├── schema.json
    ├── coverage.json
    ├── manifest.json
    ├── report.json
    ├── data_card.md
    ├── CHANGELOG.md
    ├── generation_log.json
    └── shards/
        ├── qsb_core_test_v5.1_shard_00000.parquet
        └── qsb_core_test_v5.1_shard_00000.csv (optional)
```

**Note**: `CHANGELOG.md` is automatically generated for every release and contains version history, added samples, family coverage and notes.

---

# CLI Reference: `generate.py`

All parameters are passed to `generate.py`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--n-qubits` | `14` | Number of qubits |
| `--depth` | `10` | Circuit depth |
| `--n-samples` | `1000` | Total number of circuits to generate |
| `--circuit-type` | `mixed` | Circuit family: `mixed`, `hea`, `efficient`, `real_amplitudes`, `qft`, `random` |
| `--entanglement` | `full` | Entanglement strategy: `linear`, `full`, `circular`, `sca` |
| `--noise` | `none` | Noise model (see Noise Models section below) |
| `--noise-prob` | `0.01` | Base noise probability (used by most models) |
| `--noise-params` | `{}` | JSON string with extra parameters (e.g. `{"t1": 50e-6, "t2": 30e-6}`) |
| `--observable` | `Z,X,Y` | Comma-separated observable bases |
| `--observable-mode` | `mixed` | `global`, `per_qubit`, or `mixed` |
| `--shots` | `4096` | Number of shots for noisy simulation |
| `--use-gpu` | `True` | Enable GPU acceleration (`True`/`False`) |
| `--dataset-name` | *required* | Name of the release folder (e.g. `qsb_core_v5.1`) |
| `--output-root` | `out` | Root directory for releases |
| `--seed` | `random` | Random seed for reproducibility |
| `--shard-size` | `128` | Number of samples per Parquet shard |
| `--train-frac` | `0.80` | Train split fraction |
| `--val-frac` | `0.10` | Validation split fraction |
| `--test-frac` | `0.10` | Test split fraction |
| `--write-csv` | `disabled` | Also write CSV copies of each shard |

---

# Noise Models

QSBench supports 8 different noise regimes (v5.1+):

| Noise Type | Description | When to use | Extra parameters (via `--noise-params`) |
|------------|-------------|-------------|------------------------------------------|
| `none` | No noise (ideal simulation) | Baseline | — |
| `depolarizing` | Standard depolarizing channel | General robustness | — |
| `amplitude_damping` | Amplitude damping (T1-like) | Energy relaxation studies | — |
| `phase_damping` | Pure phase damping (Tφ) | Phase coherence studies | — |
| `thermal_relaxation` | Realistic T1/T2 relaxation | Most realistic single-qubit noise | `t1`, `t2`, `gate_time_1q` |
| `phase_amplitude_damping` | Combined amplitude + phase damping | Combined decoherence | `p_amp`, `p_phase` |
| `readout` | Measurement (readout) errors | Expectation value accuracy | `p0`, `p1` |
| `device` | Full device-like noise (GenericBackendV2) | Hardware-mimic benchmarking | — (uses `n_qubits` automatically) |

**Example**:
```bash
--noise thermal_relaxation --noise-params '{"t1": 100e-6, "t2": 60e-6}'
--noise readout --noise-params '{"p0": 0.02, "p1": 0.015}'
--noise device
```

---

## Supported Use Cases

- Expectation value regression

- Noise robustness & error mitigation benchmarking

- Circuit family classification

- Sim-to-real transfer learning

- Hardware-aware quantum ML research

---

## Why QSBench?

- **Realistic noise** — beyond simple depolarizing/amplitude damping

- **Fully reproducible** — fixed seeds, deterministic splits, complete provenance

- **Production-ready format** — Parquet + rich JSON metadata

- **Research-friendly** — detailed `data_card.md` for every release

---

## License

This project is open-sourced under the Apache 2.0 License. Feel free to use it in research, publications, and commercial projects.

---

## Citation

If you use QSBench in your work, please cite:

```bibtex
@misc{qsbench2026,
  author = {NikolaI Iyankovich},
  title = {QSBench: Synthetic Quantum Dataset Generator for QML Benchmarking},
  year = {2026},
  url = {https://github.com/QSBench/QSBench-Generator}
}
```

---

**Ready to generate your first quantum dataset?**
Just run the Quick Start commands above.