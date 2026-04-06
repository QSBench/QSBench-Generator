# RFC: Phase 1 — Architectural Standardization and Big Data Readiness

**Project:** QSBench-Generator  
**Status:** Draft  
**Target window:** Now – Q3 2026  
**Authors:** QSBench contributors  

## 1. Abstract

This RFC proposes the first architecture-focused phase of QSBench-Generator. The goal is to standardize storage, add a clear hierarchy of circuit abstractions, and introduce an interoperable export path for scientific Python workflows.

Phase 1 introduces three core capabilities:

1. **Parquet as the default storage format** for scalable analysis and efficient columnar access.
2. **A hierarchy of circuit abstractions** modeled after the MQT-style compilation pipeline.
3. **HDF5 export support** for compatibility with PennyLane-oriented and broader scientific workflows.

Together, these changes establish a stable data foundation for later phases focused on physics-informed generation, quality automation, and benchmark expansion.

## 2. Motivation

QSBench aims to generate structurally enriched datasets for QML research. As the project grows, three issues become increasingly important:

- Datasets will become too large for row-oriented inspection and analysis.
- Circuit samples need explicit provenance across compilation stages.
- Researchers use multiple ecosystems, and export interoperability matters.

Without standardization, QSBench risks producing data that is difficult to query, compare, validate, and reuse across tooling stacks.

## 3. Goals

This phase is intended to achieve the following:

- Make **Parquet** the primary storage format for all generated datasets.
- Expose a **standard circuit hierarchy** that distinguishes algorithmic, optimized, native, and mapped representations.
- Provide **HDF5 export** for downstream scientific interoperability.
- Preserve backward compatibility where practical.
- Establish metadata conventions that can be extended in later phases.

## 4. Non-goals

This RFC does **not** define:

- New physics-informed generators.
- New entanglement or expressivity metrics.
- New benchmark tasks or labels.
- Model training pipelines.
- A final ontology for all possible QML circuit representations.

Those topics belong to later phases or separate RFCs.

## 5. Proposed Changes

### 5.1 Parquet storage optimization

QSBench will use **Parquet** as the default on-disk format for generated datasets.

#### Why Parquet

- Columnar storage enables **column pruning**, which reduces I/O when only metadata fields are needed.
- Compression is more effective for repeated structured metadata.
- Parquet is a strong fit for large-scale analytical workloads.
- Nested structures and arrays can be stored more naturally than in CSV.

#### Requirements

- Parquet must be the default export for all new datasets.
- Schema definitions must be explicit and versioned.
- Data types must remain stable across releases where possible.
- The format must support selective loading of metadata columns without reading full circuit payloads.

#### Recommended dataset layout

A Parquet dataset should separate:

- **Core sample identifiers**
- **Circuit representations**
- **Compilation-level metadata**
- **Device / backend metadata**
- **Benchmark labels and evaluation fields**

This allows fast querying on metadata-only workflows.

---

### 5.2 Hierarchy of abstractions (MQT-style model)

QSBench will introduce metadata describing the **circuit compilation level**. This creates a consistent interpretation of how a circuit was transformed before storage.

#### Levels

**Algorithmic**  
The original idealized algorithmic logic. This representation describes the circuit at the conceptual level, before optimization or hardware adaptation.

**Target-Independent**  
An optimized logical circuit that is still independent of any specific hardware platform. Gate identities may be simplified, merged, or reordered, but no vendor-specific constraints are applied.

**Native**  
The circuit expressed in the native gate set of a specific vendor or backend family, such as IBM, IonQ, or Rigetti.

**Mapped**  
The circuit after topology-aware mapping, including SWAP insertion, qubit placement constraints, and connectivity-aware routing.

#### Metadata fields

At minimum, each sample should expose:

- `circuit_level`
- `source_level`
- `target_backend`
- `native_gate_set`
- `mapping_applied`
- `swap_count`
- `depth_before_mapping`
- `depth_after_mapping`
- `qubit_count`
- `connectivity_profile`

#### Benefits

- Enables apples-to-apples comparison between logical and hardware-constrained circuits.
- Makes it easier to benchmark compilation quality.
- Supports downstream filtering by abstraction level.
- Provides provenance for all samples.

