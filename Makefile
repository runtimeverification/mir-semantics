POETRY     := poetry -C kmir
POETRY_RUN := $(POETRY) run

default: build

.PHONY: kmir
kmir:
	$(POETRY) install

build: kmir
	$(POETRY) run kdist -v build mir-semantics.\* -j4

##################################################
# for integration tests: build stable-mir-json in-tree

stable-mir-json:
	cd deps/stable-mir-json && cargo build

# generate smir and parse given test files (from parameter or run-rs subdirectory)
smir-parse-tests: TESTS = $(shell find $(PWD)/kmir/src/tests/integration/data/run-rs -type f -name "*.rs")
smir-parse-tests: SMIR = cargo -Z unstable-options -C deps/stable-mir-json run -- 
smir-parse-tests:
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
