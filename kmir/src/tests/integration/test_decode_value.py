from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING, NamedTuple

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


def dedent(s: str) -> str:
    from textwrap import dedent

    return dedent(s).strip()


class _TestData(NamedTuple):
    test_id: str
    evaluation: str
    expected: str


TEST_DATA: Final = (
    _TestData(
        test_id='bool-false',
        evaluation=r'#decodeValue(b"\x00", typeInfoPrimitiveType(primTypeBool), .Map)',
        expected='BoolVal ( false )',
    ),
    _TestData(
        test_id='bool-true',
        evaluation=r'#decodeValue(b"\x01", typeInfoPrimitiveType(primTypeBool), .Map)',
        expected='BoolVal ( true )',
    ),
    _TestData(
        test_id='u8',
        evaluation=r'#decodeValue(b"\xf1", typeInfoPrimitiveType(primTypeUint(uintTyU8)), .Map)',
        expected='Integer ( 241 , 8 , false )',
    ),
    _TestData(
        test_id='u16',
        evaluation=r'#decodeValue(b"\xf1\xff", typeInfoPrimitiveType(primTypeUint(uintTyU16)), .Map)',
        expected='Integer ( 65521 , 16 , false )',
    ),
    _TestData(
        test_id='u32',
        evaluation=r'#decodeValue(b"\xf1\xff\xff\xff", typeInfoPrimitiveType(primTypeUint(uintTyU32)), .Map)',
        expected='Integer ( 4294967281 , 32 , false )',
    ),
    _TestData(
        test_id='u64',
        evaluation=r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeUint(uintTyU64)), .Map)',
        expected='Integer ( 18446744073709551601 , 64 , false )',
    ),
    _TestData(
        test_id='u128',
        evaluation=dedent(
            r"""
                #decodeValue(
                    b"\xf1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
                    typeInfoPrimitiveType(primTypeUint(uintTyU128)),
                    .Map
                )
            """
        ),
        expected='Integer ( 340282366920938463463374607431768211441 , 128 , false )',
    ),
    _TestData(
        test_id='i8',
        evaluation=r'#decodeValue(b"\xf1", typeInfoPrimitiveType(primTypeInt(intTyI8)), .Map)',
        expected='Integer ( -15 , 8 , true )',
    ),
    _TestData(
        test_id='i16',
        evaluation=r'#decodeValue(b"\xf1\xff", typeInfoPrimitiveType(primTypeInt(intTyI16)), .Map)',
        expected='Integer ( -15 , 16 , true )',
    ),
    _TestData(
        test_id='i32',
        evaluation=r'#decodeValue(b"\xf1\xff\xff\xff", typeInfoPrimitiveType(primTypeInt(intTyI32)), .Map)',
        expected='Integer ( -15 , 32 , true )',
    ),
    _TestData(
        test_id='i64',
        evaluation=r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeInt(intTyI64)), .Map)',
        expected='Integer ( -15 , 64 , true )',
    ),
    _TestData(
        test_id='i128',
        evaluation=dedent(
            r"""
                #decodeValue(
                    b"\xf1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
                    typeInfoPrimitiveType(primTypeInt(intTyI128)),
                    .Map
                )
            """
        ),
        expected='Integer ( -15 , 128 , true )',
    ),
    _TestData(
        test_id='array-u8-const-len',
        evaluation=dedent(
            r"""
                #decodeValue(
                    b"\x00\x01\x02\x03",
                    typeInfoArrayType(
                        ty(0),
                        someTyConst(
                            tyConst(
                                tyConstKindValue(
                                    ty(0),
                                    allocation(
                                        b"\x04",
                                        provenanceMap(.ProvenanceMapEntries),
                                        align(1),
                                        mutabilityNot
                                    )
                                ),
                                tyConstId(100)
                            )
                        )
                    ),
                    ty(0) |-> typeInfoPrimitiveType(primTypeUint(uintTyU8))
                )
            """
        ),
        expected=dedent(
            """
                Range ( ListItem ( Integer ( 0 , 8 , false ) )
                ListItem ( Integer ( 1 , 8 , false ) )
                ListItem ( Integer ( 2 , 8 , false ) )
                ListItem ( Integer ( 3 , 8 , false ) ) )
            """
        ),
    ),
    _TestData(
        test_id='array-u8-implicit-len',
        evaluation=dedent(
            r"""
                #decodeValue(
                    b"\x00\x01\x02\x03",
                    typeInfoArrayType(ty(0), noTyConst),
                    ty(0) |-> typeInfoPrimitiveType(primTypeUint(uintTyU8))
                )
            """
        ),
        expected=dedent(
            """
                Range ( ListItem ( Integer ( 0 , 8 , false ) )
                ListItem ( Integer ( 1 , 8 , false ) )
                ListItem ( Integer ( 2 , 8 , false ) )
                ListItem ( Integer ( 3 , 8 , false ) ) )
            """
        ),
    ),
)

KORE_TEMPLATE: Final = Template(
    dedent(
        r"""
            Lbl'-LT-'generatedTop'-GT-'{}(
                Lbl'-LT-'kmir'-GT-'{}(
                    Lbl'-LT-'k'-GT-'{}(kseq{}(inj{SortEvaluation{}, SortKItem{}}($kitem), dotk{}())),
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


@pytest.mark.parametrize(
    'test_data',
    TEST_DATA,
    ids=[test_id for test_id, *_ in TEST_DATA],
)
def test_decode_value(test_data: _TestData, tmp_path: Path) -> None:
    from pyk.kore import match as km
    from pyk.kore.parser import KoreParser
    from pyk.kore.tools import kore_print
    from pyk.ktool.krun import llvm_interpret
    from pyk.utils import chain

    from kmir.build import LLVM_DEF_DIR
    from kmir.kmir import KMIR

    # Given
    kmir = KMIR(LLVM_DEF_DIR)
    input_file = tmp_path / 'term.pretty'
    input_file.write_text(test_data.evaluation)
    _returncode, kitem = kmir.kparse_into_kore(
        input_file=input_file,
        sort='Evaluation',
    )
    kore_text = KORE_TEMPLATE.substitute(kitem=kitem.text)
    parser = KoreParser(kore_text)
    init_pattern = parser.pattern()
    assert parser.eof

    # When
    final_pattern = llvm_interpret(definition_dir=LLVM_DEF_DIR, pattern=init_pattern)
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
        definition_dir=LLVM_DEF_DIR,
        pattern=value,
        output='pretty',
    )

    # Then
    assert test_data.expected == actual
