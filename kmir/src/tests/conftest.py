from pathlib import Path

import pytest
from filelock import FileLock
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
def kbuild_dir(pytestconfig: Config, tmp_path_factory: TempPathFactory) -> Path:
    existing_kbuild_dir = pytestconfig.getoption('kbuild_dir')
    if not existing_kbuild_dir:
        return tmp_path_factory.mktemp('kbuild')
    else:
        assert isinstance(existing_kbuild_dir, Path)
        return existing_kbuild_dir


@pytest.fixture(scope='session')
def kbuild(kbuild_dir: Path) -> KBuild:
    return KBuild(kbuild_dir)


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
def kmir(kbuild: KBuild, llvm_dir: Path, haskell_dir: Path) -> KMIR:
    with FileLock(str(kbuild.kbuild_dir) + '.lock'):
        return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir)
