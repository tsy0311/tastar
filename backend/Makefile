.PHONY: help install dev migrate seed test lint format clean setup health validate docker-setup

help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Unified AI Business Assistant - Makefile Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🚀 Setup & Installation:"
	@echo "  make setup         - Complete setup (install, env, docker, migrate)"
	@echo "  make install       - Install Python dependencies"
	@echo "  make docker-setup  - Set up Docker services (PostgreSQL, Redis)"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev           - Run development server"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-create - Create new migration (use: make migrate-create msg='description')"
	@echo "  make seed          - Seed database with sample data"
	@echo ""
	@echo "✅ Validation & Testing:"
	@echo "  make health        - Run health check"
	@echo "  make validate      - Validate environment variables"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters (flake8, mypy)"
	@echo "  make format        - Format code (black, isort)"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean         - Clean cache files and __pycache__"
	@echo ""

setup:
	@echo "🚀 Running complete setup..."
	@bash setup.sh

install:
	@echo "📦 Installing dependencies..."
	@bash install.sh

docker-setup:
	@echo "🐳 Setting up Docker services..."
	@cd .. && bash setup_docker.sh

dev:
	@echo "🚀 Starting development server..."
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	@echo "🔄 Running database migrations..."
	@alembic upgrade head

migrate-create:
	@if [ -z "$(msg)" ]; then \
		echo "❌ Error: Please provide a message. Usage: make migrate-create msg='description'"; \
		exit 1; \
	fi
	@echo "📝 Creating new migration: $(msg)"
	@alembic revision --autogenerate -m "$(msg)"

seed:
	@echo "🌱 Seeding database..."
	@python scripts/seed_db.py

health:
	@echo "🏥 Running health check..."
	@python scripts/check_health.py

validate:
	@echo "🔍 Validating environment..."
	@python scripts/validate_env.py

test:
	@echo "🧪 Running tests..."
	@pytest

lint:
	@echo "🔍 Running linters..."
	@flake8 app/ || true
	@mypy app/ || true

format:
	@echo "✨ Formatting code..."
	@black app/
	@isort app/

clean:
	@echo "🧹 Cleaning cache files..."
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	@echo "✅ Clean complete"






