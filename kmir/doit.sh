set -euxo pipefail

poetry_run() {
    poetry run "$@"
}

build_pyk() {
    cd kmir
    poetry update
    make
    cd -
}

# run a known Mir program from TEST_DATA_DIR
run() {
    poetry_run kmir run                                      \
        --definition-dir ${KMIR_DEFINITION_DIR}              \
        --output pretty                                      \
        --ignore-return-code                                 \
        ${TEST_DATA_DIR}/"$@"
}

# run a known Mir program from TEST_DATA_DIR with no output
run_none() {
    poetry_run kmir run                                      \
        --definition-dir ${KMIR_DEFINITION_DIR}              \
        --output none                                        \
        ${TEST_DATA_DIR}/"$@"
}

# evaluate a Mir RValue
consteval() {
    poetry_run kmir consteval                                \
        --definition-dir ${KMIR_CONSTEVAL_DEFINITION_DIR}    \
        --output pretty                                      \
        "$1"
}

# parse a known Mir program from TEST_DATA_DIR and output Kore
parse_kore() {
    poetry_run kmir parse                                    \
        --definition-dir ${KMIR_DEFINITION_DIR}              \
        --output kore                                        \
        ${TEST_DATA_DIR}/"$@"
}

# parse a known Mir program from TEST_DATA_DIR and output Pretty
parse_pretty() {
    poetry_run kmir parse                                    \
        --definition-dir ${KMIR_DEFINITION_DIR}              \
        --output pretty                                      \
        ${TEST_DATA_DIR}/"$@"
}

# view the source code of a known Mir program from TEST_DATA_DIR
view() {
  most ${TEST_DATA_DIR}/"$@"
}

# edit the source code of a known Mir program from TEST_DATA_DIR
edit() {
  emacsclient ${TEST_DATA_DIR}/"$@" &
}

if [ -z ${KMIR_DEFINITION_DIR+x} ]; then export KMIR_DEFINITION_DIR=$(poetry_run kbuild which llvm); fi
if [ -z ${KMIR_CONSTEVAL_DEFINITION_DIR+x} ]; then export KMIR_CONSTEVAL_DEFINITION_DIR=$(poetry_run kbuild which consteval-llvm); fi
export TEST_DATA_DIR=$(realpath ./src/tests/integration/test-data/)

if [ $1 == "run" ]; then
    run $2
elif [ $1 == "run-none" ]; then
    run_none "$2"
elif [ $1 == "consteval" ]; then
    consteval "$2"
elif [ $1 == "parse-kore" ]; then
    parse_kore $2
elif [ $1 == "parse-pretty" ]; then
    parse_pretty $2
elif [ $1 == "view" ]; then
    view $2
elif [ $1 == "edit" ]; then
    edit $2
fi
