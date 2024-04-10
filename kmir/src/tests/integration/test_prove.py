import sys
from pathlib import Path
from typing import Optional

import pytest
from filelock import FileLock

from kmir import KMIR
from kmir.prove import ProveOptions, ShowProofOptions, prove, show_proof

from .utils import PROVE_FAIL, PROVE_TEST_DATA, SHOW_TESTS, TEST_DATA_DIR

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
    update_expected_output: bool,
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
        (passed, failed) = prove(
            kmir,
            ProveOptions(
                {
                    'spec_file': spec_file,
                    'save_directory': use_directory,
                    'smt_timeout': 300,
                    'smt_retry_limit': 10,
                }
            ),
        )

        # Check if passed proofs are in show
        if len(passed) != 0:
            for proof in passed:
                if proof.id in SHOW_TESTS:
                    show_res = show_proof(
                        kmir,
                        ShowProofOptions(
                            {
                                'claim_label': proof.id,
                                'definition_dir': use_directory,
                            }
                        ),
                    )
                    assert_or_update_show_output(
                        show_res, TEST_DATA_DIR / f'show/{proof.id}.expected', update=update_expected_output
                    )

        # Check if failed proofs are in show
        if len(failed) != 0:
            fail = False
            for proof in failed:
                if proof.id in SHOW_TESTS:
                    # Show test might be expected to fail
                    show_res = show_proof(
                        kmir,
                        ShowProofOptions(
                            {
                                'claim_label': proof.id,
                                'definition_dir': use_directory,
                            }
                        ),
                    )
                    assert_or_update_show_output(
                        show_res, TEST_DATA_DIR / f'show/{proof.id}.expected', update=update_expected_output
                    )
                else:
                    fail = True

            assert not fail
    except Exception:
        if report_file:
            lock = FileLock(f'{report_file.name}.lock')
            with lock:
                with report_file.open('a') as f:
                    f.write(f'{spec_file.relative_to(TEST_DATA_DIR)}\t{1}\n')
                    # TODO: 1 to be replaced with actual prove result or return code
        raise


def assert_or_update_show_output(show_res: str, expected_file: Path, *, update: bool) -> None:
    assert expected_file.is_file()

    filtered_lines = (
        line
        for line in show_res.splitlines()
        if not line.startswith(
            (
                '    src: ',
                '│   src: ',
                '┃  │   src: ',
                '   │   src: ',
                'module',
            )
        )
    )
    actual_text = '\n'.join(filtered_lines) + '\n'
    expected_text = expected_file.read_text()

    if update:
        expected_file.write_text(actual_text)
    else:
        assert actual_text == expected_text
