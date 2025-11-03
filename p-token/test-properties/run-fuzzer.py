#!/usr/bin/env -S uv --project ./mir-semantics/kmir run

from __future__ import annotations

import logging
import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from kmir.kmir import KMIR
from kmir.smir import SMIRInfo
from pyk.kore.tools import kore_print
from pyk.utils import unique

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Iterable
    from typing import Final


# Basic configuration
TEST_PREFIX: Final = 'pinocchio_token_program::entrypoint::'
TEST_PATTERN: Final = re.compile(r'\|\s*(test_[a-zA-Z0-9_]+)\s*\|')
DEFAULT_SEEDS: Final = list(range(10))


# Logger setup
LOGGER: Final = logging.getLogger('ptoken.fuzzer')
LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logging.getLogger('pyk').setLevel(logging.WARNING)


# Paths
CWD: Final = Path().resolve()
ROOT_DIR: Final = (Path(__file__).parent).relative_to(CWD)
TEST_FILE: Final = ROOT_DIR / 'proofs.md'
ARTEFACTS_DIR = ROOT_DIR / 'artefacts'
SMIR_FILE: Final = ARTEFACTS_DIR / 'p-token.smir.json'
TARGET_DIR: Final = ARTEFACTS_DIR / 'fuzzing-kompiled'
RESULT_DIR: Final = ARTEFACTS_DIR / 'fuzzing'


sys.setrecursionlimit(10**8)


def main(
    tests: Iterable[str] | None,
    seeds: Iterable[int] | None,
) -> None:
    LOGGER.info('Setting up fuzzer')

    tests = load_tests(tests)
    LOGGER.info(f'The following tests will be run: {", ".join(tests)}')

    seeds = list(unique(seeds)) if seeds is not None else DEFAULT_SEEDS
    LOGGER.info(
        f'The following seeds will be used: {", ".join(str(seed) for seed in seeds)}'
    )

    smir_info = load_smir()
    LOGGER.info(f'SMIR file parsed: {SMIR_FILE}')

    kmir = load_kmir(smir_info)

    RESULT_DIR.mkdir(exist_ok=True)

    LOGGER.info('Starting fuzzer')
    for test in tests:
        for seed in seeds:
            fuzz(kmir=kmir, smir_info=smir_info, test=test, seed=seed)

    LOGGER.info('Fuzzing complete')


def load_tests(tests: Iterable[str] | None) -> list[str]:
    all_tests = TEST_PATTERN.findall(TEST_FILE.read_text())

    if tests is None:
        return all_tests

    res = list(unique(tests))
    not_found = [test for test in tests if test not in set(all_tests)]
    if not_found:
        raise ValueError(f'Tests not found: {", ".join(not_found)}')

    return res


def load_smir() -> SMIRInfo:
    if not SMIR_FILE.exists():
        raise ValueError(
            f'SMIR file {SMIR_FILE} does not exist. Run ./setup.sh to generate it'
        )
    return SMIRInfo.from_file(SMIR_FILE)


def load_kmir(smir_info: SMIRInfo) -> KMIR:
    return KMIR.from_kompiled_kore(smir_info, target_dir=TARGET_DIR, symbolic=False)


def fuzz(kmir: KMIR, smir_info: SMIRInfo, test: str, seed: int) -> None:
    LOGGER.info(f'Fuzzing: test={test}, seed={seed}')

    pattern = kmir.run_smir(
        smir_info=smir_info,
        start_symbol=f'{TEST_PREFIX}{test}',
        depth=None,
        seed=seed,
    )

    kore_text = pattern.text
    kore_file = RESULT_DIR / f'{test}-{seed}.kore'
    kore_file.write_text(kore_text)
    LOGGER.info(f'KORE file written: {kore_file}')

    pretty_text = kore_print(
        pattern=kore_text,
        definition_dir=TARGET_DIR / 'llvm',
    )
    pretty_file = RESULT_DIR / f'{test}-{seed}.pretty'
    pretty_file.write_text(pretty_text)
    LOGGER.info(f'Pretty file written: {pretty_file}')


def parse_args() -> Namespace:
    parser = ArgumentParser(description='PToken fuzzer')
    parser.add_argument('--tests', nargs='+', action='extend')
    parser.add_argument('--seeds', nargs='+', action='extend', type=int)
    return parser.parse_args()


if __name__ == '__main__':
    ns = parse_args()
    main(tests=ns.tests, seeds=ns.seeds)
