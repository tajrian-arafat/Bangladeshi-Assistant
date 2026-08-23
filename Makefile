.PHONY: install dev migrate seed test lint typecheck clean help

BACKEND_DIR := backend
PYTHON := python3
VENV := $(BACKEND_DIR)/.venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn
ALEMBIC := $(VENV)/bin/alembic
RUFF := $(VENV)/bin/ruff
LINT_IMPORTS := $(VENV)/bin/lint-imports

help:
	@echo "Bangladesh Digital Assistant — available targets:"
	@echo "  make install   Install backend dependencies in virtualenv"
	@echo "  make dev       Run FastAPI dev server with hot reload"
	@echo "  make migrate   Run Alembic migrations"
	@echo "  make seed      Load seed data (geography, agencies, services)"
	@echo "  make test      Run pytest suite"
	@echo "  make lint      Run ruff and import-linter"
	@echo "  make typecheck Run mypy"
	@echo "  make clean     Remove virtualenv and cached files"

install:
	cd $(BACKEND_DIR) && $(PYTHON) -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e "$(BACKEND_DIR)[dev]"
	@echo "Installed. Activate with: source $(VENV)/bin/activate"

dev: install
	mkdir -p $(BACKEND_DIR)/data
	cd $(BACKEND_DIR) && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate: install
	mkdir -p $(BACKEND_DIR)/data
	cd $(BACKEND_DIR) && .venv/bin/alembic upgrade head

seed: migrate
	cd $(BACKEND_DIR) && .venv/bin/python ../scripts/seed_database.py

test: install migrate
	cd $(BACKEND_DIR) && $(PYTEST) -v

lint: install
	cd $(BACKEND_DIR) && $(RUFF) check app tests
	cd $(BACKEND_DIR) && $(RUFF) format --check app tests
	$(LINT_IMPORTS) --config importlinter.ini

typecheck: install
	cd $(BACKEND_DIR) && $(VENV)/bin/mypy app

clean:
	rm -rf $(VENV) $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.mypy_cache $(BACKEND_DIR)/.ruff_cache
	find $(BACKEND_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
