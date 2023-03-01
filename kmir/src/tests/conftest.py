from pathlib import Path

import pytest
from pyk.cli_utils import dir_path
from pyk.kbuild import KBuild, Package
from pytest import Config, Parser, TempPathFactory

from kmir import KMIR


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
def kmir(llvm_dir: Path, haskell_dir: Path) -> KMIR:
    return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir)
