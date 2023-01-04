#* Variables
.PHONY: check-codestyle clean clean-build clean-dsstore clean-ipynbcheckpoints clean-mypycache clean-pyc clean-test codestyle coverage dist docker-build docker-remove docs formatting help install lint lint/flake8 lint/black mypy poetry-download poetry-remove pre-commit-install test test-all update-dev-deps
.DEFAULT_GOAL := help
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := trending_homebrew_3
VERSION := latest



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
