from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING, NamedTuple

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from pyk.kast.outer import KDefinition
    from pyk.kore.syntax import Pattern

    from kmir.parse.parser import JSON


# Wrap the definition to avoid flooding the output with text from the fixture __repr__ on test failure
class _KDefinition(NamedTuple):
    defn: KDefinition

    def __repr__(self) -> str:
        return repr('KMIR LLVM definition')


@pytest.fixture(scope='module')
def definition_dir() -> Path:
    from kmir.build import LLVM_DEF_DIR

    return LLVM_DEF_DIR


@pytest.fixture(scope='module')
def definition(definition_dir: Path) -> _KDefinition:
    from pyk.kast.outer import read_kast_definition

    defn = read_kast_definition(definition_dir / 'compiled.json')
    return _KDefinition(defn)


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
                        Lbl'-LT-'unwind'-GT-'{}(LblUnwindAction'ColnColn'Unreachable{}())
                        ,Lbl'-LT-'locals'-GT-'{}(Lbl'Stop'List{}())
                    )
                    ,Lbl'-LT-'stack'-GT-'{}(Lbl'Stop'List{}()),
                    Lbl'-LT-'memory'-GT-'{}(Lbl'Stop'Map{}()),
                    Lbl'-LT-'functions'-GT-'{}(Lbl'Stop'Map{}()),
                    Lbl'-LT-'start-symbol'-GT-'{}(Lblsymbol'LParUndsRParUnds'LIB'Unds'Symbol'Unds'String{}(\dv{SortString{}}("")))
                    ,Lbl'-LT-'types'-GT-'{}(Lbl'Stop'Map{}()),
                    Lbl'-LT-'adt-to-ty'-GT-'{}(Lbl'Stop'Map{}())
                ),
                Lbl'-LT-'generatedCounter'-GT-'{}(\dv{SortInt{}}("0"))
            )
        """
    )
)


class _TestData(NamedTuple):
    test_id: str
    bytez: bytes
    types: dict[int, JSON]
    type_info: JSON
    expected: str

    def to_pattern(self, definition: KDefinition) -> Pattern:
        from pyk.kore.prelude import SORT_K_ITEM, bytes_dv, inj, int_dv, map_pattern
        from pyk.kore.syntax import App, SortApp

        return App(
            'LbldecodeValue',
            (),
            (
                bytes_dv(self.bytez),
                self._json_type_info_to_kore(self.type_info, definition),
                map_pattern(
                    *(
                        (
                            inj(SortApp('SortTy'), SORT_K_ITEM, App('Lblty', (), (int_dv(key),))),
                            inj(SortApp('SortTypeInfo'), SORT_K_ITEM, self._json_type_info_to_kore(value, definition)),
                        )
                        for key, value in self.types.items()
                    )
                ),
            ),
        )

    @staticmethod
    def _json_type_info_to_kore(type_info: JSON, definition: KDefinition) -> Pattern:
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


TEST_DATA: Final = load_test_data()


@pytest.mark.parametrize(
    'test_data',
    TEST_DATA,
    ids=[test_id for test_id, *_ in TEST_DATA],
)
def test_decode_value(
    test_data: _TestData,
    definition_dir: Path,
    definition: _KDefinition,
    tmp_path: Path,
) -> None:
    from pyk.kore import match as km
    from pyk.kore.parser import KoreParser
    from pyk.kore.tools import kore_print
    from pyk.ktool.krun import llvm_interpret
    from pyk.utils import chain

    # Given
    evaluation = test_data.to_pattern(definition.defn)
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
