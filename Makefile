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

test:
	pytest

test-coverage:
	pytest --cov=qsbench --cov-report=term-missing

clean:
	rm -rf __pycache__ .pytest_cache .coverage *.egg-info dist build