# ============================================================================
# Business Planner - Makefile
# ============================================================================
# Convenient commands for development
# ============================================================================

.PHONY: help install dev test lint format clean run docker-up docker-down

# Default target
help:
	@echo "Business Planner - Available Commands:"
	@echo ""
	@echo "⚠️  First time? Run: make setup"
	@echo ""
	@echo "  make setup      - 🚀 First-time setup (create .env, install deps)"
	@echo "  make setup-env  - Create/update .env file interactively"
	@echo "  make install    - Install production dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make test       - Run tests with coverage"
	@echo "  make lint       - Run linters (ruff, mypy)"
	@echo "  make format     - Format code (black, isort)"
	@echo "  make clean      - Clean cache files"
	@echo "  make run        - Run application locally"
	@echo "  make run-debug  - Run in debug mode"
	@echo "  make docker-up  - Start Docker Compose (dev)"
	@echo "  make docker-down - Stop Docker Compose"
	@echo ""

# ============================================================================
# First-Time Setup
# ============================================================================

setup:
	@echo "🚀 Business Planner - First Time Setup"
	@echo ""
	@echo "Step 1: Creating .env file..."
	@python setup_env.py
	@echo ""
	@echo "Step 2: Installing dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "📖 Next steps:"
	@echo "  1. Edit .env with your API keys (see SETUP_API_KEYS.md)"
	@echo "  2. Run: make docker-up (to start PostgreSQL)"
	@echo "  3. Run: make run-debug (to start the app)"
	@echo ""

setup-env:
	@python setup_env.py

# ============================================================================
# Installation
# ============================================================================

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

# ============================================================================
# Code Quality
# ============================================================================

format:
	@echo "Formatting code..."
	black src/ tests/ --line-length 100
	isort src/ tests/ --profile black
	@echo "✅ Code formatted"

lint:
	@echo "Running linters..."
	ruff check src/ tests/
	mypy src/ --strict
	@echo "✅ Linting complete"

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "Running tests with coverage..."
	pytest tests/ \
		--cov=src \
		--cov-report=html \
		--cov-report=term \
		--cov-fail-under=80 \
		-v
	@echo "✅ Tests complete - see htmlcov/index.html for coverage report"

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-e2e:
	pytest tests/e2e -v --slow

test-fast:
	pytest tests/unit -q

# ============================================================================
# Running
# ============================================================================

run:
	python -m src.main

run-debug:
	DEBUG=true python -m src.main

# ============================================================================
# Docker
# ============================================================================

docker-up:
	cd infrastructure/docker && docker-compose up -d

docker-down:
	cd infrastructure/docker && docker-compose down

docker-logs:
	cd infrastructure/docker && docker-compose logs -f

docker-build:
	cd infrastructure/docker && docker-compose up -d --build

# ============================================================================
# Database
# ============================================================================

db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

db-reset:
	alembic downgrade base
	alembic upgrade head

db-shell:
	cd infrastructure/docker && docker-compose exec postgres psql -U planner

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "✅ Cleaned"

# ============================================================================
# All-in-one
# ============================================================================

all: format lint test
	@echo "✅ All checks passed!"

