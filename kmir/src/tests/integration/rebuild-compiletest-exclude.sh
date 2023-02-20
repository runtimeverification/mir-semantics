#!/usr/bin/env bash

RED="\033[0;31m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
NO_COLOR="\033[0m"

root=$(git rev-parse --show-toplevel)
test_data_dir="$root/kmir/src/tests/integration/test-data"
compiletest_root="$test_data_dir/compiletest-rs"
compiletest_file="$test_data_dir/compiletest-exclude"
passed_file="$test_data_dir/compiletest-passed"
failed_file="$test_data_dir/compiletest-failed"
prepocessor="$root/kmir/src/kmir/preprocessor.py"

work_dir=$(mktemp -d -t compiletest-XXXXXXXX)

if [[ ! "$work_dir" || ! -d "$work_dir" ]]; then
  echo "Could not create temp dir"
  exit 1
fi

# deletes the temp directory
function cleanup {      
  rm -rf "$work_dir"
  echo "Deleted temp working directory $work_dir"
}

# register the cleanup function to be called on the EXIT signal
trap cleanup EXIT

echo -n "" > $passed_file
echo -n "" > $failed_file

cd $work_dir

kompile "$root/kmir/k-src/mir.k" --backend haskell

if [[ $? -ne 0 ]]
then
  exit 1
fi

for f in $(find $compiletest_root -name '*.mir')
do
  echo -n "Parsing $f ..."
  $root/kmir/src/kmir/preprocessor.py $f $work_dir/tmp.mir
  kast --output KORE --sort Mir $work_dir/tmp.mir > /dev/null
  if [[ $? -eq 0 ]]
  then
    echo -e -n "${GREEN}PASSED"
    echo $f >> $passed_file
  else
    echo -e -n "${RED}FAILED"
    echo $f >> $failed_file
  fi
  echo -e "${NO_COLOR}"
done

cat $failed_file | sed 's$^.*/compiletest-rs/ui/$$' | sort > $compiletest_file