---

### 5.3 HDF5 export

QSBench will add export support for **HDF5 (.h5)**.

#### Why HDF5

- Widely used in scientific Python ecosystems.
- Convenient for tensor-like data and hierarchical grouping.
- Works well with tooling around quantum chemistry, ML, and numerical simulation.
- Aligns with workflows that expect chunked arrays and structured datasets.

#### Scope of support

HDF5 export should be designed for:

- Circuit tensors or arrays
- Numeric labels
- Sample-level metadata
- Grouped collections of benchmark subsets

#### Design principles

- Preserve the same logical schema across Parquet and HDF5 where feasible.
- Avoid duplicating semantic meaning in different fields.
- Keep HDF5 as an export target, not necessarily the primary storage layer.
- Ensure HDF5 output can be read by common scientific Python libraries with minimal friction.

## 6. Data Model Proposal

### 6.1 Core sample schema

A sample may include:

- `sample_id`
- `benchmark_name`
- `dataset_version`
- `circuit_level`
- `circuit_representation`
- `qubit_count`
- `depth`
- `gate_counts`
- `backend_name`
- `native_gate_set`
- `connectivity_profile`
- `swap_count`
- `noise_model`
- `labels`
- `generation_seed`
- `provenance`

### 6.2 Versioning

Every dataset release must include:

- dataset version
- schema version
- generator version
- optional backend/compiler version metadata

This ensures reproducibility and safe schema evolution.

## 7. Compatibility and Migration

### Backward compatibility

Existing datasets should remain readable. Where conversion is required, a migration path should be provided from legacy formats to Parquet.

### Migration strategy

1. Keep old exports available for a limited transition window.
2. Add conversion utilities from existing formats to the new schema.
3. Document all breaking schema changes explicitly.
4. Provide validation scripts to verify fidelity after migration.

## 8. Risks and Trade-offs

### Risk: Schema complexity
A richer metadata model can increase complexity. This should be mitigated by strict schema documentation and type validation.

### Risk: Format fragmentation
Supporting multiple export formats may create maintenance overhead. To reduce this, Parquet should remain the canonical storage format.

### Risk: Ambiguous abstraction levels
Different users may interpret circuit stages differently. A formal schema and controlled vocabulary are required.

### Risk: HDF5 scope creep
HDF5 can become a second primary storage system by accident. The project should keep HDF5 as an export path unless future usage clearly justifies more.

## 9. Implementation Plan

### Step 1: Storage standardization
- Define the canonical Parquet schema.
- Add schema versioning.
- Update generator output pipeline.

### Step 2: Circuit abstraction metadata
- Add compilation-level fields.
- Implement mapping between circuit stages.
- Validate backend-specific metadata consistency.

### Step 3: HDF5 export
- Define HDF5 group and dataset layout.
- Implement export utilities.
- Add round-trip and compatibility tests.

### Step 4: Documentation
- Document field definitions.
- Add examples for Parquet and HDF5 output.
- Provide guidance for filtering by abstraction level.

## 10. Acceptance Criteria

Phase 1 can be considered complete when:

- Parquet is the default storage format.
- Datasets can be filtered efficiently by metadata columns.
- Circuit samples consistently expose a compilation-level hierarchy.
- HDF5 export is available and validated.
- Schema versioning and migration notes are documented.
- At least one end-to-end benchmark dataset can be generated in the new format.

## 11. Open Questions

- Should `Algorithmic` and `Target-Independent` both be mandatory for every sample?
- Should `Native` always be derived from a named vendor backend, or can it be generic to a gate family?
- Which HDF5 layout best matches PennyLane expectations while keeping the schema simple?
- Should Parquet store full circuit text, tensor encodings, or both?

## 12. Summary

This phase turns QSBench-Generator into a more scalable and interoperable foundation. Parquet improves analytics and large-scale querying, the abstraction hierarchy improves provenance and benchmark comparability, and HDF5 export expands compatibility with scientific workflows.

This RFC establishes the minimum structural standard needed for QSBench to grow into a durable benchmark ecosystem.
