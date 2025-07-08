.PHONY: help install install-dev test test-unit test-integration test-e2e lint format clean setup setup-env

help: ## Show this help message
	@echo "ENEM Microdata ETL Pipeline - Development Commands"
	@echo "=================================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	python -m pip install -r requirements.txt

install-dev: ## Install development dependencies
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-test.txt

setup: ## Set up the development environment
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # Linux/Mac"
	@echo "  venv\\Scripts\\activate     # Windows"
	@echo ""
	@echo "Then run: make install-dev"

setup-env: ## Set up environment file
	python scripts/setup_env.py

test: ## Run all tests (excluding database tests)
	python tests/run_tests.py

test-all: ## Run all tests including database tests (if configured)
	python tests/run_tests.py --database

test-unit: ## Run unit tests only (no database)
	python tests/run_tests.py --no-database

test-database: ## Run database tests only
	python tests/run_tests.py --database-only

test-cov: ## Run tests with coverage report
	python tests/run_tests.py --coverage

test-quick: ## Run quick tests only (no database)
	python tests/run_tests.py --no-database

test-verbose: ## Run tests with verbose output
	python tests/run_tests.py --verbose

test-check-config: ## Check database configuration
	python tests/run_tests.py --check-config



# Database Commands
test-db: ## Test database connections
	python -m pytest tests/integration/test_databases.py -v



db-status: ## Check database service status
	@echo "Checking database services..."
	@docker-compose ps postgres postgres-etl

lint: ## Run linting checks
	python -m flake8 src/ tests/
	python -m mypy src/

format: ## Format code with black and isort
	python -m black src/ tests/
	python -m isort src/ tests/

format-check: ## Check if code is properly formatted
	python -m black --check src/ tests/
	python -m isort --check-only src/ tests/

clean: ## Clean up generated files
	@echo "Cleaning up generated files..."
	@python -c "import os; [os.remove(f) for f in os.listdir('.') if f.endswith('.pyc')]"
	@python -c "import shutil; [shutil.rmtree(d) for d in os.listdir('.') if d in ['__pycache__', 'build', 'dist', '.pytest_cache', 'htmlcov'] and os.path.isdir(d)]"
	@python -c "import shutil; [shutil.rmtree(d) for d in os.listdir('.') if d.endswith('.egg-info') and os.path.isdir(d)]"
	@echo "Cleanup completed!"



# Airflow Commands
airflow-start: ## Start Airflow services
	python scripts/start_airflow.py

airflow-up: ## Start all Airflow services with docker-compose
	docker-compose up -d

airflow-down: ## Stop all Airflow services
	docker-compose down

airflow-logs: ## View logs from all Airflow services
	docker-compose logs -f

airflow-restart: ## Restart all Airflow services
	docker-compose restart

airflow-init: ## Initialize Airflow variables
	docker-compose exec airflow-webserver python config/airflow_init.py

# Docker Commands
docker-build: ## Build Docker image
	docker build -t enem-microdata-etl .

docker-run: ## Run Docker container
	docker run -it --rm enem-microdata-etl

docker-compose-up: ## Start all services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop all services
	docker-compose down

docker-compose-logs: ## View logs from all services
	docker-compose logs -f

pre-commit: ## Run pre-commit hooks
	python -m pre_commit run --all-files

docs: ## Generate documentation
	@echo "Documentation is available in the docs/ directory"
	@echo "Main documentation: README.md" 