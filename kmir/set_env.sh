#! /bin/bash

# run `source set_env.sh` to set these environment vars
export KMIR_LLVM_DIR="$(poetry run kbuild which llvm)"
export KMIR_HASKELL_DIR="$(poetry run kbuild which haskell)"