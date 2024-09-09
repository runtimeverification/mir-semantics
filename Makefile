POETRY     := poetry -C kmir
POETRY_RUN := $(POETRY) run

default: build

.PHONY: kmir
kmir:
	$(POETRY) install

build: kmir
	$(POETRY) run kdist -v build mir-semantics.\* -j4

##################################################
# for integration tests: build smir_pretty in-tree

##################################################
# This will change when we set up rustc as a submodule in smir_pretty
smir-pretty-setup: deps/smir_pretty/deps/rust/src

deps/smir_pretty/deps/rust/src:
	cd deps/smir_pretty && make setup

##################################################

smir-pretty: smir-pretty-setup deps/smir_pretty/target/debug/smir_pretty

deps/smir_pretty/target/debug/smir_pretty: deps/smir_pretty
	cd deps/smir_pretty && make build_all

# generate smir and parse given test files (from parameter or run-rs subdirectory)
smir-parse-tests: TESTS = $(shell find kmir/src/tests/integration/data/run-rs -type f -name "*.rs")
smir-parse-tests: SMIR = deps/smir_pretty/run.sh
smir-parse-tests: build smir-pretty
	errors=""; \
	report() { echo $$2; errors="$$errors $$1"; }; \
	for source in ${TESTS}; do \
	    echo -n "$$source: "; \
	    dir=$$(dirname $${source}); \
	    target=$${dir}/$$(basename $${source%.rs}).smir.json; \
	    ${SMIR} -Z no-codegen --out-dir $${dir} $$source \
		&& (echo -n "smir-ed "; \
		    ${POETRY_RUN} convert-from-definition $${target} Pgm > /dev/null \
			&& (echo "and parsed!"; rm $${target}) || report "$$source" "PARSE ERROR!") \
		|| report "$$source" "SMIR ERROR!" ; \
	    done; \
	[ -z "$$errors" ] || (echo "FAILING TESTS:"; printf ". %s\n" $${errors}; exit 1); \
