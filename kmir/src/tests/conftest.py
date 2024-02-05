from pathlib import Path
from typing import Optional

import pytest
from _pytest.config import Notset
from pyk.cli.utils import dir_path, file_path
from pyk.kbuild import KBuild, Project
from pytest import FixtureRequest, Config, Parser, TempPathFactory

from kmir.kmir import KMIR

from .utils import KMIR_DIR


def pytest_addoption(parser: Parser) -> None:
    parser.addoption('--no-skip', action='store_true', default=False, help='do not skip tests')
    parser.addoption(
        '--kbuild-dir',
        dest='kbuild_dir',
        type=dir_path,
        help='Exisiting kbuild cache directory. Example: `~/.kbuild`. Note: tests will fail of it is invalid. Call `kbuild kompile` to populate it.',
    )
    parser.addoption(
        '--report-file',
        dest='report_file',
        type=file_path,
        help='File to report test failures.',
    )
    parser.addoption(
        '--update-expected-output',
        action='store_true',
        default=False,
        help='Write expected output files for proof tests',
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
def report_file(pytestconfig: Config) -> Optional[Path]:
    report_file_path = pytestconfig.getoption('report_file')
    if isinstance(report_file_path, Notset):
        return None
    if not report_file_path:
        return None
    if report_file_path.exists():
        report_file_path.unlink()
    report_file_path.touch()
    return report_file_path

@pytest.fixture
def update_expected_output(request: FixtureRequest) -> bool:
    return request.config.getoption('--update-expected-output')

@pytest.fixture(scope='session')
def kbuild(kbuild_dir: Path) -> KBuild:
    return KBuild(kbuild_dir)


@pytest.fixture(scope='session')
def project() -> Project:
    return Project.load_from_dir(KMIR_DIR)


@pytest.fixture(scope='session')
def llvm_dir(kbuild: KBuild, project: Project) -> Path:
    return kbuild.kompile(project, 'llvm')


@pytest.fixture(scope='session')
def haskell_dir(kbuild: KBuild, project: Project) -> Path:
    return kbuild.kompile(project, 'haskell')


@pytest.fixture(scope='session')
def kmir(llvm_dir: Path, haskell_dir: Path) -> KMIR:
    return KMIR(llvm_dir=llvm_dir, haskell_dir=haskell_dir)
