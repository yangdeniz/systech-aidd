.PHONY: run test install format lint typecheck quality db-up db-down db-migrate db-reset db-revision

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

# API commands
api-run:
	uv run uvicorn src.api.main:app --reload --port 8000

api-test:
	@echo Testing API endpoints...
	@uv run python -c "import httpx; import sys; r = httpx.get('http://localhost:8000/stats?period=day'); print(f'GET /stats?period=day: {r.status_code}'); r = httpx.get('http://localhost:8000/stats?period=week'); print(f'GET /stats?period=week: {r.status_code}'); r = httpx.get('http://localhost:8000/stats?period=month'); print(f'GET /stats?period=month: {r.status_code}')"

api-docs:
	@echo Opening API documentation...
	@cmd /c start http://localhost:8000/docs

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