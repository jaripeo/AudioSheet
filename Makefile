# AudioSheet developer entry points - ARCHITECTURE.md Section 5.1.
#
# Every target runs offline once `make bootstrap` has completed (INV-1). The only
# target that touches the network is `bootstrap` itself.
#
# Toolchain is project-local and pinned:
#   .tooling/          bootstrap venv holding uv, node, npm and pnpm
#   core/.venv/        Python 3.11 environment for the DSP/ML core
#   node_modules/      pnpm workspace for the TypeScript packages

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

ROOT      := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
TOOLING   := $(ROOT)/.tooling
UV        := $(TOOLING)/bin/uv
PNPM      := $(TOOLING)/bin/pnpm
NODE_BIN  := $(TOOLING)/bin
VENV      := $(ROOT)/core/.venv
PY        := $(VENV)/bin/python
PYTEST    := $(VENV)/bin/pytest
RUFF      := $(VENV)/bin/ruff
MYPY      := $(VENV)/bin/mypy

# Python 3.11 is required: madmom and numba wheel availability, and the 3.12+
# distutils removal, both break the audio stack (Section 4.1).
PYTHON_VERSION := 3.11

export PATH := $(NODE_BIN):$(PATH)

.PHONY: help bootstrap bootstrap-py bootstrap-ts schema schema-check \
        lint lint-py lint-ts format test test-py test-ts \
        typecheck verify-models validate-fixture gate clean clean-all

help: ## Show this help
	@echo "AudioSheet - make targets"
	@echo
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | sort \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Bootstrap - the only network-touching target
# ---------------------------------------------------------------------------

bootstrap: bootstrap-py bootstrap-ts ## Install the full toolchain (needs network once)
	@echo "bootstrap complete; every other target now runs offline"

$(UV):
	@echo ">> installing uv into .tooling"
	@python3 -m venv $(TOOLING)
	@$(TOOLING)/bin/pip install --quiet --upgrade pip
	@$(TOOLING)/bin/pip install --quiet uv

bootstrap-py: $(UV) ## Install Python 3.11 and the core dependencies
	@echo ">> installing CPython $(PYTHON_VERSION)"
	@$(UV) python install $(PYTHON_VERSION)
	@echo ">> creating core/.venv"
	@cd core && $(UV) venv --python $(PYTHON_VERSION) .venv
	@echo ">> syncing core dependencies"
	@cd core && $(UV) sync --group dev

bootstrap-ts: $(UV) ## Install Node, pnpm and the workspace dependencies
	@echo ">> installing Node and pnpm into .tooling"
	@$(TOOLING)/bin/pip install --quiet nodejs-wheel-binaries
	@bash scripts/link-node.sh
	@echo ">> installing workspace dependencies"
	@$(PNPM) install --frozen-lockfile || $(PNPM) install

# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

schema: ## Regenerate the JSON Schema and the Pydantic models from the TypeScript
	@$(PY) scripts/gen_schema.py

schema-check: ## Fail if the generated schema artefacts have drifted
	@$(PY) scripts/gen_schema.py --check

# ---------------------------------------------------------------------------
# Lint and types
# ---------------------------------------------------------------------------

lint: lint-py lint-ts ## Lint and typecheck everything

lint-py: ## ruff + mypy --strict over the Python core and scripts
	@echo ">> ruff"
	@$(RUFF) check core/audiosheet core/tests scripts
	@echo ">> ruff format --check"
	@$(RUFF) format --check core/audiosheet core/tests scripts
	@echo ">> mypy --strict"
	@cd core && $(MYPY)
	@$(MYPY) --strict scripts

lint-ts: typecheck ## eslint + tsc --noEmit over the TypeScript workspace
	@echo ">> eslint"
	@$(PNPM) run lint

typecheck: ## tsc --build over every package, plus the test project
	@echo ">> tsc"
	@$(PNPM) run typecheck

format: ## Apply ruff and eslint autofixes
	@$(RUFF) format core/audiosheet core/tests scripts
	@$(RUFF) check --fix core/audiosheet core/tests scripts
	@$(PNPM) run lint:fix

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test: test-py test-ts ## Run every test suite

test-py: ## pytest over the Python core
	@cd core && $(PYTEST)

test-ts: ## vitest over the TypeScript packages
	@$(PNPM) run test

# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------

verify-models: ## Check vendored model digests against models/manifest.json
	@$(PY) scripts/verify_models.py

validate-fixture: ## Run the S6 gate over the hand-authored fixture
	@cd core && $(PY) -m audiosheet.cli validate tests/fixtures/handmade/simple_scale.json

gate: schema-check lint test validate-fixture verify-models ## Run the phase exit gate
	@echo
	@echo "GATE PASSED"

# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

clean: ## Remove build output and caches, keeping the toolchain
	@rm -rf packages/*/dist packages/*/*.tsbuildinfo
	@rm -rf .audiosheet core/.audiosheet
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	@find . -name '.pytest_cache' -type d -prune -exec rm -rf {} +
	@find . -name '.mypy_cache' -type d -prune -exec rm -rf {} +
	@find . -name '.ruff_cache' -type d -prune -exec rm -rf {} +
	@echo "clean"

clean-all: clean ## Also remove the toolchain and every installed dependency
	@rm -rf $(TOOLING) $(VENV) node_modules packages/*/node_modules apps/*/node_modules
	@echo "clean-all"
