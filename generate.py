"""
QSBench v5.1.0 — modular release generator with versioned output folders,
metadata, schema, coverage, manifest, report, changelog, and data card.
"""

from generator.generator import DatasetGenerator


def main() -> None:
    generator = DatasetGenerator()
    generator.run()


if __name__ == "__main__":
    main()