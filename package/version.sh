#!/usr/bin/env bash

set -xeuo pipefail

notif() { echo "== $@" >&2 ; }
fatal() { echo "[FATAL] $@" ; exit 1 ; }

version_file="package/version"

# Bump the given version by the requested level and write it to the version file.
# Usage: version_bump <version> [major|minor|patch]  (defaults to patch)
# The version counter lives on the `release` branch, so <version> is always the
# prior released version -- see docs/dev/releasing.md
version_bump() {
    local version level version_major version_minor version_patch new_version
    version="$1" ; shift
    level="${1:-patch}"
    version_major="$(echo ${version} | cut --delimiter '.' --field 1)"
    version_minor="$(echo ${version} | cut --delimiter '.' --field 2)"
    version_patch="$(echo ${version} | cut --delimiter '.' --field 3)"
    case "${level}" in
        major) new_version="$((version_major + 1)).0.0"                              ;;
        minor) new_version="${version_major}.$((version_minor + 1)).0"               ;;
        patch) new_version="${version_major}.${version_minor}.$((version_patch + 1))" ;;
        *)     fatal "Unknown bump level: ${level} (expected major, minor or patch)" ;;
    esac
    echo "${new_version}" > "${version_file}"
    notif "Version: ${new_version}"
}

version_sub() {
    local version
    version="$(cat $version_file)"
    sed --in-place 's/^version = ".*"$/version = "'${version}'"/' kmir/pyproject.toml
}

version_command="$1" ; shift

case "${version_command}" in
    bump) version_bump "$@"                      ;;
    sub)  version_sub  "$@"                      ;;
    *)    fatal "No command: ${version_command}" ;;
esac
