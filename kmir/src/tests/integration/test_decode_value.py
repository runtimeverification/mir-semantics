from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING, NamedTuple

from kmir.build import LLVM_DEF_DIR
from kmir.smir import SMIRInfo

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Final

    from pyk.kast.outer import KDefinition
    from pyk.kore.syntax import Pattern


@pytest.fixture(scope='session')
def definition_dir() -> Path:
    import shutil
    from .utils import TEST_DATA_DIR
    from kmir.kmir import KMIR

    target_dir = TEST_DATA_DIR / 'decode-value' / '.tmp'

    # generate and compile an LLVM interpreter with the type-table
    _ = KMIR.from_kompiled_kore(TEST_SMIR, target_dir=str(target_dir), symbolic=False)

    yield target_dir / 'llvm'
    print (f'Should now remove {target_dir}')
    # shutil.rmtree(target_dir, ignore_errors=True)


@pytest.fixture(scope='session')
def definition(definition_dir: Path) -> KDefinition:
    from pyk.kast.outer import read_kast_definition

    res = read_kast_definition(definition_dir / 'compiled.json')

    # Monkey patch __repr__ on the fixture to avoid flooding the output on test failure
    cls = res.__class__
    new_repr = lambda self: repr('KMIR LLVM definition')
    new_cls = type(f'{cls.__name__}WithCustomRepr', (cls,), {'__repr__': new_repr})
    object.__setattr__(res, '__class__', new_cls)

    return res


def dedent(s: str) -> str:
    from textwrap import dedent

    return dedent(s).strip()


KORE_TEMPLATE: Final = Template(
    dedent(
        r"""
            Lbl'-LT-'generatedTop'-GT-'{}(
                Lbl'-LT-'kmir'-GT-'{}(
                    Lbl'-LT-'k'-GT-'{}(kseq{}(inj{SortEvaluation{}, SortKItem{}}($evaluation), dotk{}())),
                    Lbl'-LT-'retVal'-GT-'{}(LblnoReturn'Unds'KMIR-CONFIGURATION'Unds'RetVal{}()),
                    Lbl'-LT-'currentFunc'-GT-'{}(Lblty{}(\dv{SortInt{}}("-1"))),
                    Lbl'-LT-'currentFrame'-GT-'{}(
                        Lbl'-LT-'currentBody'-GT-'{}(Lbl'Stop'List{}()),
                        Lbl'-LT-'caller'-GT-'{}(Lblty{}(\dv{SortInt{}}("-1"))),
                        Lbl'-LT-'dest'-GT-'{}(Lblplace{}(Lbllocal{}(\dv{SortInt{}}("-1")),LblProjectionElems'ColnColn'empty{}())),
                        Lbl'-LT-'target'-GT-'{}(LblnoBasicBlockIdx'Unds'BODY'Unds'MaybeBasicBlockIdx{}()),
                        Lbl'-LT-'unwind'-GT-'{}(LblUnwindAction'ColnColn'Unreachable{}()),
                        Lbl'-LT-'locals'-GT-'{}(Lbl'Stop'List{}())
                    ),
                    Lbl'-LT-'stack'-GT-'{}(Lbl'Stop'List{}()),
                    Lbl'-LT-'memory'-GT-'{}(Lbl'Stop'Map{}()),
                    Lbl'-LT-'functions'-GT-'{}(Lbl'Stop'Map{}()),
                    Lbl'-LT-'start-symbol'-GT-'{}(Lblsymbol'LParUndsRParUnds'LIB'Unds'Symbol'Unds'String{}(\dv{SortString{}}(""))),
                    Lbl'-LT-'types'-GT-'{}(Lbl'Stop'Map{}())
                ),
                Lbl'-LT-'generatedCounter'-GT-'{}(\dv{SortInt{}}("0"))
            )
        """
    )
)


class _TestData(NamedTuple):
    test_id: str
    bytez: bytes
    types: dict[int, dict[str, Any]]
    type_info: dict[str, Any]
    expected: str

    def to_pattern(self, definition: KDefinition) -> Pattern:
        from pyk.kore.prelude import bytes_dv
        from pyk.kore.syntax import App

        return App(
            'LbldecodeValue',
            (),
            (
                bytes_dv(self.bytez),
                self._json_type_info_to_kore(self.type_info, definition),
            ),
        )

    @staticmethod
    def _json_type_info_to_kore(type_info: dict[str, Any], definition: KDefinition) -> Pattern:
        from pyk.konvert import kast_to_kore

        from kmir.parse.parser import Parser

        parser = Parser(definition)
        parse_res = parser.parse_mir_json(type_info, 'TypeInfo')
        assert parse_res
        term, sort = parse_res
        return kast_to_kore(definition, term, sort)


