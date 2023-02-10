#!/usr/bin/env bash

set -e

KOMPILE_DIR=`dirname $1`
shift

ORIGINAL_FILE=$1
shift

PROOF_FILE=$(realpath $1)
shift

MODULE_NAME=$(basename "$ORIGINAL_FILE" | sed 's/\.[^\.]*$//' | tr [:lower:] [:upper:])

KOMPILE_TOOL_DIR=kompile-tool

REPL_SCRIPT=$(realpath $KOMPILE_TOOL_DIR/kast.kscript)

KPROVEX=$(realpath $KOMPILE_TOOL_DIR/k/bin/kprovex)
KORE_REPL=$(realpath $KOMPILE_TOOL_DIR/k/bin/kore-repl)
KORE_EXEC=$(realpath $KOMPILE_TOOL_DIR/k/bin/kore-exec)

TMP_DIR=$(mktemp -d)
trap 'rm -rf -- "$TMP_DIR"' EXIT

cp -RL $KOMPILE_DIR $TMP_DIR
chmod -R a+w $TMP_DIR/*

pushd $TMP_DIR > /dev/null

DEBUG_COMMAND="time"
BACKEND_TOOL=$KORE_EXEC
if [ $# -eq 0 ]; then
  BACKEND_TOOL=$KORE_EXEC
else
  if [ "$1" == "--debug" ]; then
    BACKEND_TOOL="$KORE_REPL --repl-script $REPL_SCRIPT"
    if [ -n "$KDEBUG" ]; then
      DEBUG_COMMAND="$KDEBUG"
    fi
  else
    echo "Unknown argument: '$1'"
    exit 1
  fi
fi

BACKEND_COMMAND="$DEBUG_COMMAND \
    $BACKEND_TOOL \
    --version \
    --smt-timeout 4000 \
"

$KPROVEX \
  --spec-module "$MODULE_NAME" \
  "$PROOF_FILE" \
  --haskell-backend-command "$BACKEND_COMMAND"
> output 2>&1 \
|| ( \
    ( \
      (cat output | grep "core dumped") \
      && (cp output /home/virgil/tmp/kprove; cp * /home/virgil/tmp/kprove; cat output 2>&1; false) \
    ) \
    || (cat output 2>&1; false) \
  )

