.PHONY: virtual_env_set
virtual_env_set:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV not set)
endif

### DEV ###
.PHONY: run_bg
run_api:
	cd api && make run

.PHONY: run_bg
run_bg:
	cd bg && make run

### DEPENDENCIES ###
.PHONY: install_dev
install_dev:
	cd api && make install
	cd bg && make install

.PHONY: install_ext
install_ext: requirements/local.txt virtual_env_set
	pip install -r requirements/local.txt

.PHONY: install
install: install_ext install_dev

.PHONY: sync_ext
sync_ext: requirements/local.txt virtual_env_set
	pip-sync requirements/local.txt

.PHONY: sync
sync: sync_ext install_dev

.PHONY: lock
lock: virtual_env_set
	pip-compile-multi --no-upgrade --autoresolve --skip-constraints

.PHONY: upgrade
upgrade: virtual_env_set
	pip-compile-multi --autoresolve --skip-constraints

### CI ###
.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf build dist pip-compile-multi.egg-info docs/_build
	find . -name "*.pyc" -delete
	find * -type d -name '__pycache__' | xargs rm -rf
