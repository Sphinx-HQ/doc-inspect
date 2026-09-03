.PHONY: install test lint format demo samples

PYTHON ?= python3
VENV ?= .venv
PIP = $(VENV)/bin/pip
PY = $(VENV)/bin/python

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -e ".[demo,dev]"

test:
	$(VENV)/bin/pytest

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy src

format:
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

demo:
	$(VENV)/bin/flask --app demo.app run --reload

samples:
	$(PY) samples/make_samples.py
