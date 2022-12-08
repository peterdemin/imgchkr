COMPOSE := docker-compose
COMPOSE_CI := docker-compose -f docker-compose.ci.yml

.PHONY: virtual_env_set
virtual_env_set:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV not set)
endif

PASSTHROUGH := fmt cov lint coverage


### DEV ###
.PHONY: run_bg
run_api:
	$(MAKE) -C api run

.PHONY: run_bg
run_bg:
	$(MAKE) -C bg run

.PHONY: run_redis
run_redis:
	docker run --rm -p 6379:6379 redis:alpine

### DEPENDENCIES ###
.PHONY: install_dev
install_dev: virtual_env_set
	$(MAKE) -C api install
	$(MAKE) -C bg install
	$(MAKE) -C lib install

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
		--no-upgrade -t requirements/local.in
	pip-compile-multi --autoresolve --skip-constraints --use-cache \
		--no-upgrade -t requirements/devpi.in

.PHONY: upgrade
upgrade: virtual_env_set
	pip-compile-multi --autoresolve --skip-constraints --use-cache \
		-t requirements/local.in
	pip-compile-multi --autoresolve --skip-constraints --use-cache \
		-t requirements/devpi.in

### LOCAL QA ###
.PHONY: t
t:
	$(MAKE) -C api test
	$(MAKE) -C bg test
	$(MAKE) -C lib test
	@diff -u api/src/imgchkr_api/constants.py bg/src/imgchkr_bg/constants.py

.PHONY: local-e2e
local-e2e:
	pytest -vvvs \
		--api-host=127.0.0.1 \
		--callback-host=127.0.0.1 \
		testing/test_golden.py

.PHONY: $(PASSTHROUGH)
$(PASSTHROUGH):
	$(MAKE) -C api $@
	$(MAKE) -C bg $@
	$(MAKE) -C lib $@

### DOCKER ###
.PHONY: build
build:
	$(COMPOSE_CI) build

.PHONY: test
test:
	$(COMPOSE_CI) up --abort-on-container-exit --exit-code-from ci ci

.PHONY: test-e2e
test-e2e:
	$(COMPOSE_CI) up --abort-on-container-exit --exit-code-from e2e e2e
	$(COMPOSE_CI) kill

.PHONY: server
server:
	$(COMPOSE) up

.PHONY: dev-server
dev-server:
	$(COMPOSE_CI) up

.PHONY: down
down:
	$(COMPOSE) down --remove-orphans
	$(COMPOSE_CI) down --remove-orphans


### MISC ###
.PHONY: clean
clean:
	$(MAKE) -C api clean
	$(MAKE) -C bg clean
	$(MAKE) -C lib clean
	rm -rf testing/__pycache__
