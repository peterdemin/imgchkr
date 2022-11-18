.PHONY: virtual_env_set
virtual_env_set:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV not set)
endif

### DEV ###
.PHONY: run_bg
run_api:
	$(MAKE) -C api run

.PHONY: run_bg
run_bg:
	$(MAKE) -C bg run

### DEPENDENCIES ###
.PHONY: install_dev
install_dev:
	$(MAKE) -C api install
	$(MAKE) -C bg install

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
	pip-compile-multi --autoresolve --skip-constraints --use-cache \
		--no-upgrade

.PHONY: upgrade
upgrade: virtual_env_set
	pip-compile-multi --autoresolve --skip-constraints --use-cache

### CI ###
.PHONY: test
test:
	$(MAKE) -C api test
	$(MAKE) -C bg test

.PHONY: coverage
coverage:
	$(MAKE) -C api coverage


### MISC ###
.PHONY: clean
clean:
	$(MAKE) -C api clean
	$(MAKE) -C bg clean
