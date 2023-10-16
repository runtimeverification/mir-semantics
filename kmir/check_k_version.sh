#!/usr/bin/env bash

set -euo pipefail

EXPECTED=$(cat ../deps/k_release)
INSTALLED=$(kompile --version | head -1 | cut -f3 -dv)

if grep -q "$EXPECTED" <<< "$INSTALLED"; 
then
    exit 0 
else
    echo "Installed K version $INSTALLED does not match required version $EXPECTED in deps/k_release"
    echo "The correct version can be installed with:"
    echo "    kup install k --version v$EXPECTED"
    exit 1
fi