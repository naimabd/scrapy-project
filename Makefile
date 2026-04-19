.PHONY: setup dev test lint format help

help:
	@echo "Available commands:"
	@echo "  setup   - Install dependencies"
	@echo "  dev     - Run Dagster development server"
	@echo "  test    - Run tests"
	@echo "  lint    - Run ruff and mypy"
	@echo "  format  - Run ruff format"

setup:
	pip install -e ".[dev]"

dev:
	dagster dev -f src/orchestrator/definitions.py

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	ruff format .
