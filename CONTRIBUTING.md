# Contributing to QSBench

Thank you for considering contributing to QSBench!  
We welcome contributions from researchers, engineers, students, and quantum enthusiasts.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Workflow](#workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Questions?](#questions)

---

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of-conduct/).  
Be kind, respectful, and constructive.

---

## How Can I Contribute?

### Reporting Bugs

- Open an issue using the **Bug Report** template
- Include:
  - QSBench version (`__version__`)
  - Python and Qiskit versions
  - Steps to reproduce
  - Expected vs actual behavior
  - Error traceback (if any)

### Suggesting Features / Improvements

- Open an issue with the **Feature Request** template
- Clearly describe the use case and why it's important
- Bonus: suggest implementation approach

### Contributing Code

We especially welcome contributions in the following areas:
- New noise models
- Better circuit generation families
- Export formats (HDF5, Zarr, etc.)
- Performance improvements
- Documentation and examples
- Tests

---

## Development Setup

```bash
git clone https://github.com/QSBench/QSBench-Generator.git
cd QSBench-Generator

# Recommended: use virtual environment
python -m venv venv
source venv/bin/activate

# Install the package in editable mode with development dependencies (CPU version)
pip install -e ".[dev]"
```

### GPU support (optional)

If you have a CUDA-compatible GPU and want to use GPU-accelerated simulation:
```bash
# GPU + dev dependencies
pip install -e ".[gpu,dev]"
```

**Note:** `qiskit-aer-gpu` is now an optional dependency.
The default installation (`.[dev]`) uses the CPU version of Aer, which works on any machine.
Docker image (CUDA-based) continues to work as before.

---

## Workflow

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/awesome-new-noise-model
```
3. Make your changes
4. Add tests (if applicable)
5. Ensure linting and tests pass:
```bash
make lint
make test
```
6. Commit using Conventional Commits
7. Push and open a Pull Request

---

## Commit Guidelines

We use **Conventional Commits:**
```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Allowed types:

- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or correcting tests
- `chore` — maintenance
- `perf` — performance improvement

Examples:

- `feat(noise): add thermal_relaxation model with T1/T2 support`
- `fix(generator): correct split assignment for edge cases`
- `docs: improve CONTRIBUTING.md`

### Pull Request Guidelines

- **Title** should follow Conventional Commits style
- **Description** must include:
  - What was changed and why
  - Related issue (if any)
  - Testing done
- One PR = one logical change
- Keep PRs reasonably small
- All tests must pass
- Code must pass linting (`ruff`, `black`, `mypy`)

---

## Coding Standards

- **Python version**: 3.10+
- **Formatter**: Black
- **Linter**: Ruff
- **Type checking**: mypy
- **Import sorting**: isort

Run before committing:

```bash
make format      # black + isort
make lint        # ruff
make type-check  # mypy
```

---

## Testing

```bash
make test             # Run all tests
```

We aim for high test coverage on core modules (`generator`, `noise`, `storage`, `estimation`, etc).

---

## Documentation

- All new public functions and classes must have docstrings
- Update `README.md` and relevant documentation when adding features
- For large changes — update `docs/` folder (if exists)

---

## Questions?

- Open a `Discussion` in the repository
- Or contact the maintainer directly via GitHub Issues

---

**Thank you for contributing to QSBench!**
Together we are building better tools for the quantum machine learning community.