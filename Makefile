UV     := uv --directory kmir
UV_RUN := $(UV) run

PARALLEL := 4

TOP_DIR    := $(shell pwd)

default: check build

build:
	$(UV_RUN) kdist -v build mir-semantics\.* -j$(PARALLEL)

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
		${UV_RUN} parse $$(realpath $${target}) Pgm > /dev/null \
			&& (echo "and parsed!"; rm $${target}) \
			|| report "$$source" "PARSE ERROR!"; \
		fi; \
	done; \
	[ -z "$$errors" ] || (echo "FAILING TESTS:"; printf ". %s\n" $${errors}; exit 1); \

##################################################
# Targets operating in the `kmir` directory

test-unit:
	$(UV_RUN) pytest $(TOP_DIR)/kmir/src/tests/unit --maxfail=1 --verbose $(TEST_ARGS)

test-integration: build
	$(UV_RUN) pytest $(TOP_DIR)/kmir/src/tests/integration --maxfail=1 --verbose \
			--durations=0 --numprocesses=$(PARALLEL) --dist=worksteal $(TEST_ARGS)

# Checks and formatting

format: autoflake isort black
check: check-flake8 check-mypy check-autoflake check-isort check-black

check-flake8:
	$(UV_RUN) flake8 src

check-mypy:
	$(UV_RUN) mypy src

autoflake:
	$(UV_RUN) autoflake --quiet --in-place src

check-autoflake:
	$(UV_RUN) autoflake --quiet --check src

isort:
	$(UV_RUN) isort src

check-isort:
	$(UV_RUN) isort --check src

black:
	$(UV_RUN) black src

check-black:
	$(UV_RUN) black --check src

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

.PHONY: pyupgrade
pyupgrade: SRC_FILES := $(shell find kmir/src -type f -name '*.py')
pyupgrade:
	$(UV_RUN) pyupgrade --py310-plus $(SRC_FILES)

# Update smir exec tests expectations
.PHONY: update-exec-smir
update-exec-smir:
	UPDATE_EXEC_SMIR=true $(UV_RUN) pytest -k test_exec_smir

# Update checked-in smir.json files (using stable-mir-json dependency and jq)
.PHONY: update-smir-json
update-smir-json: TARGETS = $(shell git ls-files | grep -e ".*\.smir\.json$$")
update-smir-json: SMIR = cargo -q -Z unstable-options -C deps/stable-mir-json run --
update-smir-json: stable-mir-json
	for file in ${TARGETS}; do \
		dir=$$(realpath $$(dirname $$file)); \
		rust=$$dir/$$(basename $${file%.smir.json}.rs); \
		[ -f "$$rust" ] || (echo "Source file $$rust missing."; exit 1); \
		${SMIR} -Zno-codegen --out-dir $$dir $$rust; \
		jq . $$file > $$file.tmp; \
		mv $$file.tmp $$file; \
	done

# run the above two targets in sequence and print a message to the user
.PHONY: update-smir-tests
update-smir-tests: update-smir-json update-exec-smir
	@echo "smir.json files and execute expectations updated."
	@echo "Proof tests might need manual updating"
