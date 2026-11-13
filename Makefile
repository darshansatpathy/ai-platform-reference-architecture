.PHONY: install check test fit docs cost audit

install:
	python -m venv .venv && .venv/bin/pip install -e ".[dev]"

check:
	ruff check . && ruff format --check . && mypy && pytest --cov=archfit --cov-fail-under=85

test:
	pytest

fit:
	archfit check && archfit docs --check

docs:
	archfit docs

cost:
	archfit cost

audit:
	pip-audit --skip-editable
