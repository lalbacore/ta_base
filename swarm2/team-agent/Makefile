.PHONY: help install test test-coverage lint format clean

help:
    @echo "Team Agent - Development Commands"
    @echo "=================================="
    @echo "make install       - Install dependencies"
    @echo "make test          - Run all tests"
    @echo "make test-coverage - Run tests with coverage"
    @echo "make lint          - Run pylint and mypy"
    @echo "make format        - Format code with black and isort"
    @echo "make clean         - Clean cache files"
    @echo "make check         - Run all checks (lint + test)"

install:
    pip install -e ".[dev]"

test:
    python -m unittest discover -s utils/tests -p "test_*.py" -v

test-coverage:
    pytest --cov=swarms --cov=base --cov-report=html --cov-report=term

lint:
    pylint swarms base utils
    mypy swarms base utils --ignore-missing-imports

format:
    black .
    isort .

clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .coverage htmlcov .mypy_cache dist build *.egg-info

check: lint test
    @echo "✅ All checks passed!"