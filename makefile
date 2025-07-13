sync:
	uv sync
lint:
	uv run ruff check

fix:
	uv run ruff check --fix

format:
	uv run ruff format

migrate:
	uv run alembic revision --autogenerate -m "auto_$(shell date +%s)_$(m)" && uv run alembic upgrade head

dev: 
	uv run fastapi dev app/main.py

prod:
	uv run uvicorn app.main:app --reload
