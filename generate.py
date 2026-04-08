"""
QSBench v5.1.0 — entry point
"""

from qsbench.generator import DatasetGenerator


def main() -> None:
    generator = DatasetGenerator()
    generator.run()


if __name__ == "__main__":
    main()