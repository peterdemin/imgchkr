.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: install
install:
	pip install -e .

.PHONY: run
run:
	flask --debug --app imgchkr_api.cli run --port 5001 --host 0.0.0.0

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
