.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -rfv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv

install: ## Install dependencies
	pip install flit
	make clean
	flit install --deps develop --symlink
	pre-commit install

lint: ## Run code linters
	autoflake --remove-all-unused-imports --remove-unused-variables  --ignore-init-module-imports -r easy tests
	black --check easy tests
	isort --check easy tests
	flake8
	mypy easy

fmt format: ## Run code formatters
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports  -r easy tests
	isort easy tests
	black easy tests

test: ## Run tests
	pytest -s -vv

test-cov: ## Run tests with coverage
	pytest --cov=easy --cov-report term

test-cov-full: ## Run tests with coverage term-missing
	pytest --cov=easy --cov-report term-missing tests

doc-deploy: ## Run Deploy Documentation
	make clean
	mkdocs gh-deploy --force

bump:
	bumpversion patch

bump-feat:
	bumpversion feat

bump-major:
	bumpversion major
