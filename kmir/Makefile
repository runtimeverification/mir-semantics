.PHONY: default all clean build install \
        poetry-install                  \
        test test-unit test-integration \
        format isort autoflake black    \
        check check-isort check-autoflake check-black check-flake8 check-mypy

default: check test-unit

all: check test

clean:
	rm -rf dist .mypy_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;

build:
	poetry build

poetry-install:
	poetry install

POETRY_RUN := poetry run


# Tests

test: test-unit test-integration

test-unit: poetry-install
	$(POETRY_RUN) pytest src/tests/unit --maxfail=1 --verbose $(TEST_ARGS)

test-integration: poetry-install
	$(POETRY_RUN) pytest src/tests/integration --numprocesses=4 --durations=0 --maxfail=1 --verbose $(TEST_ARGS)

compiletest-exclude:
	$(eval TMP := $(shell mktemp))
	$(POETRY_RUN) pytest src/tests/integration --no-skip -k test_compiletest --numprocesses=4 --verbose $(TEST_ARGS) 2>&1 | tee $(TMP)
	grep ^FAILED $(TMP) | grep -oP '(?<=\[).*(?=\])' | sort > src/tests/integration/test-data/compiletest-exclude
	rm $(TMP)
.PHONY: compiletest-exclude

compiletest-run-fail:
	$(POETRY_RUN) pytest src/tests/integration/test_run.py                      \
            --no-skip                                                               \
            -k test_compiletest                                                     \
            --report-file src/tests/integration/test-data/compiletest-run-fail.json \
            $(TEST_ARGS)                                                            \
            2>&1 | tee $(TMP)
.PHONY: compiletest-run-fail

handwritten-run-fail:
	$(POETRY_RUN) pytest src/tests/integration/test_run.py                      \
            -k test_handwritten                                                     \
            --report-file src/tests/integration/test-data/handwritten-run-fail.json \
            $(TEST_ARGS)                                                            \
            2>&1 | tee $(TMP)
.PHONY: handwritten-test-run

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

kbuild-%:
	$(POETRY_RUN) kbuild kompile $*
.PHONY: kbuild-*

