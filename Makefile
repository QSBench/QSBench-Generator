.PHONY: format lint type-check test test-coverage clean

format:
	ruff check --fix .
	black .
	isort .

lint:
	ruff check .
	black --check .
	isort --check-only .

type-check:
	mypy qsbench

# Главное изменение: всегда устанавливаем пакет перед тестами
test:
	pip install -e ".[dev]" --quiet
	pytest

test-coverage:
	pip install -e ".[dev]" --quiet
	pytest --cov=qsbench --cov-report=term-missing --cov-report=xml

clean:
	rm -rf __pycache__ .pytest_cache .coverage *.egg-info dist build