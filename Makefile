.PHONY: check check-full lint test parity docs pages vignettes setup-venv

VENV_DIR ?= $(HOME)/.venvs/brain-pymice
VENV_PYTHON := $(VENV_DIR)/bin/python
PYTHON ?= $(shell test -x $(VENV_PYTHON) && echo $(VENV_PYTHON) || echo python3)
PIP ?= pip

check: lint test parity-structural audit-code-display

check-full: check parity-rng vignettes

lint:
	ruff format --check .
	ruff check .

test:
	$(PYTHON) -m pytest tests/ -q --ignore=tests/parity/test_rng_parity.py -m "not r_backend"

parity-structural:
	$(PYTHON) -m pytest tests/parity/test_structural_alignment.py -q

audit-code-display:
	$(PYTHON) devtools/audit_code_display.py

parity-rng:
	$(PYTHON) -m pytest tests/parity/test_rng_parity.py -q

vignettes:
	$(PYTHON) devtools/run_vignettes.py

docs:
	mkdocs build -d site

pages: docs
	@test -f docs/vignettes/index.html || (echo "Run 'make vignettes' first to generate docs/vignettes/" && exit 1)
	@echo "Site ready in site/ (includes docs/vignettes/ static copy)"

setup-venv:
	bash devtools/setup_venv.sh

install-dev: setup-venv