#!/usr/bin/env bash

set -xueo pipefail

which kmir
kmir --help
kmir --version

# ( \
#      cd kmir/src/tests/integration/data/crate-tests/single-bin/main-crate \
#   && kmir run                                                             \
# )

# kmir prove kmir/src/tests/integration/data/prove-rs/if.rs
