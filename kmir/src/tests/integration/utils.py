from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


# Mir files that were written by hand to test *PARSING*. May not be valid for execution.
HANDWRITTEN_MIR_DIR = TEST_DATA_DIR / 'parse-mir'
MIR_PARSE_FILES = tuple(HANDWRITTEN_MIR_DIR.glob('*.mir'))
HANDWRITTEN_PARSE_TEST_DATA = tuple(
    (str(input_path.relative_to(TEST_DATA_DIR)), input_path) for input_path in MIR_PARSE_FILES
)

HANDWRITTEN_PARSE_FAIL_LIST = TEST_DATA_DIR / 'handwritten-parse-fail.tsv'
HANDWRITTEN_PARSE_FAIL = {
    str(input_path.split('\t')[0]) for input_path in HANDWRITTEN_PARSE_FAIL_LIST.read_text().splitlines()
}

# Mir files compiled from handwritten Rust examples for execution test
HANDWRITTEN_RUST_DIR = TEST_DATA_DIR / 'run-rs'
MIR_RUN_FILES = tuple(HANDWRITTEN_RUST_DIR.rglob('*.mir'))
HANDWRITTEN_RUN_TEST_DATA = tuple(
    (str(input_path.relative_to(TEST_DATA_DIR)), input_path) for input_path in MIR_RUN_FILES
)

HANDWRITTEN_RUN_FAIL_FILE = TEST_DATA_DIR / 'handwritten-run-fail.tsv'
HANDWRITTEN_RUN_FAIL = {test.split('\t')[0] for test in HANDWRITTEN_RUN_FAIL_FILE.read_text().splitlines()}


# Mir files dumped from rustc's unit test suite
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
MIR_COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(TEST_DATA_DIR)), input_path) for input_path in MIR_COMPILETEST_FILES
)

COMPILETEST_PARSE_FAIL_FILE = TEST_DATA_DIR / 'compiletest-parse-fail.tsv'
COMPILETEST_PARSE_EXCLUDE = [
    # This crashes with a stack overflow when parsing the json,
    # but passes with sys.setrecursionlimit(40000). However, that
    # uses a lot of memory.
    #
    # With the Bison GLR parser, it throws 'memory exhausted'
    'compiletest-rs/ui/pattern/usefulness/issue-88747.mir',
    # Unicode issues
    'compiletest-rs/ui/cast/cast-rfc0401.mir',
    'compiletest-rs/ui/utf8_idents.mir',
    'compiletest-rs/ui/weird-exprs.mir',
]

COMPILETEST_PARSE_FAIL = {
    str(input_path.split('\t')[0]) for input_path in (COMPILETEST_PARSE_FAIL_FILE.read_text().splitlines())
}

COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail.tsv'
COMPILETEST_RUN_EXCLUDE = [
    # macos only
    'backtrace-apple-no-dsymutil.mir',
    # requires special compilation
    'codegen/init-large-type.mir',
    'macros/macro-with-attrs1.mir',
    'macros/syntax-extension-cfg.mir',
    'mir/mir_overflow_off.mir',
    'numbers-arithmetic/next-power-of-two-overflow-ndebug.mir',
    'panic-runtime/abort.mir',
    'test-attrs/test-vs-cfg-test.mir',
    'codegen/issue-28950.mir',
    # takes too long
    'iterators/iter-count-overflow-debug.mir',
    'iterators/iter-count-overflow-ndebug.mir',
    'iterators/iter-position-overflow-debug.mir',
    'iterators/iter-position-overflow-ndebug.mir',
    'compiletest-rs/ui/consts/promote_evaluation_unused_result.mir',
    # requires special run flags
    'test-attrs/test-filter-multiple.mir',
    # requires environment variables when running
    'exec-env.mir',
    # scanner error
    'new-unicode-escapes.mir',
    'multibyte.mir',
]
COMPILETEST_RUN_FAIL = {
    test.split('\t')[0] for test in COMPILETEST_RUN_FAIL_FILE.read_text().splitlines() + COMPILETEST_RUN_EXCLUDE
}

# proving test data
PROVE_TEST_DIR = TEST_DATA_DIR / 'prove-rs'
MIR_PROVE_FILES = tuple(PROVE_TEST_DIR.rglob('*.k'))
PROVE_TEST_DATA = tuple(
    ( (str(input_path.relative_to(TEST_DATA_DIR)), input_path)) for input_path in MIR_PROVE_FILES
)
""" INITIAL_SPECS = PROVE_TEST_DIR / 'simple-spec.k'
EMPTY_PROGRAM = PROVE_TEST_DIR / 'empty-program.k'
PROVE_TEST_DATA = [INITIAL_SPECS, EMPTY_PROGRAM] """

PROVE_FAIL_FILE = TEST_DATA_DIR / 'handwritten-prove-fail.tsv'
PROVE_FAIL = {test.split('\t')[0] for test in PROVE_FAIL_FILE.read_text().splitlines()}