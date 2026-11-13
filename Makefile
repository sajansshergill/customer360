.PHONY: setup generate run test demo lint dbt deps

PYTHON ?= python3
VENV ?= .venv
ROOT := $(CURDIR)
export PYTHONPATH := $(ROOT)/src:$(ROOT)

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip && pip install -r requirements.txt -r requirements-dev.txt
	. $(VENV)/bin/activate && pip install -e .

generate:
	$(VENV)/bin/python data/synthetic/generate.py $(or $(PROFILES),1000)

run: generate
	bash scripts/run_pipeline.sh

test:
	$(VENV)/bin/pytest -q

demo:
	bash scripts/run_demo.sh

lint:
	$(VENV)/bin/ruff check src tests api data_quality

dbt:
	cd dbt && ../$(VENV)/bin/dbt deps && ../$(VENV)/bin/dbt seed && ../$(VENV)/bin/dbt run && ../$(VENV)/bin/dbt test

deps:
	cd dbt && ../$(VENV)/bin/dbt deps
