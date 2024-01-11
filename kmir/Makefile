POETRY_RUN := poetry run

.PHONY: default all clean build install \
        poetry-install                  \
        test test-unit test-integration \
        test-integration-parse          \
        test-integration-run            \
        format isort autoflake black    \
        check check-isort check-autoflake check-black check-flake8 check-mypy

default: check test-unit

all: check test

.PHONY: clean
clean:
	rm -rf kdist/;
	rm -rf dist .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} \;

.PHONY: build-backends
build-backends: clean kbuild-llvm kbuild-llvmc kbuild-haskell

.PHONY: build
build: poetry-install build-backends
	poetry build

.PHONY: poetry-install
poetry-install:
	poetry install

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


# Kompilation

kbuild-%: check-k-version
	$(POETRY_RUN) kbuild kompile $*

kwhich-%:
	$(POETRY_RUN) kbuild which $*

# VERSION intended to be empty, unless building with nix
check-k-version:
	./check_k_version.sh $(VERSION)

.PHONY: kbuild-*

# Tests
test: test-unit test-integration

test-unit: poetry-install
	$(POETRY_RUN) pytest src/tests/unit --maxfail=1 --verbose $(TEST_ARGS)

test-integration: poetry-install
	$(POETRY_RUN) pytest -ra                                              \
        src/tests/integration/test_parse.py                               \
        src/tests/integration/test_run.py                                 \
        src/tests/integration/test_prove.py                               \
        --numprocesses=4 --durations=0 --maxfail=1 --verbose $(TEST_ARGS) \

test-integration-parse: poetry-install
	$(POETRY_RUN) pytest src/tests/integration/test_parse.py --numprocesses=4 --durations=0 --maxfail=1 --verbose $(TEST_ARGS)

test-integration-run: poetry-install
	$(POETRY_RUN) pytest src/tests/integration/test_run.py --numprocesses=4 --durations=0 --maxfail=1 --verbose $(TEST_ARGS)

test-integration-prove: poetry-install
	$(POETRY_RUN) pytest src/tests/integration/test_prove.py --numprocesses=4 --durations=0 --maxfail=1 --verbose $(TEST_ARGS)

## Produce *-fail.tsv files by running the tests with --no-skip and no parallelism
compiletest-parse-fail:
	-$(POETRY_RUN) pytest src/tests/integration/test_parse.py                        \
            --tb=line                                                                \
            --no-skip                                                                \
            -k test_compiletest                                                      \
            --report-file src/tests/integration/test-data/compiletest-parse-fail.tsv \
            $(TEST_ARGS);
	sort src/tests/integration/test-data/compiletest-parse-fail.tsv -o src/tests/integration/test-data/compiletest-parse-fail.tsv
.PHONY: compiletest-parse-fail

compiletest-run-fail:
	-$(POETRY_RUN) pytest src/tests/integration/test_run.py                         \
            --timeout=30                                                            \
            --tb=line                                                               \
            --no-skip                                                               \
            -k test_compiletest                                                     \
            --report-file src/tests/integration/test-data/compiletest-run-fail.tsv  \
            $(TEST_ARGS);
	sort src/tests/integration/test-data/compiletest-run-fail.tsv -o src/tests/integration/test-data/compiletest-run-fail.tsv
.PHONY: compiletest-run-fail

handwritten-parse-fail:
	-$(POETRY_RUN) pytest src/tests/integration/test_parse.py                         \
            --tb=line                                                                 \
            --no-skip                                                                 \
            -k test_handwritten_syntax                                                \
            --report-file src/tests/integration/test-data/handwritten-parse-fail.tsv  \
            $(TEST_ARGS);
	sort src/tests/integration/test-data/handwritten-parse-fail.tsv -o src/tests/integration/test-data/handwritten-parse-fail.tsv
.PHONY: handwritten-test-parse

handwritten-run-fail:
	$(POETRY_RUN) pytest src/tests/integration/test_run.py                          \
            --tb=line                                                               \
            --no-skip                                                               \
            -k test_handwritten                                                     \
            --report-file src/tests/integration/test-data/handwritten-run-fail.tsv  \
            $(TEST_ARGS);
	sort src/tests/integration/test-data/handwritten-run-fail.tsv -o src/tests/integration/test-data/handwritten-run-fail.tsv
.PHONY: handwritten-test-run

handwritten-prove-fail:
	$(POETRY_RUN) pytest src/tests/integration/test_prove.py                      \
			--tb=line                                                               \
			--no-skip                                                               \
            -k test_handwritten                                                     \
            --report-file src/tests/integration/test-data/handwritten-prove-fail.tsv  \
            $(TEST_ARGS);
	sort src/tests/integration/test-data/handwritten-prove-fail.tsv -o src/tests/integration/test-data/handwritten-prove-fail.tsv
.PHONY: handwritten-test-prove

## compile the handwritten Rust integration tests to Mir
compile-handwritten-rust:
	make -C src/tests/integration/test-data/handwritten-rust
.PHONY: compile-handwritten-rust

