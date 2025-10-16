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
