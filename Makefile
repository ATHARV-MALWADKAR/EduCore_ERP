.PHONY: help setup run dev test lint security clean docker-build docker-up docker-down docs

help:
	@echo "College ERP Development Commands"
	@echo "===================================="
	@echo "make setup          - Install dependencies"
	@echo "make run            - Start all services with docker-compose"
	@echo "make dev            - Run backend in development mode"
	@echo "make test           - Run tests with coverage"
	@echo "make test-fast      - Run tests without coverage"
	@echo "make lint           - Run linters (flake8, black, isort)"
	@echo "make format         - Auto-format code with black and isort"
	@echo "make security       - Run security scans (bandit, safety)"
	@echo "make mypy           - Type check with mypy"
	@echo "make docker-build   - Build Docker images"
	@echo "make docker-up      - Start all containers"
	@echo "make docker-down    - Stop all containers"
	@echo "make docker-logs    - View container logs"
	@echo "make clean          - Clean up generated files"
	@echo "make db-migrate     - Run database migrations"
	@echo "make db-seed        - Seed database with sample data"
	@echo "make docs           - Generate API documentation"

# Development Setup
setup:
	pip install -e ".[dev,e2e]"
	mkdir -p tests/{unit,integration,e2e}
	echo "✓ Dependencies installed. Set up .env file next."

# Running the Application
run: docker-build docker-up
	@echo "✓ All services started. Access the app at http://localhost:3000"

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	sleep 5
	docker-compose logs -f

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

dev:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
test:
	pytest -v --cov=backend --cov-report=term-short --cov-report=html

test-fast:
	pytest -v

test-specific:
	pytest -v -k $(TEST_NAME)

test-coverage:
	pytest --cov=backend --cov-report=html && open htmlcov/index.html

test-e2e:
	playwright install
	pytest tests/e2e -v

# Code Quality
lint:
	flake8 backend tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 backend tests --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format:
	black backend tests
	isort backend tests

security:
	@echo "Running Bandit..."
	bandit -r backend -ll -x tests
	@echo "\nRunning Safety..."
	safety check --json || true

mypy:
	mypy backend --ignore-missing-imports

# Database
db-migrate:
	cd backend && alembic upgrade head

db-rollback:
	cd backend && alembic downgrade -1

db-seed:
	cd backend && python -c "from app.db.init_db import seed_database; from app.db.session import SessionLocal; db = SessionLocal(); seed_database(db); print('✓ Database seeded')"

# Documentation
docs:
	@echo "API docs available at http://localhost:8000/docs"

# Cleanup
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name 'htmlcov' -delete
	find . -type d -name '*.egg-info' -delete
	find . -type d -name '.env' -delete

reset-db:
	docker-compose down -v
	docker volume rm college_erp_mysql_data || true
	docker-compose up -d mysql
	sleep 5
	make db-migrate
	make db-seed
	@echo "✓ Database reset and seeded"

install-playwright:
	playwright install chromium

version:
	@echo "College ERP v1.0.0"
