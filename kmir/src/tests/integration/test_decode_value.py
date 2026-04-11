from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import pytest

from kmir.smir import SMIRInfo

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Final

    from pyk.kast.outer import KDefinition
    from pyk.kore.syntax import Pattern


@pytest.fixture(scope='session')
def definition_dir():  # -> Path:
    import time

    from kmir.kmir import KMIR

    from .utils import TEST_DATA_DIR

    target_dir = TEST_DATA_DIR / 'decode-value' / 'tmp'

    # prevent other processes from concurrently trying to compile
    # (the scope='session' above does not actually work in pytest-xdist)
    lock_file = TEST_DATA_DIR / 'decode-value' / 'tmp.lock'
    try:
        with open(lock_file, 'x') as _:
            # generate and compile an LLVM interpreter with the type-table
            _ = KMIR.from_kompiled_kore(TEST_SMIR, target_dir=target_dir, symbolic=False)
        lock_file.unlink()
    except FileExistsError:
        # wait loop until interpreter exists, max 1min
        secs = 0
        while lock_file.exists() and secs < 60:
            time.sleep(1)
        if not (target_dir / 'llvm' / 'interpreter').exists():
            raise Exception('Waited in vain for interpreter to arise. Exiting') from None

    yield target_dir / 'llvm'

    # should remove the target_dir but other processes are probably still using it
    print(f'Remove {target_dir} if you want to clean up')


@pytest.fixture(scope='session')
def definition(definition_dir: Path) -> KDefinition:
    from pyk.kast.outer import read_kast_definition

    res = read_kast_definition(definition_dir / 'compiled.json')
    _patch_definition(res)
    return res


def _patch_definition(definition: KDefinition) -> None:
    # Monkey patch __repr__ on the fixture to avoid flooding the output on test failure
    cls = definition.__class__
    new_repr = lambda self: repr('KMIR LLVM definition')
    new_cls = type(f'{cls.__name__}WithCustomRepr', (cls,), {'__repr__': new_repr})
    object.__setattr__(definition, '__class__', new_cls)


class _TestData(NamedTuple):
    test_id: str
    bytez: bytes
    types: dict[int, dict[str, Any]]
    type_info: dict[str, Any]
    expected: str

    def to_pattern(self, definition: KDefinition) -> Pattern:
        from pyk.kast.inner import KApply, KSort, Subst
        from pyk.kast.manip import split_config_from
        from pyk.kast.prelude.bytes import bytesToken
        from pyk.kast.prelude.collections import list_empty, map_empty
        from pyk.kast.prelude.utils import token
        from pyk.konvert import kast_to_kore

        from kmir.parse.parser import Parser

        parser = Parser(definition)
        parse_res = parser.parse_mir_json(self.type_info, 'TypeInfo')
        assert parse_res
        type_info_term, _ = parse_res
        evaluation = KApply('decodeValue', bytesToken(self.bytez), type_info_term)

        init_config = definition.init_config(KSort('GeneratedTopCell'))
        _, init_subst = split_config_from(init_config)
        config = Subst(
            {
                **init_subst,
                'K_CELL': evaluation,
                'OWNEDSLOTS_CELL': list_empty(),
                'SLOTSTORE_CELL': map_empty(),
                'GENERATEDCOUNTER_CELL': token(0),
            }
        )(definition.empty_config(KSort('GeneratedTopCell')))

        return kast_to_kore(definition, config, KSort('GeneratedTopCell'))


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

    types = json.loads((TEST_DATA_DIR / 'decode-value' / 'type-table').read_text())
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
    'struct-simple-permuted-fields',
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
    from pyk.kore.tools import kore_print
    from pyk.ktool.krun import llvm_interpret
    from pyk.utils import chain

    if test_data.test_id in SKIP:
        pytest.skip()

    # Given
    init_pattern = test_data.to_pattern(definition)

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


@pytest.fixture(scope='module')
def kmir_definition_dir() -> Path:
    from kmir.build import LLVM_DEF_DIR

    return LLVM_DEF_DIR


@pytest.fixture(scope='module')
def kmir_definition(kmir_definition_dir: Path) -> KDefinition:
    from pyk.kast.outer import read_kast_definition

    res = read_kast_definition(kmir_definition_dir / 'compiled.json')
    _patch_definition(res)
    return res


@pytest.mark.parametrize(
    'test_data',
    TEST_DATA,
    ids=[test_id for test_id, *_ in TEST_DATA],
)
def test_python_decode_value(
    test_data: _TestData,
    kmir_definition_dir: Path,
    kmir_definition: KDefinition,
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
    kore = kast_to_kore(kmir_definition, kast, KSort('Value'))
    actual = kore_print(
        definition_dir=kmir_definition_dir,
        pattern=kore,
        output='pretty',
    )

    # Then
    assert test_data.expected == actual
