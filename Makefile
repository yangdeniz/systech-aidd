.PHONY: help run test install format lint typecheck quality db-up db-down db-migrate db-reset db-revision
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install project dependencies"
	@echo "  make run              - Run the Telegram bot"
	@echo "  make format           - Format code with ruff"
	@echo "  make lint             - Lint code with ruff"
	@echo "  make typecheck        - Type check with mypy"
	@echo "  make test             - Run tests with coverage"
	@echo "  make quality          - Run all quality checks (format, lint, typecheck, test)"
	@echo ""
	@echo "Database:"
	@echo "  make db-up            - Start PostgreSQL in Docker"
	@echo "  make db-down          - Stop Docker containers"
	@echo "  make db-migrate       - Run database migrations"
	@echo "  make db-revision MSG='message' - Create new migration"
	@echo "  make db-reset         - Reset database (warning: deletes all data)"
	@echo ""
	@echo "API:"
	@echo "  make api-run          - Run API server (mock mode)"
	@echo "  make api-run-real     - Run API server (real data mode)"
	@echo "  make api-test         - Test API endpoints"
	@echo "  make api-docs         - Open API documentation in browser"
	@echo "  make api-info         - Get API info and cache status"
	@echo "  make api-clear-cache  - Clear API cache"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make frontend-dev     - Start frontend dev server"
	@echo "  make frontend-build   - Build frontend for production"
	@echo "  make frontend-test    - Run frontend tests"
	@echo "  make frontend-lint    - Lint frontend code"
	@echo "  make frontend-format  - Format frontend code"
	@echo "  make frontend-quality - Run all frontend quality checks"
	@echo ""
	@echo "Combined:"
	@echo "  make quality-all      - Run all quality checks (backend + frontend)"

install:
	uv sync --all-extras

run:
	uv run python -m src.bot.main

format:
	uv run ruff format src tests

lint:
	uv run ruff check src tests --fix

typecheck:
	uv run mypy src/bot

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

quality: format lint typecheck test

# Database management commands
db-up:
	docker-compose up -d postgres

db-down:
	docker-compose down

db-migrate:
	uv run alembic upgrade head

db-revision:
	uv run alembic revision --autogenerate -m "$(MSG)"

db-reset:
	docker-compose down -v
	docker-compose up -d postgres
	timeout /t 5 /nobreak
	uv run alembic upgrade head

# API commands (Mock mode by default)
api-run:
	uv run uvicorn src.api.main:app --reload --port 8000

api-run-real:
	set COLLECTOR_MODE=real&& uv run uvicorn src.api.main:app --reload --port 8000

api-test:
	@echo Testing API endpoints...
	@uv run python -c "import httpx; import sys; r = httpx.get('http://localhost:8000/stats?period=day'); print(f'GET /stats?period=day: {r.status_code}'); r = httpx.get('http://localhost:8000/stats?period=week'); print(f'GET /stats?period=week: {r.status_code}'); r = httpx.get('http://localhost:8000/stats?period=month'); print(f'GET /stats?period=month: {r.status_code}')"

api-docs:
	@echo Opening API documentation...
	@cmd /c start http://localhost:8000/docs

api-info:
	@echo Getting API info and cache status...
	@uv run python -c "import httpx; import json; r = httpx.get('http://localhost:8000/'); print(json.dumps(r.json(), indent=2)); r = httpx.get('http://localhost:8000/cache/info'); print('\\nCache info:'); print(json.dumps(r.json(), indent=2))"

api-clear-cache:
	@echo Clearing API cache...
	@uv run python -c "import httpx; r = httpx.post('http://localhost:8000/cache/clear'); print(r.json())"

# Frontend commands
.PHONY: frontend-install frontend-dev frontend-build frontend-test frontend-lint frontend-format frontend-quality

frontend-install:
	@echo Installing frontend dependencies...
	cd frontend/app && pnpm install

frontend-dev:
	@echo Starting frontend development server...
	cd frontend/app && pnpm run dev

frontend-build:
	@echo Building frontend for production...
	cd frontend/app && pnpm run build

frontend-test:
	@echo Running frontend tests...
	cd frontend/app && pnpm run test:ci

frontend-lint:
	@echo Linting frontend code...
	cd frontend/app && pnpm run lint

frontend-format:
	@echo Formatting frontend code...
	cd frontend/app && pnpm run format

frontend-quality:
	@echo Running frontend quality checks...
	cd frontend/app && pnpm run quality

# Combined quality check (backend + frontend)
quality-all: quality frontend-quality
	@echo All quality checks passed!