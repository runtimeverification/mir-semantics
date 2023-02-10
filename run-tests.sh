#!/usr/bin/env bash

set -e
set -o pipefail

kompile-tool/prepare-k.sh
scripts/gen-syntax-tests.py
bazel test //...
