# ==============================================================================
# Makefile for GuardianAI v2 (Aegis Runtime) Automation
# ==============================================================================

.PHONY: help run test docker-build docker-up docker-down lint format clean

help:
	@echo "======================================================================"
	@echo "GuardianAI v2 (Aegis Runtime) Automation Commands"
	@echo "======================================================================"
	@echo "  make run          : Run the FastAPI server locally (dev mode)"
	@echo "  make test         : Execute tests via Pytest"
	@echo "  make docker-build : Build docker image"
	@echo "  make docker-up    : Build and start container services"
	@echo "  make docker-down  : Stop docker containers"
	@echo "  make lint         : Run Ruff lint checks and Mypy typing checks"
	@echo "  make format       : Format code with Black and Ruff fix"
	@echo "  make clean        : Clean temporary caches and Python compiler files"
	@echo "======================================================================"

run:
	poetry run uvicorn main:app --reload --host 127.0.0.1 --port 8000

test:
	poetry run pytest -v

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

lint:
	poetry run ruff check app/ tests/
	poetry run mypy app/

format:
	poetry run black app/ tests/
	poetry run ruff check --fix app/ tests/

clean:
	@echo "Cleaning cache and build files..."
	python -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__') if p.exists()]"
	python -c "import shutil; [shutil.rmtree(p) for p in ['.pytest_cache', '.ruff_cache', '.mypy_cache'] if pathlib.Path(p).exists()]"
	@echo "Clean completed."
