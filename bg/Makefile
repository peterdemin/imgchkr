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
	rm -rf build dist *.egg-info