def load_test_data() -> tuple[_TestData, ...]:
    from .utils import TEST_DATA_DIR

    test_data_dir = TEST_DATA_DIR / 'decode-value'
    test_files = sorted(test_data_dir.glob('*.json'))
    return tuple(parse_test_data(test_file, test_file.with_suffix('.expected')) for test_file in test_files)


def parse_test_data(test_file: Path, expected_file: Path) -> _TestData:
    import json

    test_data = json.loads(test_file.read_text())
    expected = expected_file.read_text().rstrip()

    return _TestData(
        test_id=test_file.stem,
        bytez=bytes(test_data['bytes']),
        types=dict(test_data['types']),
        type_info=test_data['typeInfo'],
        expected=expected,
    )

def load_test_types():
    import json
    from .utils import TEST_DATA_DIR

    types = json.loads( (TEST_DATA_DIR / 'decode-value' / 'type-table').read_text())
    assert isinstance(types, list)

    smir = {
        'name': 'decode_value',
        'crate-id': 0,
        'allocs': [],
        'debug': None,
        'functions': [],
        'items': [],
        'machine': None,
        'spans': [],
        'uneval_consts': [],
        'types': types,
    }
    return SMIRInfo(smir)


TEST_DATA: Final = load_test_data()
TEST_SMIR: Final = load_test_types()
SKIP: Final = (
    'enum-1-variant-1-field',
    'enum-1-variant-2-fields',
    'enum-2-variants-1-field',
    'enum-option-nonzero-none',
    'enum-option-nonzero-some',
    'str',
)


@pytest.mark.parametrize(
    'test_data',
    TEST_DATA,
    ids=[test_id for test_id, *_ in TEST_DATA],
)
def test_decode_value(
    test_data: _TestData,
    definition_dir: Path,
    definition: KDefinition,
    tmp_path: Path,
) -> None:
    from pyk.kore import match as km
    from pyk.kore.parser import KoreParser
    from pyk.kore.tools import kore_print
    from pyk.ktool.krun import llvm_interpret
    from pyk.utils import chain

    if test_data.test_id in SKIP:
        pytest.skip()

    # Given
    evaluation = test_data.to_pattern(definition)
    kore_text = KORE_TEMPLATE.substitute(evaluation=evaluation.text)
    parser = KoreParser(kore_text)
    init_pattern = parser.pattern()
    assert parser.eof

    # When
    final_pattern = llvm_interpret(definition_dir=definition_dir, pattern=init_pattern)
    value = (
        chain
        >> km.app("Lbl'-LT-'generatedTop'-GT-'")
        >> km.arg("Lbl'-LT-'kmir'-GT-'")
        >> km.arg("Lbl'-LT-'k'-GT-'")
        >> km.arg('kseq')
        >> km.arg('inj')
        >> km.arg(0)
    )(final_pattern)
    actual = kore_print(
        definition_dir=definition_dir,
        pattern=value,
        output='pretty',
    )

    # Then
    assert test_data.expected == actual


@pytest.mark.parametrize(
    'test_data',
    TEST_DATA,
    ids=[test_id for test_id, *_ in TEST_DATA],
)
def test_python_decode_value(
    test_data: _TestData,
    definition_dir: Path,
    definition: KDefinition,
    tmp_path: Path,
) -> None:
    from pyk.kast.inner import KSort
    from pyk.konvert import kast_to_kore
    from pyk.kore.tools import kore_print

    from kmir.decoding import decode_value
    from kmir.ty import Ty, TypeMetadata

    type_info = TypeMetadata.from_raw(test_data.type_info)
    types = {Ty(ty): TypeMetadata.from_raw(data) for ty, data in test_data.types.items()}

    # When
    value = decode_value(
        data=test_data.bytez,
        type_info=type_info,
        types=types,
    )
    kast = value.to_kast()
    kore = kast_to_kore(definition, kast, KSort('Value'))
    actual = kore_print(
        definition_dir=definition_dir,
        pattern=kore,
        output='pretty',
    )

    # Then
    assert test_data.expected == actual
