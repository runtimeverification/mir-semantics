from pathlib import Path

import pytest

from kmir import KMIR

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program(input_path)


COMPILETEST_PERMANENT_EXCLUDE = [
    # This crashes with a stack overflow when parsing the json,
    # but passes with sys.setrecursionlimit(40000). However, that
    # uses a lot of memory.
    'pattern/usefulness/issue-88747.mir',
    # Other tests with stack overflows.
    'array-slice-vec/vec-dst.mir',
    'command/command-exec.mir',
    'command/command-pre-exec.mir',
    'binding/pat-tuple-1.mir',
    'destructuring-assignment/tuple_destructure.mir',
    'dynamically-sized-types/dst-field-align.mir',
    'dynamically-sized-types/dst-raw.mir',
    'enum/issue-42747.mir',
    'enum-discriminant/discriminant_value.mir',
    'enum-discriminant/get_discr.mir',
    'for-loop-while/label_break_value.mir',
    'for-loop-while/loop-break-value.mir',
    'generics/issue-32498.mir',
    'macros/macro-literal.mir',
    'macros/rfc-3086-metavar-expr/count-and-length-are-distinct.mir',
    'mir/mir_codegen_switch.mir',
    'mir/mir_match_test.mir',
    'numbers-arithmetic/div-mod.mir',
    'numbers-arithmetic/issue-8460.mir',
    'numbers-arithmetic/numeric-method-autoexport.mir',
    'numbers-arithmetic/shift.mir',
    'numbers-arithmetic/shift-various-types.mir',
    'op-assign-builtins-by-ref.mir',
    'or-patterns/bindings-runpass-1.mir',
    'or-patterns/bindings-runpass-2.mir',
    'or-patterns/search-via-bindings.mir',
    'pattern/bindings-after-at/bind-by-copy.mir',
    'range_inclusive.mir',
    'raw-str.mir',
    'self/arbitrary_self_types_raw_pointer_trait.mir',
    'std-backtrace.mir',
    'struct-enums/borrow-tuple-fields.mir',
    'struct-enums/enum-discrim-manual-sizing.mir',
    'struct-enums/enum-null-pointer-opt.mir',
    'try-block/try-block.mir',
    'tuple-index.mir',
]
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines() + COMPILETEST_PERMANENT_EXCLUDE)
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(
    kmir: KMIR,
    test_id: str,
    input_path: Path,
    tmp_path: Path,
    allow_skip: bool,
) -> None:
    if allow_skip and test_id in COMPILETEST_EXCLUDE:
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # When
    kmir.parse_program(input_path, temp_file=temp_file)
