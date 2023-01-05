PROJECT := trending-homebrew
PACKAGE := trending_homebrew
MODULES := $(wildcard $(PACKAGE)/*.py)

#* Variables
.PHONY: check-codestyle clean clean-build clean-dsstore clean-ipynbcheckpoints clean-mypycache clean-pyc clean-test codestyle coverage dist docker-build docker-remove docs formatting help install lint lint/flake8 lint/black mypy poetry-download poetry-remove pre-commit-install test test-all update-dev-deps
.DEFAULT_GOAL := help
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := trending_homebrew
VERSION := latest

# MAIN TASKS ##################################################################

.PHONY: all
all: install

.PHONY: ci
ci: format check test mkdocs ## Run all tasks that determine CI status

.PHONY: dev
dev: install .clean-test ## Continuously run all CI tasks when files chanage
	poetry run sniffer

.PHONY: run
run: install ## Start the program
	poetry run python $(PACKAGE)/__main__.py

.PHONY: shell
shell: install ## Launch an IPython session
	poetry run ipython --ipython-dir=notebooks

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv
DEPENDENCIES := $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
install: $(DEPENDENCIES) .cache

$(DEPENDENCIES): poetry.lock
	@ rm -rf $(VIRTUAL_ENV)/.poetry-*
	@ poetry config virtualenvs.in-project true
	poetry install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

.cache:
	@ mkdir -p .cache

# CHECKS ######################################################################

.PHONY: format
format: install
	poetry run isort $(PACKAGE) tests notebooks
	poetry run black $(PACKAGE) tests notebooks
	@ echo

.PHONY: check
check: install format  ## Run formaters, linters, and static analysis
ifdef CI
	git diff --exit-code
endif
	poetry run mypy $(PACKAGE) tests
	poetry run pylint $(PACKAGE) tests --rcfile=.pylint.ini
	poetry run pydocstyle $(PACKAGE) tests

# TESTS #######################################################################

RANDOM_SEED ?= $(shell date +%s)
FAILURES := .cache/pytest/v/cache/lastfailed

PYTEST_OPTIONS := --random --random-seed=$(RANDOM_SEED)
ifndef DISABLE_COVERAGE
PYTEST_OPTIONS += --cov=$(PACKAGE)
endif
ifdef CI
PYTEST_OPTIONS += --cov-report=xml
endif
PYTEST_RERUN_OPTIONS := --last-failed --exitfirst

.PHONY: test
test: test-all ## Run unit and integration tests

.PHONY: test-unit
test-unit: install
	@ ( mv $(FAILURES) $(FAILURES).bak || true ) > /dev/null 2>&1
	poetry run pytest $(PACKAGE) $(PYTEST_OPTIONS)
	@ ( mv $(FAILURES).bak $(FAILURES) || true ) > /dev/null 2>&1
ifndef DISABLE_COVERAGE
	poetry run coveragespace update unit
endif

.PHONY: test-int
test-int: install
	@ if test -e $(FAILURES); then poetry run pytest tests $(PYTEST_RERUN_OPTIONS); fi
	@ rm -rf $(FAILURES)
	poetry run pytest tests $(PYTEST_OPTIONS)
ifndef DISABLE_COVERAGE
	poetry run coveragespace update integration
endif

.PHONY: test-all
test-all: install
	@ if test -e $(FAILURES); then poetry run pytest $(PACKAGE) tests $(PYTEST_RERUN_OPTIONS); fi
	@ rm -rf $(FAILURES)
	poetry run pytest $(PACKAGE) tests $(PYTEST_OPTIONS)
ifndef DISABLE_COVERAGE
	poetry run coveragespace update overall
endif

.PHONY: read-coverage
read-coverage:
	bin/open htmlcov/index.html

# DOCUMENTATION ###############################################################

MKDOCS_INDEX := site/index.html

.PHONY: docs
docs: mkdocs uml ## Generate documentation and UML
ifndef CI
	@ eval "sleep 3; bin/open http://127.0.0.1:8000" &
	poetry run mkdocs serve
endif

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): docs/requirements.txt mkdocs.yml docs/*.rst
	@ mkdir -p docs
	@ cd docs && ln -sf ../readme.rst index.rst
	@ cd docs/about && ln -sf ../../CHANGELOG.rst changelog.rst
	@ cd docs/about && ln -sf ../../CONTRIBUTING.rst contributing.rst
	@ cd docs/about && ln -sf ../../LICENSE license.rst
	poetry run mkdocs build --clean --strict

docs/requirements.txt: poetry.lock
	@ poetry export --with dev --without-hashes | grep mkdocs > $@
	@ poetry export --with dev --without-hashes | grep pygments >> $@
	@ poetry export --with dev --without-hashes | grep jinja2 >> $@

.PHONY: uml
uml: install docs/*.png
docs/*.png: $(MODULES)
	poetry run pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

# BUILD #######################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl
EXE_FILES := dist/$(PACKAGE).*

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES) pyproject.toml
	rm -f $(DIST_FILES)
	poetry build

.PHONY: exe
exe: install $(EXE_FILES)
$(EXE_FILES): $(MODULES) $(PACKAGE).spec
	# For framework/shared support: https://github.com/yyuu/pyenv/wiki
	poetry run pyinstaller $(PACKAGE).spec --noconfirm --clean

$(PACKAGE).spec:
	poetry run pyi-makespec $(PACKAGE)/__main__.py --onefile --windowed --name=$(PACKAGE)

# RELEASE #####################################################################

.PHONY: upload
upload: dist ## Upload the current version to PyPI
	git diff --name-only --exit-code
	poetry publish
	bin/open https://pypi.org/project/$(PROJECT)

# CLEANUP #####################################################################

.PHONY: clean
clean: .clean-build .clean-docs .clean-test .clean-install ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean
	rm -rf $(VIRTUAL_ENV)

.PHONY: .clean-install
.clean-install:
	find $(PACKAGE) tests -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-docs
.clean-docs:
	rm -rf docs/*.png site

.PHONY: .clean-build
.clean-build:
	rm -rf *.spec dist build

# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help


define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 trending_homebrew tests

check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -ll --recursive trending_homebrew tests

clean: clean-build clean-dsstore clean-ipynbcheckpoints clean-mypycache clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-dsstore:
	find . | grep -E ".DS_Store" | xargs rm -rf

clean-ipynbcheckpoints:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

clean-mypycache:
	find . | grep -E ".mypy_cache" | xargs rm -rf

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py37-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

lint/flake8: ## check style with flake8
	flake8 trending_homebrew tests
lint/black: ## check style with black
	black --check trending_homebrew tests

lint: lint/flake8 lint/black test check-codestyle mypy check-safety ## check style

mypy:
	poetry run mypy --config-file pyproject.toml ./

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

update-dev-deps:
	poetry add -D bandit@latest darglint@latest "isort[colors]@latest" mypy@latest pre-commit@latest pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	poetry add -D --allow-prereleases black@latest

coverage: ## check code coverage quickly with the default Python
	coverage run --source trending_homebrew -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/trending_homebrew.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ trending_homebrew
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

formatting: codestyle

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

poetry-download: ## install Poetry
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

poetry-remove: ## uninstall Poetry
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

pre-commit-install:
	poetry run pre-commit install

install: clean ## install the package to the active Python's site-packages
	python setup.py install
