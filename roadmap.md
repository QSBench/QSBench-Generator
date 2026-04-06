# QSBench-Generator Roadmap (2026+)

**Project goal:** to become the de facto standard for generating structurally enriched datasets in quantum machine learning (QML), providing researchers with data that captures both device physics and the topological complexity of algorithms.

## Phase 1: Architectural Standardization and Big Data Readiness (Now – Q3 2026)

- **Parquet storage optimization**  
  Move fully to **Parquet** as the default storage format to enable efficient **column pruning** and **data skipping** when analyzing individual metadata fields.

- **Hierarchy of abstractions (MQT-style model)**  
  Introduce metadata that explicitly describes the circuit compilation level:
  - **Algorithmic** — the original, idealized algorithmic logic.
  - **Target-Independent** — optimized logical gates, still independent of any specific hardware platform.
  - **Native** — gates expressed in the native gate set of a specific vendor (IBM, IonQ, Rigetti, etc.).
  - **Mapped** — the circuit after topology-aware mapping, including SWAP insertion and hardware connectivity constraints.

- **HDF5 export**  
  Add support for **.h5 / HDF5** export to enable seamless integration with the PennyLane Datasets ecosystem and other scientific Python workflows.

## Phase 2: Physics-Informed Generation (Q4 2026 – Q1 2027)

- **HamLib integration**  
  Add a circuit-generation module based on real physical Hamiltonians, including **Heisenberg**, **Fermi–Hubbard**, and **MaxCut**-inspired models.

- **Entanglement targeting (CE)**  
  Implement generation of data with a desired distribution of **Concentratable Entanglement**, instead of fixed values. This is especially important for training generative QML models where entanglement diversity matters.

- **Dynamic circuits**  
  Support circuit instructions with **mid-circuit measurements** (`MEASURE`) and **classical control flow** (`IF`), which are required for benchmarking error-correction and adaptive quantum algorithms.

## Phase 3: Data Quality and Automation (Q2 2027 – Q4 2027)

- **Validation via SWAP test**  
  Integrate automatic checks for uniqueness and diversity of generated states using the **SWAP test**, helping to prevent duplicate information in training samples.

- **AutoQML & ansatz search**  
  Develop meta-datasets for automated architecture selection (NAS-style workflows) that predict classification accuracy from structural features and noise parameters.

- **Advanced expressivity metrics**  
  Include metadata fields for **entangling capability** and **expressibility** of circuits, enabling better evaluation of their ability to approximate complex functions.

## Comparative Format Overview in QSBench

| Feature | Parquet (Default) | CSV (Optional) | HDF5 (Planned) |
|---|---:|---:|---:|
| Compression | High (columnar) | Low | Medium |
| Read speed | Very high for Big Data workloads | Low | High |
| Complex types | Supports nested structures and arrays | Strings/numbers only | Supports complex scientific objects |
| Main use case | Analytics, GNNs, large-scale benchmarking | Quick inspection, small samples | Scientific ML, quantum chemistry, PennyLane integration |

## Implementation Notes

- **Mathematical metrics**  
  For all circuits, a **fidelity** score will be computed under different noise models:
  \[
  F(\rho, \sigma) = \left(\mathrm{Tr}\sqrt{\sqrt{\rho}\,\sigma\,\sqrt{\rho}}\right)^2
  \]

- **Entropy-based indicators**  
  The datasets will also include **von Neumann entropy**:
  \[
  S(\rho) = -\mathrm{Tr}(\rho \ln \rho)
  \]
  This provides a more precise view of decoherence in thermodynamic noise models.

## Suggested positioning

QSBench-Generator should emphasize three differentiators:

1. **Hardware awareness** — metadata that captures compilation, mapping, and device-specific constraints.
2. **Physics realism** — generation driven by real Hamiltonians and physically meaningful noise.
3. **Benchmark automation** — built-in quality checks and meta-datasets for downstream model selection and performance prediction.

Together, these features can make QSBench not just a dataset generator, but a reusable benchmarking infrastructure for QML research.

