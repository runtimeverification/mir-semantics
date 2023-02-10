#!/usr/bin/env bash

set -e

SPEC_MODULE_NAME=$1
shift

KOMPILE_DIR=`dirname $1`
shift

DEFINITION=$(realpath $1)
shift

SPEC=$(realpath $1)
shift

COMMAND=$1
shift

OUTPUT=$(realpath $1)
shift

BREADTH=$1
shift

MODULE_NAME=$(cat $COMMAND | sed 's/^.*--module \([^ ]*\) .*$/\1/')

# SPEC_MODULE_NAME=$(cat $COMMAND | sed 's/^.*--spec-module \([^ ]*\) .*$/\1/')

KOMPILE_TOOL_DIR=kompile-tool

REPL_SCRIPT=$(realpath $KOMPILE_TOOL_DIR/kast.kscript)

KORE_EXEC="$(realpath $KOMPILE_TOOL_DIR/k/bin/kore-exec) --breadth $BREADTH"
KORE_REPL="rlwrap $(realpath $KOMPILE_TOOL_DIR/k/bin/kore-repl) --repl-script $REPL_SCRIPT"

DEBUG_COMMAND="time"
BACKEND_COMMAND=$KORE_EXEC
if [ $# -eq 0 ]; then
  BACKEND_COMMAND=$KORE_EXEC
else
  if [ "$1" == "--debug" ]; then
    shift
    BACKEND_COMMAND=$KORE_REPL
    if [ -n "$KDEBUG" ]; then
      DEBUG_COMMAND="$KDEBUG"
    fi
    if [ $# -ne 0 ]; then
      echo "Unknown argument: '$1'"
      exit 1
    fi
  else
    if [ "$1" == "--" ]; then
      shift
    else
      echo "Unknown argument: '$1'"
      exit 1
    fi
  fi
fi

echo "$@"

PATH=$(realpath $KOMPILE_TOOL_DIR/k/bin):$PATH

cd $(dirname $KOMPILE_DIR)

$DEBUG_COMMAND \
    $BACKEND_COMMAND \
    --version \
    --smt-timeout 4000 \
    $DEFINITION \
    --prove $SPEC \
    --module $MODULE_NAME \
    --spec-module $SPEC_MODULE_NAME \
    --output $OUTPUT \
    "$@"
