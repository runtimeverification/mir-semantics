from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.cterm.show import CTermShow
from pyk.kast.pretty import PrettyPrinter
from pyk.proof.show import APRProofShow

from kmir.kmir import KMIRAPRNodePrinter
from kmir.options import ProveRSOpts, ShowOpts

if TYPE_CHECKING:
    from pyk.proof.reachability import APRProof

    from kmir.kmir import KMIR


THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[3]
PASSING_TSV = REPO_ROOT / 'deps' / 'stable-mir-json' / 'tests' / 'ui' / 'passing.tsv'
SKIP_FILE = THIS_DIR / 'data' / 'stable-mir-ui' / 'skip.txt'
PASSING_TESTS: tuple[str, ...] = tuple(
    line.split('\t', maxsplit=1)[0] for line in PASSING_TSV.read_text().splitlines() if line.strip()
)
SKIP_ENTRIES: frozenset[str] = (
    frozenset(line for line in SKIP_FILE.read_text().splitlines() if line.strip())
    if SKIP_FILE.is_file()
    else frozenset()
)
# In --update-skip mode, each passing case is removed and skip.txt is rewritten immediately.
_update_skip_pending: set[str] = set(SKIP_ENTRIES)


@pytest.fixture(scope='session')
def rust_dir_root() -> Path:
    rust_dir_root_raw = os.environ.get('RUST_DIR_ROOT')
    if not rust_dir_root_raw:
        pytest.fail(
            'RUST_DIR_ROOT is required. Example: RUST_DIR_ROOT=/path/to/rust make test-stable-mir-ui',
            pytrace=False,
        )

    rust_dir_root = Path(rust_dir_root_raw).expanduser().resolve()
    if not rust_dir_root.is_dir():
        pytest.fail(f'RUST_DIR_ROOT is not a directory: {rust_dir_root}', pytrace=False)

    return rust_dir_root


def _is_linear_termination(proof: APRProof) -> bool:
    return proof.passed and len(proof.kcfg.splits()) == 0 and len(proof.kcfg.ndbranches()) == 0


@pytest.mark.timeout(300)
@pytest.mark.parametrize('test_rel_path', PASSING_TESTS, ids=PASSING_TESTS)
def test_stable_mir_ui(
    test_rel_path: str, kmir: KMIR, rust_dir_root: Path, update_skip_mode: bool, tmp_path: Path
) -> None:
    if (test_rel_path in SKIP_ENTRIES) != update_skip_mode:
        pytest.skip()

    try:
        proof = kmir.prove_rs(ProveRSOpts(rust_dir_root / test_rel_path, proof_dir=tmp_path))
        linear = _is_linear_termination(proof)
    except Exception:
        if update_skip_mode:
            pytest.xfail('Error during proof')
        raise

    if update_skip_mode:
        if not linear:
            pytest.xfail('Still failing strict check')
            return
        _update_skip_pending.discard(test_rel_path)
        SKIP_FILE.write_text('\n'.join(sorted(_update_skip_pending)) + '\n' if _update_skip_pending else '')
    elif not linear:
        show_file = tmp_path / 'show.txt'
        cterm_show = CTermShow(PrettyPrinter(kmir.definition).print)
        display_opts = ShowOpts(tmp_path, proof.id, full_printer=False, smir_info=None, omit_current_body=False)
        shower = APRProofShow(kmir.definition, node_printer=KMIRAPRNodePrinter(cterm_show, proof, display_opts))
        show_file.write_text('\n'.join(shower.show(proof)))
        assert proof.passed, f'Proof did not pass. See: {show_file}'
        raise AssertionError(f'Proof is non-linear. See: {show_file}')
