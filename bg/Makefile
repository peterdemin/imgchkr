.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: install
install:
	pip install -e .

.PHONY: run
run:
	watchmedo auto-restart --directory=src/imgchkr_bg --pattern=*.py --recursive -- \
		python -m imgchkr_bg.cli

.PHONY: clean
clean:
	rm -rf build dist htmlcov src/*.egg-info src/*/__pycache__

.PHONY: test
test:  ## run unit tests
	pytest -vvvs

.PHONY: lint
lint:  ## run lint tests
	pylint -j 0 --rcfile ../pyproject.toml src/imgchkr_bg
	mypy --config-file ../pyproject.toml src/imgchkr_bg

.PHONY: coverage
coverage: ## check code coverage
	pytest -vvvs --cov=imgchkr_bg
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html
