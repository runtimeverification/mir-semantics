from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'handwritten'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))
HANDWRITTEN_TEST_DATA = tuple(
    (str(input_path.relative_to(TEST_DATA_DIR)), input_path) for input_path in HANDWRITTEN_SYNTAX_FILES
)


COMPILETEST_PARSE_PERMANENT_EXCLUDE = [
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
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_PARSE_FAIL_FILE = TEST_DATA_DIR / 'compiletest-parse-fail.tsv'
COMPILETEST_PARSE_FAIL = {
    str(input_path.split('\t')[0])
    for input_path in (COMPILETEST_PARSE_FAIL_FILE.read_text().splitlines() + COMPILETEST_PARSE_PERMANENT_EXCLUDE)
}
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(TEST_DATA_DIR)), input_path) for input_path in COMPILETEST_FILES
)
