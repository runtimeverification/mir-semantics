from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


COMPILETEST_PERMANENT_EXCLUDE = [
    # This crashes with a stack overflow when parsing the json,
    # but passes with sys.setrecursionlimit(40000). However, that
    # uses a lot of memory.
    'pattern/usefulness/issue-88747.mir'
]
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines() + COMPILETEST_PERMANENT_EXCLUDE)
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)


COMPILETEST_RUN_PASS_FILE = TEST_DATA_DIR / 'compiletest-run-pass'
COMPILETEST_RUN_PASS = set(COMPILETEST_RUN_PASS_FILE.read_text().splitlines())
COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail'
COMPILETEST_RUN_FAIL = set(COMPILETEST_RUN_FAIL_FILE.read_text().splitlines())
