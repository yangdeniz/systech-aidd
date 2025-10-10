.PHONY: run test install

install:
	uv sync --all-extras

run:
	uv run python src/bot/main.py

test:
	uv run pytest tests/ -v

