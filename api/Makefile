.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
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
PROJ := imgchkr_api

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: build
build: clean  ## build distribution packages
	python setup.py sdist bdist_wheel

.PHONY: install
install:  ## install package in development mode
	pip install -e .

.PHONY: run
run:  ## run API server in debug mode
	flask --debug --app $(PROJ).cli run --port 5001 --host 0.0.0.0

.PHONY: gunicorn
gunicorn:  ## run API server in debug mode
	gunicorn --bind 0.0.0.0:5001 --workers 3 imgchkr_api.cli:app

.PHONY: clean
clean:  ## remove all build artifacts
	rm -rf build dist htmlcov src/*.egg-info
	find src -type d -name __pycache__ -delete
	find src -type f -name '*.pyc' -delete

.PHONY: test
test:  ## run unit tests
	pytest -vvvs

.PHONY: lint
lint:  ## run lint tests
	pylint --rcfile ../pyproject.toml src/$(PROJ)
	mypy --config-file ../pyproject.toml src/$(PROJ)

.PHONY: cov
cov: ## check code coverage
	pytest -vvvs --cov=$(PROJ)
	coverage report -m
	coverage html

.PHONY: coverage
coverage: cov ## open code coverage report in browser
	$(BROWSER) htmlcov/index.html
