#!/usr/bin/env bash

set -xueo pipefail

which kmir
kmir --help

kmir parse --output pretty tests/arithm-simple.mir > tests/nix-arithm-simple.parse.out 
git --no-pager diff tests/nix-arithm-simple.parse.out tests/arithm-simple.parse.out

kmir run   --output pretty tests/arithm-simple.mir > tests/nix-arithm-simple.run.out 
# When the K issue below is solved, tests/nix-arithm-simple.run.out will need to be updated
# https://github.com/runtimeverification/k/issues/3604
# Uncomment and run `nix build --extra-experimental-features 'nix-command flakes' --print-build-logs .#kmir-test`
git --no-pager diff tests/nix-arithm-simple.run.out   tests/arithm-simple.run.out