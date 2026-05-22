"""Run stable-mir-ui tests using kmir run (LLVM backend).

For each test in passing.tsv, compiles the .rs file to SMIR JSON,
runs it with the LLVM backend, and checks that execution reaches #EndProgram.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from kmir.cargo import cargo_get_smir_json
from kmir.kmir import KMIR
from kmir.smir import SMIRInfo

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[3]
PASSING_TSV = REPO_ROOT / 'deps' / 'stable-mir-json' / 'tests' / 'ui' / 'passing.tsv'
SKIP_FILE = THIS_DIR / 'data' / 'stable-mir-ui' / 'skip-exec.txt'
PASSING_TESTS: tuple[str, ...] = tuple(
    line.split('\t', maxsplit=1)[0] for line in PASSING_TSV.read_text().splitlines() if line.strip()
)
SKIP_ENTRIES: frozenset[str] = (
    frozenset(line for line in SKIP_FILE.read_text().splitlines() if line.strip())
    if SKIP_FILE.is_file()
    else frozenset()
)


@pytest.fixture(scope='session')
def rust_dir_root() -> Path:
    rust_dir_root_raw = os.environ.get('RUST_DIR_ROOT')
    if not rust_dir_root_raw:
        pytest.fail(
            'RUST_DIR_ROOT is required. Example: RUST_DIR_ROOT=/path/to/rust ./run-ui-tests.sh',
            pytrace=False,
        )

    rust_dir_root = Path(rust_dir_root_raw).expanduser().resolve()
    if not rust_dir_root.is_dir():
        pytest.fail(f'RUST_DIR_ROOT is not a directory: {rust_dir_root}', pytrace=False)

    return rust_dir_root


@pytest.mark.timeout(300)
@pytest.mark.parametrize('test_rel_path', PASSING_TESTS, ids=PASSING_TESTS)
def test_stable_mir_ui_exec(test_rel_path: str, rust_dir_root: Path, update_skip_mode: bool, tmp_path: Path) -> None:
    if (test_rel_path in SKIP_ENTRIES) != update_skip_mode:
        pytest.skip()

    rs_file = rust_dir_root / test_rel_path

    try:
        smir_data = cargo_get_smir_json(rs_file, save_smir=False)
        smir_info = SMIRInfo(smir_data)
    except Exception:
        if update_skip_mode:
            pytest.xfail('Compilation error')
        raise

    try:
        with tempfile.TemporaryDirectory() as target_dir:
            kmir = KMIR.from_kompiled_kore(smir_info, target_dir=Path(target_dir), symbolic=False)
            result = kmir.run_smir(smir_info)
            result_pretty = kmir.kore_to_pretty(result)
    except Exception:
        if update_skip_mode:
            pytest.xfail('Execution error')
        raise

    reached_end = '#EndProgram ~> .K' in result_pretty

    if update_skip_mode:
        if not reached_end:
            pytest.xfail('Did not reach #EndProgram')
        return

    if not reached_end:
        output_file = tmp_path / 'show.txt'
        output_file.write_text(result_pretty)
        raise AssertionError(f'Execution did not reach #EndProgram. See: {output_file}')
