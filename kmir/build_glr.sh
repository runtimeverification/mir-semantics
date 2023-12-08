#!/usr/bin/env bash

set -euo pipefail

if [ "$1" == "llvm" ]; then
    case $# in

    1)
        kmir init $(kbuild which llvm)
        ;;
    *)
        poetry run kmir init $(poetry run kbuild which llvm)
        ;;
    esac
fi