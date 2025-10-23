#!/bin/bash
# Wrapper to reuse p-token setup for spl-token
set -euo pipefail

SCRIPT_DIR="$(realpath "$(dirname "$0")")"
PTOKEN_DIR="$(realpath "${SCRIPT_DIR}/../../p-token/test-properties")"

export CRATE_DIR="$(realpath "${SCRIPT_DIR}/..")"  # program root
export ARTIFACT_BASENAME="spl-token"
export ARTEFACTS_DIR="${SCRIPT_DIR}/artefacts"

exec "${PTOKEN_DIR}/setup.sh" "$@"
