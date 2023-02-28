from pathlib import Path
from subprocess import CalledProcessError

import pytest
from pyk.cli_utils import run_process
from pyk.kbuild import KBuild, Package
from pytest import Config, Parser, TempPathFactory

from kmir import KMIR


def pytest_addoption(parser: Parser) -> None:
    print(parser)
    parser.addoption('--no-skip', action='store_true', default=False, help='do not skip tests')


@pytest.fixture(scope='session')
def allow_skip(pytestconfig: Config) -> bool:
    return not pytestconfig.getoption('no_skip')


@pytest.fixture(scope='session')
def kbuild(tmp_path_factory: TempPathFactory) -> KBuild:
    return KBuild(tmp_path_factory.mktemp('kbuild'))


@pytest.fixture(scope='session')
def package() -> Package:
    return Package.create(Path('kbuild.toml'))


@pytest.fixture(scope='session')
def llvm_dir(kbuild: KBuild, package: Package) -> Path:
    return kbuild.kompile(package, 'llvm')


@pytest.fixture(scope='session')
def haskell_dir(kbuild: KBuild, package: Package) -> Path:
    return kbuild.kompile(package, 'haskell')


@pytest.fixture(scope='session')
def mir_parser(llvm_dir: Path) -> Path:
    path_to_mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
    try:
        kast_command = ['kast']
        kast_command += ['--definition', str(llvm_dir)]
        kast_command += ['--module', 'MIR-SYNTAX']
        kast_command += ['--sort', 'Mir']
        kast_command += ['--gen-glr-parser']
        kast_command += [str(path_to_mir_parser)]
        run_process(kast_command)
        return path_to_mir_parser
    except CalledProcessError as err:
        raise ValueError("Couldn't generate Bison parser") from err


@pytest.fixture(scope='session')
def kmir(llvm_dir: Path, haskell_dir: Path, mir_parser: Path) -> KMIR:
    return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir, mir_parser=mir_parser)
