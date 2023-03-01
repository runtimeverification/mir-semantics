from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


COMPILETEST_PERMANENT_EXCLUDE = [
    # This crashes with a stack overflow when parsing the json,
    # but passes with sys.setrecursionlimit(40000). However, that
    # uses a lot of memory.
    # With Bison parser, it throws 'memory exhausted'
    # It is also included in compiletest-exclude
    'pattern/usefulness/issue-88747.mir',
    ## TODO: the following files parse with the Bison parser,
    ## we should remove them form the list
    # # Other tests with stack overflows.
    # 'array-slice-vec/estr-slice.mir',
    # 'array-slice-vec/evec-slice.mir',
    # 'array-slice-vec/vec-dst.mir',
    # 'associated-type-bounds/union-bounds.mir',
    # 'command/command-exec.mir',
    # 'command/command-pre-exec.mir',
    # 'consts/issue-19244.mir',
    # 'binding/pat-tuple-1.mir',
    # 'deriving/deriving-cmp-generic-enum.mir',
    # 'deriving/deriving-cmp-generic-struct.mir',
    # 'deriving/deriving-cmp-generic-tuple-struct.mir',
    # 'destructuring-assignment/tuple_destructure.mir',
    # 'dynamically-sized-types/dst-field-align.mir',
    # 'dynamically-sized-types/dst-raw.mir',
    # 'dynamically-sized-types/dst-trait.mir',
    # 'dynamically-sized-types/dst-trait-tuple.mir',
    # 'enum/issue-42747.mir',
    # 'enum-discriminant/discriminant_value.mir',
    # 'enum-discriminant/get_discr.mir',
    # 'for-loop-while/label_break_value.mir',
    # 'for-loop-while/loop-break-value.mir',
    # 'generics/issue-32498.mir',
    # 'macros/macro-literal.mir',
    # 'macros/rfc-3086-metavar-expr/count-and-length-are-distinct.mir',
    # 'match/issue-5530.mir',
    # 'mir/mir_codegen_switch.mir',
    # 'mir/mir_match_test.mir',
    # 'numbers-arithmetic/div-mod.mir',
    # 'numbers-arithmetic/issue-8460.mir',
    # 'numbers-arithmetic/numeric-method-autoexport.mir',
    # 'numbers-arithmetic/shift.mir',
    # 'numbers-arithmetic/shift-various-types.mir',
    # 'op-assign-builtins-by-ref.mir',
    # 'or-patterns/bindings-runpass-1.mir',
    # 'or-patterns/bindings-runpass-2.mir',
    # 'or-patterns/search-via-bindings.mir',
    # 'packed/packed-struct-vec.mir',
    # 'pattern/bindings-after-at/bind-by-copy.mir',
    # 'range_inclusive.mir',
    # 'raw-str.mir',
    # 'self/arbitrary_self_types_raw_pointer_trait.mir',
    # 'std-backtrace.mir',
    # 'struct-enums/borrow-tuple-fields.mir',
    # 'struct-enums/enum-discrim-manual-sizing.mir',
    # 'struct-enums/enum-null-pointer-opt.mir',
    # 'try-block/try-block.mir',
    # 'tuple-index.mir',
    # # OOM tests
    # 'closures/2229_closure_analysis/run_pass/box.mir',
    # 'derives/derive-hygiene.mir',
    # 'drop/drop_order.mir',
    # # timeout tests
    # 'oom_unwind.mir',
]
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines() + COMPILETEST_PERMANENT_EXCLUDE)
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)
