#!/usr/bin/env bash

set -xueo pipefail

which kmir
kmir --help

# there is no `kmir version` implemented yet
# kmir version

# ( \
#      cd kmir/src/tests/integration/data/crate-tests/single-bin/main-crate \
#   && kmir run                                                             \
# )

# kmir prove-rs kmir/src/tests/integration/data/prove-rs/if.rs
