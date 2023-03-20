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
PROJ := imgchkr_bg
SRC_DIR := src/$(PROJ)
TEST_FILES := (find $(SRC_DIR) -type f -name 'test_*.py' -exec basename {} \;)

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: build
build: clean  ## build distribution packages
	python setup.py sdist bdist_wheel

.PHONY: install
install:  ## install package in development mode
	pip install -e .

.PHONY: run
run:  ## run background worker in debug mode with autoreload
	cd .. && watchmedo auto-restart --directory=bg/src/imgchkr_bg --pattern=*.py --recursive -- \
		python -m imgchkr_bg.cli

.PHONY: clean
clean:  ## remove all build artifacts
	rm -rf build dist htmlcov src/*.egg-info .*_cache .pytype .coverage
	rm -f *.png
	find src -type d -name __pycache__ -delete
	find src -type f -name '*.pyc' -delete

.PHONY: test
test:  ## run unit tests
	pytest -vvvs

.PHONY: lint
lint:  ## run lint tests
	pylint --rcfile ../pyproject.toml $(SRC_DIR)
	mypy --config-file ../pyproject.toml $(SRC_DIR)

.PHONY: cov
cov: ## check code coverage
	pytest -vvvs --cov=$(PROJ) --cov-branch \
		--cov-fail-under=90 --cov-report=
	coverage report --rcfile ../pyproject.toml -m

.PHONY: coverage
coverage: cov ## open code coverage report in browser
	coverage html --rcfile ../pyproject.toml
	$(BROWSER) htmlcov/index.html

.PHONY: fmt
fmt:
	isort $(SRC_DIR)
	black $(SRC_DIR)

.PHONY: uml
uml:
	pyreverse \
		-o png \
		-p $(PROJ) \
		--ignore $$($(TEST_FILES) | paste -sd "," - ) \
		$(SRC_DIR)
