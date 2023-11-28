#!/usr/bin/env bash

set -xueo pipefail

which kmir
kmir --help

kmir parse --output pretty sum-to-n.mir > nix-sum-to-n.parse.out 
git --no-pager diff nix-sum-to-n.parse.out sum-to-n.parse.out

kmir run   --output pretty sum-to-n.mir > nix-sum-to-n.run.out 
# When the K issue below is solved, nix-asum-to-n.run.out will need to be updated
# https://github.com/runtimeverification/k/issues/3604
# Uncomment and run `nix build --extra-experimental-features 'nix-command flakes' --print-build-logs .#kmir-test`
git --no-pager diff nix-sum-to-n.run.out   sum-to-n.run.out

kmir prove --spec-file simple-spec.k