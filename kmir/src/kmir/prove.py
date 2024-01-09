import logging
import sys
from pathlib import Path
from typing import Final

from .kmir import KMIR

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def prove(
    kmir: KMIR,
    spec_file: Path,
    *,
    save_directory: Path | None = None,
    reinit: bool = False,
    depth: int | None = None,
    smt_timeout: int | None = None,
    smt_retry_limit: int | None = None,
    trace_rewrites: bool = False,
    # kore_rpc_command: str | Iterable[str] | None = None,
) -> None:
    _LOGGER.info('Extracting claims from file')

    if kmir.prover:
        kmir_prover = kmir.prover
    else:
        raise ValueError('The prover object in kmir is not initialised.')

    claims = kmir_prover.get_all_claims(spec_file)
    assert claims, ValueError(f'No claims found in file {spec_file}')

    results: list[tuple[str, str]] = []
    failed = 0
    for claim in claims:
        # start an rpc session with KoreServer
        server = kmir_prover.set_kore_server(smt_timeout=smt_timeout, smt_retry_limit=smt_retry_limit)

        with kmir_prover.rpc_session(server, claim.label, trace_rewrites) as session:
            proof = kmir_prover.initialise_a_proof(claim, session, save_directory=save_directory, reinit=reinit)
            res = kmir.prove_driver(proof, session, max_depth=depth)

            _, passed = res
            if passed == 'failed':
                failed += 1
            results.append(res)
    print(results)

    if failed:  # TODO: fail immediately or fail when all claims tried.
        sys.exit(failed)
