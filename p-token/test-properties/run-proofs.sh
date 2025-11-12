#!/bin/bash
#
# Run all start symbols given as arguments (or read them from proofs.md
# table if -a given) with given run options (-o) and timeout (-t).
# Options and defaults:
#   -t NUM   : timeout in seconds (default 2h=7200)
#   -o STRING: prove-rs options. Default "--max-iterations 1000 --max-depth 2000"
#   -a       : run all start symbols from first table in `proofs.md` (1st column)
#   -m       : run all start symbols from multisig table in `proofs.md` (2nd column)
#   -c       : continue existing proofs instead of reloading (which is default)
#   -l FILE  : log output to file "$NAME.PID" instead of stdout
#
# Always runs verbosely, always uses artefacts/proof
# as proof directory
#######################################################################

# Overridable via environment (kept minimal):
# - START_PREFIX: start-symbol prefix (default: pinocchio_token_program::entrypoint::)
# - ARTIFACT_BASENAME: artefact base name (default: p-token)
START_PREFIX="${START_PREFIX:-pinocchio_token_program::entrypoint::}"
ARTIFACT_BASENAME="${ARTIFACT_BASENAME:-p-token}"

ALL_NAMES=$(sed -n -e 's/^| \(test_p[a-zA-Z0-9:_]*\) *|.*/\1/p' proofs.md)
MULTISIG_NAMES=$(sed -n -e 's/^| m | \(test_p[a-zA-Z0-9:_]*\) *|.*/\1/p' proofs.md)

TIMEOUT=7200
PROVE_OPTS="--max-iterations 1000 --max-depth 2000"
RELOAD_OPT="--reload"
LOG_FILE=""

while getopts ":t:o:l:amc" opt; do
    case $opt in
        t)
            TIMEOUT=$OPTARG
            ;;
        o)
            PROVE_OPTS=$OPTARG
            ;;
        l)
            LOG_FILE="$OPTARG.$$"
            ;;
        a)
            TESTS=${ALL_NAMES}
            ;;
        m)
            TESTS=${MULTISIG_NAMES}
            ;;
        c)
            RELOAD_OPT=""
            ;;
        \?)
            echo "[ERROR] Invalid option -$OPTARG." 1>&2
            echo 1>&2
            head -14 $0 1>&2
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Collect tests
if [ -z "$TESTS" ]; then
    if [ "$#" -eq 0 ]; then
        echo "[ERROR] No test function names given. Use -a or provide at least one name." 1>&2
        exit 2
    fi
    TESTS=$@
fi

if [ ! -z "$LOG_FILE" ]; then
    echo "[INFO] Logging output to file $LOG_FILE instead of stdout"
    exec &> $LOG_FILE
fi

set -u

REPO_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

MIR_COMMIT=$(git -C mir-semantics rev-parse --short HEAD 2>/dev/null || echo "unknown")

PROOF_DIR="${ARTIFACTS_DIR:-artefacts}/proof-${REPO_COMMIT}-${MIR_COMMIT}"
mkdir -p "${PROOF_DIR}"

# Default proof status directory to live inside the hashed artefacts/proof directory
PROOF_STATUS_DIR="${PROOF_STATUS_DIR:-${PROOF_DIR}/proof_status}"
mkdir -p "${PROOF_STATUS_DIR}"

if [ -z "${RELOAD_OPT}" ]; then
    MODE="Continuing"
else
    MODE="Re-running"
fi

echo "${MODE} tests ${TESTS} with options '$PROVE_OPTS' and timeout $TIMEOUT"

prefix=${START_PREFIX}

for name in $TESTS; do
    echo "============================== $name ============================"
    start=$prefix$name
    status_file="${PROOF_STATUS_DIR:-proof_status}/${name}.txt"
    start_time=$(date +%s)

    timeout --preserve-status -v ${TIMEOUT} \
        uv --project mir-semantics/kmir run -- \
        kmir prove-rs --smir "${ARTIFACTS_DIR:-artefacts}/${ARTIFACT_BASENAME}.smir.json" \
        --proof-dir "${PROOF_DIR}" --verbose --start-symbol $start ${RELOAD_OPT} ${PROVE_OPTS}
    prove_rc=$?

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    previous_duration=0
    if [ -z "${RELOAD_OPT}" ] && [ -f "${status_file}" ]; then
        previous_duration_line=$(grep -m1 '^total_duration_seconds:' "${status_file}" || true)
        if [ -z "${previous_duration_line}" ]; then
            previous_duration_line=$(grep -m1 '^duration_seconds:' "${status_file}" || true)
        fi
        if [ -n "${previous_duration_line}" ]; then
            previous_duration=$(echo "${previous_duration_line}" | awk -F': *' '{print $2}')
        fi
        if ! [[ "${previous_duration}" =~ ^[0-9]+$ ]]; then
            previous_duration=0
        fi
    fi

    total_duration=$((previous_duration + duration))

    {
        echo "name: ${name}"
        echo "timestamp: $(date -Is)"
        echo "duration_seconds: ${duration}"
        echo "total_duration_seconds: ${total_duration}"
        echo "prove_exit_code: ${prove_rc}"
        echo "repo_commit: ${REPO_COMMIT}"
        echo "mir_semantics_commit: ${MIR_COMMIT}"
        echo ""
    } > "${status_file}"

    uv --project mir-semantics/kmir run -- \
       kmir show --proof-dir "${PROOF_DIR}" ${ARTIFACT_BASENAME}.smir.$start \
       --full-printer > "${PROOF_DIR}/${name}-full.txt"
    uv --project mir-semantics/kmir run -- \
       kmir show --proof-dir "${PROOF_DIR}" ${ARTIFACT_BASENAME}.smir.$start \
       --statistics --leaves >> "${status_file}"
    echo "==========================================================================="
done
