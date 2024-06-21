POETRY     := poetry -C kmir
POETRY_RUN := $(POETRY) run

default: build

.PHONY: kmir
kmir:
	$(POETRY) install

build: kmir
	$(POETRY) run kdist -v build mir-semantics.\* -j4
