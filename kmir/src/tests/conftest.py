from pathlib import Path

import pytest
from pyk.cli_utils import check_file_path, dir_path
from pyk.kbuild import KBuild, Package
from pytest import Config, Parser, TempPathFactory

from kmir import KMIR
from kmir.pyk_utils import generate_mir_bison_parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption('--no-skip', action='store_true', default=False, help='do not skip tests')
    parser.addoption(
        '--kbuild-dir',
        dest='kbuild_dir',
        type=dir_path,
        help='Exisiting kbuild cache directory. Example: `~/.kbuild`. Note: tests will fail of it is invalid. Call `kbuild kompile` to populate it.',
    )


@pytest.fixture(scope='session')
def allow_skip(pytestconfig: Config) -> bool:
    return not pytestconfig.getoption('no_skip')


@pytest.fixture(scope='session')
def kbuild(pytestconfig: Config, tmp_path_factory: TempPathFactory) -> KBuild:
    kbuild_dir = pytestconfig.getoption('kbuild_dir')
    if not kbuild_dir:
        return KBuild(tmp_path_factory.mktemp('kbuild'))
    else:
        assert isinstance(kbuild_dir, Path)
        return KBuild(kbuild_dir)


@pytest.fixture(scope='session')
def package() -> Package:
    return Package.create(Path('kbuild.toml'))


@pytest.fixture(scope='session')
def llvm_dir(pytestconfig: Config, kbuild: KBuild, package: Package) -> Path:
    if pytestconfig.getoption('kbuild_dir'):
        return kbuild.definition_dir(package, 'llvm')
    else:
        return kbuild.kompile(package, 'llvm')


@pytest.fixture(scope='session')
def haskell_dir(pytestconfig: Config, kbuild: KBuild, package: Package) -> Path:
    if pytestconfig.getoption('kbuild_dir'):
        return kbuild.definition_dir(package, 'haskell')
    else:
        return kbuild.kompile(package, 'haskell')


@pytest.fixture(scope='session')
def mir_parser(llvm_dir: Path) -> Path:
    path_to_mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
    try:
        check_file_path(path_to_mir_parser)
    except ValueError:
        # generate the parser if it does not exist
        path_to_mir_parser = generate_mir_bison_parser(llvm_dir, path_to_mir_parser)
    return path_to_mir_parser


@pytest.fixture(scope='session')
def kmir(llvm_dir: Path, haskell_dir: Path, mir_parser: Path) -> KMIR:
    return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir, mir_parser=mir_parser)
