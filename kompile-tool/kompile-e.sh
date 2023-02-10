#!/usr/bin/env bash

set -e

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

PARENT_DIR=`dirname $0`

KOMPILE=$PARENT_DIR/kompile_e_tool.runfiles/__main__/kompile-tool/k/bin/kompile
$KOMPILE --backend haskell "${INCLUDES[@]}" -E "$@" > /dev/null
