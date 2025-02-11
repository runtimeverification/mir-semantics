POETRY     := poetry -C kmir
POETRY_RUN := $(POETRY) run

TOP_DIR    := $(shell pwd)

default: build

build: poetry-install
	$(POETRY) run kdist -v build mir-semantics.\* -j4

.PHONY: test
test: test-unit test-integration smir-parse-tests

##################################################
# for integration tests: build stable-mir-json in-tree

stable-mir-json:
	cd deps/stable-mir-json && cargo build

# generate smir and parse given test files (from parameter or run-rs subdirectory)
smir-parse-tests: TESTS = $(shell find $(PWD)/kmir/src/tests/integration/data/run-rs -type f -name "*.rs")
smir-parse-tests: SMIR = cargo -q -Z unstable-options -C deps/stable-mir-json run --
smir-parse-tests: # build # commented out for CI's sake
	errors=""; \
	report() { echo $$2; errors="$$errors $$1"; }; \
	for source in ${TESTS}; do \
	    echo -n "$$source: "; \
	    dir=$$(dirname $${source}); \
	    target=$${dir}/$$(basename $${source%.rs}).smir.json; \
	    ${SMIR} -Z no-codegen --out-dir $${dir} $$source \
		&& echo -n "smir-ed " \
		|| report "$$source" "SMIR ERROR!"; \
	    if [ -s $${target} ]; then \
		${POETRY_RUN} convert-from-definition $$(realpath $${target}) Pgm > /dev/null \
			&& (echo "and parsed!"; rm $${target}) \
			|| report "$$source" "PARSE ERROR!"; \
		fi; \
	done; \
	[ -z "$$errors" ] || (echo "FAILING TESTS:"; printf ". %s\n" $${errors}; exit 1); \

##################################################
# Targets operating in the `kmir` directory

.PHONY: poetry-install
poetry-install:
	$(POETRY) install

test-unit: # build # commented out for CI's sake
	$(POETRY_RUN) pytest $(TOP_DIR)/kmir/src/tests/unit --maxfail=1 --verbose $(TEST_ARGS)

test-integration: build
	$(POETRY_RUN) pytest $(TOP_DIR)/kmir/src/tests/integration --maxfail=1 --verbose \
			--durations=0 --numprocesses=4 --dist=worksteal $(TEST_ARGS)

# Checks and formatting

format: autoflake isort black
check: check-flake8 check-mypy check-autoflake check-isort check-black

check-flake8: poetry-install
	$(POETRY_RUN) flake8 src

check-mypy: poetry-install
	$(POETRY_RUN) mypy src

autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --in-place src

check-autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --check src

isort: poetry-install
	$(POETRY_RUN) isort src

check-isort: poetry-install
	$(POETRY_RUN) isort --check src

black: poetry-install
	$(POETRY_RUN) black src

check-black: poetry-install
	$(POETRY_RUN) black --check src

# Coverage

COV_ARGS :=

cov: cov-all

cov-%: TEST_ARGS += --cov=mir_semantics --no-cov-on-fail --cov-branch --cov-report=term

cov-all: TEST_ARGS += --cov-report=html:cov-all-html $(COV_ARGS)
cov-all: test-all

cov-unit: TEST_ARGS += --cov-report=html:cov-unit-html $(COV_ARGS)
cov-unit: test-unit

cov-integration: TEST_ARGS += --cov-report=html:cov-integration-html $(COV_ARGS)
cov-integration: test-integration

##################################################
# Utilities

.PHONY: clean
clean:
	rm -rf kmir/dist kmir/.coverage kmir/cov-* kmir/.mypy_cache kmir/.pytest_cache
	find kmir/ -type d -name __pycache__ -prune -exec rm -rf {} \;

pyupgrade: SRC_FILES := $(shell find kmir/src -type f -name '*.py')
pyupgrade: poetry-install
	$(POETRY_RUN) pyupgrade --py310-plus $(SRC_FILES)

# Update smir exec tests expectations
.PHONY: update-exec-smir
update-exec-smir: poetry-install
	UPDATE_EXEC_SMIR=true $(POETRY_RUN) pytest -k test_exec_smir
