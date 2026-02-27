#!/usr/bin/env bash
set -xeuo pipefail

# Kup relies on cachix registry k-framework-binary.
CACHE="k-framework-binary"
OWNER_REPO="$(git remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')"
REV="$(git rev-parse HEAD)"
# Get the output of the nix build for kmir.
OUT="$(nix build --no-link --json ".#kmir" | jq -r '.[0].outputs.out')"
KEY="github:${OWNER_REPO}/${REV}#kmir"

SUMMARY="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

{
  echo "## Cachix Publish Summary"
  echo "CACHE: $CACHE"
  echo "OUT: $OUT"
  echo "KEY: $KEY"
} >> "$SUMMARY"

# Verify push + pin together. Both can become visible with some delay.
HASH="$(basename "$OUT" | cut -d- -f1)"
PUSH_NARINFO_URL="https://${CACHE}.cachix.org/${HASH}.narinfo"
PIN_API_URL="https://app.cachix.org/api/v1/cache/${CACHE}/pin"
PIN_VISIBILITY_TIMEOUT_SECONDS=120 # 2 minutes
PIN_VISIBILITY_INTERVAL_SECONDS=5 # 5 seconds
PIN_VISIBILITY_ATTEMPTS=$((PIN_VISIBILITY_TIMEOUT_SECONDS / PIN_VISIBILITY_INTERVAL_SECONDS))
for i in $(seq 1 "$PIN_VISIBILITY_ATTEMPTS"); do
  PUSH_STATUS="$(curl -sS -o /dev/null -w '%{http_code}' "$PUSH_NARINFO_URL")" || PUSH_STATUS="000"
  if curl -fsSL "$PIN_API_URL" | jq -e --arg k "$KEY" 'any(.[]; .name == $k)' > /dev/null; then
    PIN_STATUS="pin-ok"
  else
    PIN_STATUS="pin-missing"
  fi

  echo "push-http: ${PUSH_STATUS}" >> "$SUMMARY"
  echo "pin-status: ${PIN_STATUS}" >> "$SUMMARY"

  if [ "$PUSH_STATUS" = "200" ] && [ "$PIN_STATUS" = "pin-ok" ]; then
    echo "cachix-status: push-and-pin-ok" >> "$SUMMARY"
    exit 0
  fi

  echo "cachix-check-attempt-${i}: not-ready, retrying in ${PIN_VISIBILITY_INTERVAL_SECONDS}s" >> "$SUMMARY"
  sleep "$PIN_VISIBILITY_INTERVAL_SECONDS"
done

echo "cachix-status: push-or-pin-missing-after-${PIN_VISIBILITY_TIMEOUT_SECONDS}s" >> "$SUMMARY"
exit 1
