.PHONY: setup dev test lint format help

help:
	@echo "Available commands:"
	@echo "  setup   - Install dependencies"
	@echo "  dev     - Run Dagster development server"
	@echo "  test    - Run tests"
	@echo "  lint    - Run ruff and mypy"
	@echo "  format  - Run ruff format"

setup:
	.venv/bin/pip install -e ".[dev]"

dev:
	mkdir -p .dagster
	.venv/bin/dagster dev -f src/orchestrator/definitions.py

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check src/
	.venv/bin/mypy src/

format:
	.venv/bin/ruff format src/

