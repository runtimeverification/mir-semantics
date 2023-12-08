#!/usr/bin/env bash

set -euo pipefail

POETRY_RUN="$1"

if [ "$1" == "llvm" ]; then
    $(POETRY_RUN) kmir init $($(POETRY_RUN) kbuild which llvm)
fi