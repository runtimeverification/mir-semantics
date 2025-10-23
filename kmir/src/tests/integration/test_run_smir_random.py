from __future__ import annotations

import shutil
from dataclasses import dataclass
from functools import cached_property
from random import Random
from typing import TYPE_CHECKING

import pytest
from pyk.kast.prelude.k import GENERATED_TOP_CELL
from pyk.kore.tools import kore_print
from pyk.ktool.krun import llvm_interpret

from kmir.cargo import cargo_get_smir_json
from kmir.kast import RandomMode, make_call_config
from kmir.kmir import KMIR
from kmir.smir import SMIRInfo

from .utils import TEST_DATA_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from pytest import FixtureRequest, TempPathFactory


TEST_ROOT_DIR: Final = (TEST_DATA_DIR / 'run-smir-random').resolve()


@pytest.fixture(params=list(range(10)))
def seed(request: FixtureRequest) -> int:
    return request.param


@pytest.fixture
def random(seed: int) -> Random:
    return Random(seed)


@pytest.fixture(
    scope='module',
    params=[project_dir.name for project_dir in TEST_ROOT_DIR.iterdir()],
)
def project_name(request: FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope='module')
def project_dir(project_name: str, tmp_path_factory: TempPathFactory) -> Path:
    source_dir = TEST_ROOT_DIR / project_name
    target_dir = tmp_path_factory.mktemp(project_name)
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    return target_dir


@pytest.fixture(scope='module')
def smir_info(project_dir: Path) -> SMIRInfo:
    smir_data = cargo_get_smir_json(
        rs_file=project_dir / 'test.rs',
        flags=['--crate-type', 'lib', '--deny', 'warnings'],
        cwd=project_dir,  # TODO: Find a better way to set the .smir.json output path
        save_smir=True,
    )
    return SMIRInfo(smir_data)


@pytest.fixture(scope='module')
def kmir(smir_info: SMIRInfo, project_name: str, tmp_path_factory) -> KMIR:
    target_dir = tmp_path_factory.mktemp(f'{project_name}-kompiled')
    kmir = KMIR.from_kompiled_kore(
        smir_info=smir_info,
        target_dir=target_dir,
        bug_report=None,
        symbolic=False,
    )
    return kmir


@dataclass
class _TestDataHandle:
    project_name: str
    seed: int

    @cached_property
    def expected_init(self) -> str:
        return self.init_file.read_text()

    @cached_property
    def expected_final(self) -> str:
        return self.final_file.read_text()

    @property
    def init_file(self) -> Path:
        return TEST_ROOT_DIR / self.project_name / f'init-{self.seed}.expected'

    @property
    def final_file(self) -> Path:
        return TEST_ROOT_DIR / self.project_name / f'final-{self.seed}.expected'

    def write_init(self, expected: str) -> None:
        self.init_file.write_text(expected)

    def write_final(self, expected: str) -> None:
        self.final_file.write_text(expected)


@pytest.fixture
def handle(project_name: str, seed: int) -> _TestDataHandle:
    return _TestDataHandle(project_name, seed)


def test_run_smir_random(
    kmir: KMIR,
    smir_info: SMIRInfo,
    random: Random,
    handle: _TestDataHandle,
    update_expected_output: bool,
) -> None:
    # When
    init_kast, _ = make_call_config(
        kmir.definition,
        smir_info=smir_info,
        start_symbol='test',
        mode=RandomMode(random),
    )
    init_kore = kmir.kast_to_kore(init_kast, sort=GENERATED_TOP_CELL)
    actual_init = kore_print(
        definition_dir=kmir.definition_dir,
        pattern=init_kore,
        output='pretty',
    )

    # Then
    if update_expected_output:
        handle.write_init(actual_init)
    else:
        assert handle.expected_init == actual_init

    # And when
    final_kore = llvm_interpret(
        definition_dir=kmir.definition_dir,
        pattern=init_kore,
    )
    actual_final = kore_print(
        definition_dir=kmir.definition_dir,
        pattern=final_kore,
        output='pretty',
    )

    # Then
    if update_expected_output:
        handle.write_final(actual_final)
    else:
        assert handle.expected_final == actual_final
