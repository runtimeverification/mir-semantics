from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING

import pytest

from kmir.build import LLVM_DEF_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


def dedent(s: str) -> str:
    from textwrap import dedent

    return dedent(s).strip()


TEST_DATA: Final = (
    (
        r'#decodeValue(b"\x00", typeInfoPrimitiveType(primTypeBool), .Map)',
        'BoolVal ( false )',
    ),
    (
        r'#decodeValue(b"\x01", typeInfoPrimitiveType(primTypeBool), .Map)',
        'BoolVal ( true )',
    ),
    (
        r'#decodeValue(b"\xf1", typeInfoPrimitiveType(primTypeUint(uintTyU8)), .Map)',
        'Integer ( 241 , 8 , false )',
    ),
    (
        r'#decodeValue(b"\xf1\xff", typeInfoPrimitiveType(primTypeUint(uintTyU16)), .Map)',
        'Integer ( 65521 , 16 , false )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff", typeInfoPrimitiveType(primTypeUint(uintTyU32)), .Map)',
        'Integer ( 4294967281 , 32 , false )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeUint(uintTyU64)), .Map)',
        'Integer ( 18446744073709551601 , 64 , false )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeUint(uintTyU128)), .Map)',
        'Integer ( 340282366920938463463374607431768211441 , 128 , false )',
    ),
    (
        r'#decodeValue(b"\xf1", typeInfoPrimitiveType(primTypeInt(intTyI8)), .Map)',
        'Integer ( -15 , 8 , true )',
    ),
    (
        r'#decodeValue(b"\xf1\xff", typeInfoPrimitiveType(primTypeInt(intTyI16)), .Map)',
        'Integer ( -15 , 16 , true )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff", typeInfoPrimitiveType(primTypeInt(intTyI32)), .Map)',
        'Integer ( -15 , 32 , true )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeInt(intTyI64)), .Map)',
        'Integer ( -15 , 64 , true )',
    ),
    (
        r'#decodeValue(b"\xf1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff", typeInfoPrimitiveType(primTypeInt(intTyI128)), .Map)',
        'Integer ( -15 , 128 , true )',
    ),
    (
        dedent(
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
        dedent(
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
    r"""
    Lbl'-LT-'generatedTop'-GT-'{}(
        Lbl'-LT-'kmir'-GT-'{}(
            Lbl'-LT-'k'-GT-'{}(kseq{}($kitem, dotk{}())),
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


@pytest.mark.parametrize(
    'evaluation,expected',
    TEST_DATA,
    ids=[evaluation for evaluation, *_ in TEST_DATA],
)
def test_decode_value(evaluation: str, expected: str, tmp_path: Path) -> None:
    from pyk.kore import match as km
    from pyk.kore.parser import KoreParser
    from pyk.kore.tools import kore_print
    from pyk.ktool.kprint import _kast
    from pyk.ktool.krun import llvm_interpret
    from pyk.utils import chain

    # Given
    kitem_text = _kast(
        definition_dir=LLVM_DEF_DIR,
        expression=evaluation,
        input='rule',
        output='kore',
        sort='Evaluation',
        temp_dir=tmp_path,
    ).stdout
    kore_text = KORE_TEMPLATE.substitute(kitem=kitem_text)
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
    assert expected == actual
