.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: install
install:
	pip install -e .

.PHONY: run
run:
	watchmedo auto-restart --directory=src/imgchkr_bg --pattern=*.py --recursive -- \
		celery -A imgchkr_bg.tasks worker --concurrency=1 --loglevel=INFO -E

.PHONY: clean
clean:
	rm -rf build dist htmlcov src/*.egg-info src/*/__pycache__

.PHONY: test
test:  ## run unit tests
	pytest -vvvs

.PHONY: coverage
coverage: ## check code coverage
	pytest -vvvs --cov=imgchkr_api
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html
