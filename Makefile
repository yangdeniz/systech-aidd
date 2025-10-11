.PHONY: run test install format lint typecheck quality

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
