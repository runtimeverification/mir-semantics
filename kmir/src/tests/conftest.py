from pathlib import Path

import pytest
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
def kmir(llvm_dir: Path, haskell_dir: Path) -> KMIR:
    return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir)
