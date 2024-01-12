import sys
from pathlib import Path
from typing import Optional

import pytest
from filelock import FileLock

from kmir import KMIR, prove

from .utils import PROVE_FAIL, PROVE_TEST_DATA, TEST_DATA_DIR

sys.setrecursionlimit(10**8)


@pytest.mark.parametrize(
    ('test_id', 'spec_file'),
    PROVE_TEST_DATA,
    ids=[test_id for test_id, *_ in PROVE_TEST_DATA],
)
def test_handwritten(
    kmir: KMIR,
    test_id: str,
    spec_file: Path,
    tmp_path: Path,
    allow_skip: bool,
    report_file: Optional[Path],
    #  caplog: LogCaptureFixture,
) -> None:
    # caplog.set_level(logging.INFO)

    if allow_skip and test_id in PROVE_FAIL:
        pytest.skip()

    # Given
    tmp_path / 'log.txt'
    use_directory = tmp_path / 'kprove'
    use_directory.mkdir()

    # When
    try:
        prove(
            kmir,
            spec_file=spec_file,
            save_directory=use_directory,
            smt_timeout=300,
            smt_retry_limit=10,
        )
    except Exception:
        if report_file:
            lock = FileLock(f'{report_file.name}.lock')
            with lock:
                with report_file.open('a') as f:
                    f.write(f'{spec_file.relative_to(TEST_DATA_DIR)}\t{1}\n')
                    # TODO: 1 to be replaced with actual prove result or return code
        raise
