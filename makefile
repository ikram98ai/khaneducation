sync:
	uv sync
lint:
	uv run ruff check

fix:
	uv run ruff check --fix

format:
	uv run ruff format

test:
	uv run pytest test_main.py

migrate:
	uv run alembic revision --autogenerate -m "auto_$(shell date +%s)_$(m)" && uv run alembic upgrade head

adminuser:
	uv run python create_admin.py -u="$(u)" -e="$(e)"

dev: 
	uv run fastapi dev app/main.py

prod:
	uv run uvicorn app.main:app --reload
