#!/usr/bin/env bash
#
# --kore-from-path will take the Haskell Backend
#      from the $PATH (as opposed to taking
#      the Haskell Backend in the K package)
#

set -e
set -o pipefail

KOMPILE=`which kompile`
BIN=`dirname $KOMPILE`
RELEASE=`dirname $BIN`
WORKSPACE=$(bazel info | grep "workspace:" | sed 's/^.* //')
ROOT=$WORKSPACE/kompile-tool/k

mkdir -p $ROOT

cp -r $RELEASE/* $ROOT

rm -r $ROOT/share/kframework/pl-tutorial

if [ "$1" == "--kore-from-path" ]
then
  KORE_BIN=$(dirname $(which kore-repl))
  cp $KORE_BIN/kore-* $ROOT/bin
fi
