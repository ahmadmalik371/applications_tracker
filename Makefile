.PHONY: help setup dev test lint format migrate docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies (backend and frontend)
	@echo "Setting up backend..."
	cd backend && pip install -r requirements.txt
	@echo "Setting up frontend..."
	cd frontend && npm install

dev: ## Run development servers (API and Web) concurrently
	@echo "Starting development servers..."
	# This requires a tool like concurrently or tmux in practice
	# For now, it's a placeholder for starting both

docker-up: ## Start infrastructure containers (Postgres, Redis)
	docker-compose up -d

docker-down: ## Stop infrastructure containers
	docker-compose down

test: ## Run tests for backend and frontend
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

lint: ## Run linters
	@echo "Linting backend..."
	cd backend && ruff check .
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: ## Run code formatters
	@echo "Formatting backend..."
	cd backend && black . && ruff check --fix .
	@echo "Formatting frontend..."
	cd frontend && npm run format

migrate: ## Run database migrations
	@echo "Running Alembic migrations..."
	cd backend && alembic upgrade head

clean: ## Remove compiled python files and node_modules
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/node_modules
