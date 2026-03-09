#!/bin/bash
#
# Setup for running property tests with kmir (defaults for p-token).
# - checks out submodule mir-semantics (recursively incl. stable-mir-json)
# - builds stable-mir-json and mir-semantics
# - builds the selected crate with STABLE MIR and links SMIR JSON into artefacts
#
# Usage:
#   ./setup.sh [OPTIONS]
#
# Options (p-token defaults):
#   --skip-submodules           Skip refreshing git submodules (default)
#   --with-submodules           Refresh git submodules
#   -h, --help                  Show help
#
# Overridable via environment (kept minimal):
#   CRATE_DIR         Crate to build (default: ../ for p-token)
#   ARTIFACT_BASENAME Artefact base name (default: p-token)
#
# After running it, one can use:
#   `uv --project mir-semantics/kmir run -- kmir ...`
######################################################################

set -xeuo pipefail

SCRIPT_DIR="$(realpath "$(dirname "$0")")"

SKIP_SUBMODULES=true
CRATE_DIR="${CRATE_DIR:-$(realpath "${SCRIPT_DIR}/..")}"
ARTIFACT_BASENAME="${ARTIFACT_BASENAME:-p-token}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-submodules)
            SKIP_SUBMODULES=true; shift ;;
        --with-submodules)
            SKIP_SUBMODULES=false; shift ;;
        -h|--help)
            echo "Usage: $0 [--skip-submodules]"; exit 0 ;;
        *)
            echo "Unknown option: $1"; echo "Use --help for usage."; exit 1 ;;
    esac
done

cd "${SCRIPT_DIR}"

# Refresh/check out submodules (unless skipped)
if [ "${SKIP_SUBMODULES}" = false ]; then
    echo "Refreshing git submodules..."
    git submodule update --init --recursive
    git submodule status --recursive

    echo "Checking out mir-semantics at origin/feature/p-token..."
    if git -C mir-semantics status --porcelain | grep -v '^?? ' >/dev/null; then
        echo "Skipping checkout: tracked local changes detected."
    else
        git -C mir-semantics fetch origin feature/p-token || true
        git -C mir-semantics checkout --quiet origin/feature/p-token || true
    fi
else
    echo "Skipping git submodule refresh..."
fi

# Ensure stable-mir-json acts as its own workspace to avoid root workspace capture.
# Add an empty [workspace] if missing (idempotent, independent of git status).
SMJ_CARGO_TOML="mir-semantics/deps/stable-mir-json/Cargo.toml"
if ! grep -q '^\[workspace\]' "$SMJ_CARGO_TOML"; then
    printf "\n\n# avoid workspace confusion in token repo\n[workspace]\n" >> "$SMJ_CARGO_TOML"
fi

# Build mir-semantics and stable-mir-json
make -C mir-semantics stable-mir-json build

export RUSTC=$PWD/mir-semantics/deps/.stable-mir-json/release.sh
${RUSTC} --version

# Build selected crate with stable-mir-json (clean first)
pushd "${CRATE_DIR}" >/dev/null
# Force cargo to emit artifacts under the crate's own target directory
export CARGO_TARGET_DIR="${CRATE_DIR}/target"
cargo clean && cargo build --features runtime-verification,assumptions
popd >/dev/null

# Collect SMIR JSONs from the crate's target dir
if ! SMIRS=$(ls "${CRATE_DIR}/target/debug/deps"/*.smir.json 2>/dev/null | sort); then
    echo "[ERROR] No SMIR JSON files found under ${CRATE_DIR}/target/debug/deps."
    echo "        Ensure the crate built with RUSTC wrapper and produced .smir.json outputs."
    exit 3
fi
ls ${SMIRS}

# Link all SMIR JSON and store in artefacts directory
mkdir -p "${ARTEFACTS_DIR:-artefacts}/"
uv --project mir-semantics/kmir run -- kmir link ${SMIRS} -o "${ARTEFACTS_DIR:-artefacts}/${ARTIFACT_BASENAME}.smir.json"
