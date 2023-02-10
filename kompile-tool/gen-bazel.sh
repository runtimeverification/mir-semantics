#!/usr/bin/env bash

set -e

workspace=$(bazel info | grep "workspace:" | sed 's/^.* //')

$workspace/kompile-tool/gen-bazel.py "$@"
