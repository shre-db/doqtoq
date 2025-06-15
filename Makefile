# DoqToq Development Makefile
.PHONY: help install install-dev test lint format type-check security-check clean docker-build docker-run pre-commit setup-dev

# Default target
help:
	@echo "DoqToq Development Commands"
	@echo "=========================="
	@echo "setup-dev      - Set up development environment"
	@echo "install        - Install production dependencies"
	@echo "install-dev    - Install development dependencies"
	@echo "test           - Run test suite"
	@echo "test-cov       - Run tests with coverage report"
	@echo "lint           - Run all linting checks"
	@echo "format         - Format code with black and isort"
	@echo "type-check     - Run type checking with mypy"
	@echo "security-check - Run security checks"
	@echo "pre-commit     - Run pre-commit hooks"
	@echo "clean          - Clean up temporary files"
	@echo "docker-build   - Build Docker images"
	@echo "docker-run     - Run application in Docker"
	@echo "docs           - Generate documentation"
	@echo "release-check  - Check if ready for release"

# Development setup
setup-dev:
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "Development environment ready!"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=backend --cov=app --cov-report=html --cov-report=term-missing

test-integration:
	pytest tests/ -m integration -v

test-unit:
	pytest tests/ -m unit -v

# Code quality
lint: flake8 black-check isort-check

flake8:
	flake8 backend/ app/ tests/ --max-line-length=88 --extend-ignore=E203,W503

black-check:
	black --check backend/ app/ tests/

isort-check:
	isort --check-only backend/ app/ tests/

format:
	black backend/ app/ tests/
	isort backend/ app/ tests/

type-check:
	mypy backend/ app/ --ignore-missing-imports

# Security
security-check: bandit safety

bandit:
	bandit -r backend/ app/ -f json -o bandit-report.json

safety:
	safety check --json --output safety-report.json

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f bandit-report.json safety-report.json

# Docker
docker-build:
	docker build -f Dockerfile.venv -t doqtoq:latest .
	docker build -f Dockerfile.conda -t doqtoq:conda .

docker-run:
	docker run -p 8501:8501 --env-file .env doqtoq:latest

docker-run-dev:
	docker run -p 8501:8501 -v $(PWD):/app --env-file .env doqtoq:latest

# Documentation
docs:
	@echo "Generating documentation..."
	# Add sphinx documentation generation here
	@echo "Documentation generated in docs/_build/"

# Release preparation
release-check: lint type-check security-check test
	@echo "✅ All checks passed! Ready for release."

# Performance testing
perf-test:
	python tests/test_streaming_performance.py

# Start application
start:
	streamlit run app/main.py

start-dev:
	streamlit run app/main.py --server.runOnSave=true --server.fileWatcherType=poll
