from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


COMPILETEST_PERMANENT_EXCLUDE = [
    # This crashes with a stack overflow when parsing the json,
    # but passes with sys.setrecursionlimit(40000). However, that
    # uses a lot of memory.
    'pattern/usefulness/issue-88747.mir',
    # Other tests with stack overflows.
    'array-slice-vec/byte-literals.mir',
    'array-slice-vec/estr-slice.mir',
    'array-slice-vec/evec-slice.mir',
    'array-slice-vec/vec-dst.mir',
    'array-slice-vec/vec-matching.mir',
    'associated-type-bounds/union-bounds.mir',
    'augmented-assignments-rpass.mir',
    'backtrace.mir',
    'binding/match-borrowed_str.mir',
    'binding/match-vec-alternatives.mir',
    'coercion/coerce-unify.mir',
    'command/command-exec.mir',
    'command/command-pre-exec.mir',
    'consts/cast-discriminant-zst-enum.mir',
    'consts/const-binops.mir',
    'consts/const-int-overflowing-rpass.mir',
    'consts/const-vecs-and-slices.mir',
    'consts/issue-19244.mir',
    'binding/pat-tuple-1.mir',
    'borrowck/fsu-moves-and-copies.mir',
    'deriving/deriving-cmp-generic-enum.mir',
    'deriving/deriving-cmp-generic-struct.mir',
    'deriving/deriving-cmp-generic-struct-enum.mir',
    'deriving/deriving-cmp-generic-tuple-struct.mir',
    'deriving/deriving-show.mir',
    'deriving/deriving-show-2.mir',
    'destructuring-assignment/tuple_destructure.mir',
    'drop/drop-trait-enum.mir',
    'dynamically-sized-types/dst-field-align.mir',
    'dynamically-sized-types/dst-raw.mir',
    'dynamically-sized-types/dst-trait.mir',
    'dynamically-sized-types/dst-trait-tuple.mir',
    'enum/issue-42747.mir',
    'enum-discriminant/discriminant_value.mir',
    'enum-discriminant/get_discr.mir',
    'for-loop-while/label_break_value.mir',
    'for-loop-while/linear-for-loop.mir',
    'for-loop-while/loop-break-value.mir',
    'generics/issue-32498.mir',
    'macros/issue-98466.mir',
    'macros/macro-literal.mir',
    'macros/rfc-3086-metavar-expr/count-and-length-are-distinct.mir',
    'match/issue-5530.mir',
    'mir/mir_build_match_comparisons.mir',
    'mir/mir_codegen_switch.mir',
    'mir/mir_match_test.mir',
    'numbers-arithmetic/div-mod.mir',
    'numbers-arithmetic/issue-8460.mir',
    'numbers-arithmetic/numeric-method-autoexport.mir',
    'numbers-arithmetic/shift.mir',
    'numbers-arithmetic/shift-various-types.mir',
    'op-assign-builtins-by-ref.mir',
    'or-patterns/basic-switchint.mir',
    'or-patterns/bindings-runpass-1.mir',
    'or-patterns/bindings-runpass-2.mir',
    'or-patterns/or-patterns-default-binding-modes.mir',
    'or-patterns/search-via-bindings.mir',
    'or-patterns/slice-patterns.mir',
    'overloaded/overloaded-autoderef.mir',
    'overloaded/overloaded-deref-count.mir',
    'packed/packed-struct-size.mir',
    'packed/packed-struct-vec.mir',
    'pattern/bindings-after-at/bind-by-copy.mir',
    'range_inclusive.mir',
    'raw-str.mir',
    'self/arbitrary_self_types_raw_pointer_trait.mir',
    'statics/static-impl.mir',
    'std-backtrace.mir',
    'stdlib-unit-tests/issue-21058.mir',
    'stdlib-unit-tests/minmax-stability-issue-23687.mir',
    'stdlib-unit-tests/seq-compare.mir',
    'stdlib-unit-tests/raw-fat-ptr.mir',
    'overloaded/overloaded-deref.mir',
    'struct-enums/borrow-tuple-fields.mir',
    'struct-enums/enum-discrim-manual-sizing.mir',
    'struct-enums/enum-null-pointer-opt.mir',
    'try-block/try-block.mir',
    'type/type-ascription.mir',
    'tuple-index.mir',
    # OOM tests
    'array-slice-vec/subslice-patterns-const-eval-match.mir',
    'array-slice-vec/subslice-patterns-const-eval.mir',
    'array-slice-vec/vec-matching.mir' 'binding/match-vec-alternatives.mir',
    'cast/supported-cast.mir',
    'cleanup-rvalue-scopes.mir',
    'closures/2229_closure_analysis/run_pass/box.mir',
    'closures/deeply-nested_closures.mir',
    'consts/chained-constants-stackoverflow.mir',
    'consts/const-float-bits-conv.mir',
    'consts/const-float-classify.mir',
    'consts/const-int-arithmetic.mir',
    'consts/const_in_pattern/accept_structural.mir',
    'consts/const_let_eq_float.mir',
    'consts/const_let_eq.mir',
    'derives/derive-hygiene.mir',
    'deriving/deriving-associated-types.mir',
    'deriving/issue-58319.mir',
    'drop/drop_order.mir',
    'drop/dropck_legal_cycles.mir',
    'drop/dynamic-drop.mir',
    'dynamically-sized-types/dst-struct.mir',
    'dynamically-sized-types/dst-tuple.mir',
    'enum-discriminant/niche.mir',
    'generator/discriminant.mir',
    'half-open-range-patterns/half-open-range-pats-semantics.mir',
    'iterators/issue-58952-filter-type-length.mir',
    'let-else/let-else-drop-order.mir',
    'macros/issue-99265.mir',
    'macros/rfc-3086-metavar-expr/macro-expansion.mir',
    'mir/mir_codegen_calls.mir',
    'mir/issue-29227.mir',
    'mir/mir_misc_casts.mir',
    'numbers-arithmetic/i128.mir',
    'numbers-arithmetic/num-wrapping.mir',
    'numbers-arithmetic/shift-near-oflo.mir',
    'numbers-arithmetic/u128.mir',
    'recursion/issue-86784.mir',
    'rfcs/rfc1857-drop-order.mir',
    'struct-enums/align-struct.mir',
    'struct-enums/enum-discrim-width-stuff.mir',
    'struct-enums/enum-non-c-like-repr-c.mir',
    'struct-enums/enum-non-c-like-repr-c-and-int.mir',
    'struct-enums/enum-non-c-like-repr-int.mir',
    'struct-enums/small-enums-with-fields.mir',
    'try-operator.mir',
    'ufcs-polymorphic-paths.mir',
    'union/union-packed.mir',
    # Unicode issues
    'cast/cast-rfc0401.mir',
    'utf8_idents.mir',
    'weird-exprs.mir',
]
COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines() + COMPILETEST_PERMANENT_EXCLUDE)
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)
