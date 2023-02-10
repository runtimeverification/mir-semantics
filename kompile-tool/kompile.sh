#!/usr/bin/env bash

set -e

PARENT_DIR=`dirname $0`

INCLUDE_DIRS=$1
shift

INCLUDES=(-I `pwd`)
if [ $INCLUDE_DIRS != ':' ]
then
  for f in `echo "$INCLUDE_DIRS" | sed 's/:/ /g'`
  do
    INCLUDES+=(-I $(pwd)/$f)
  done
fi

OUTPUT_DIR=`dirname $1`
OUTPUT_DIR=`dirname $OUTPUT_DIR`
shift

KOMPILE=$PARENT_DIR/kompile_tool.runfiles/__main__/kompile-tool/k/bin/kompile
$KOMPILE --backend haskell "${INCLUDES[@]}" --directory "$OUTPUT_DIR" "$@"
#  --emit-json
