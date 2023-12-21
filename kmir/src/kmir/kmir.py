__all__ = ['KMIR']

import logging
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Callable, Final, Iterable, Iterator, Optional, final

from pyk.cterm import CTerm
from pyk.kast.inner import KInner
from pyk.kast.outer import KClaim
from pyk.kcfg import KCFG, KCFGExplore
from pyk.kore.parser import KoreParser
from pyk.kore.prelude import SORT_K_ITEM, inj, top_cell_initializer
from pyk.kore.rpc import KoreClient, KoreServer
from pyk.kore.syntax import Pattern, SortApp
from pyk.kore.tools import PrintOutput, kore_print
from pyk.ktool.kprove import KProve
from pyk.proof import APRProof, APRProver, EqualityProof, EqualityProver
from pyk.proof.proof import Proof, Prover  # not exported explicitly
from pyk.utils import BugReport, check_file_path, run_process

from .semantics import KMIRSemantics
from .utils import ensure_ksequence_on_k_cell, is_functional

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


@final
@dataclass(frozen=True)
class KMIRProve:
    haskell_dir: Path
    mir_prove: KProve
    # mir_konfig: KMIRSemantics
    backend_cmd: list[str]  # `kore-rpc` for legacy backend; `kore-booster-rpc ` for booster backend with dylib supplied
    bug_report: Optional[BugReport] = None
    # explore: Iterator[KCFGExplore]

    # use_booster should be removed in future
    def __init__(self, haskell_dir: Path, use_booster: bool, br: Optional[BugReport]):
        mir_prove = KProve(haskell_dir)  # TODO: should pass in main-file, bug_report, save_directory etc.

        if use_booster:
            ext: str
            match sys.platform:
                case 'linux':
                    ext = 'so'
                case 'darwin':
                    ext = 'dylib'
                case _:
                    raise ValueError('Unsupported platform: {sys.platform}')

            kompiled_dir = self.haskell_dir / '..'
            dylib = kompiled_dir / 'llvmc' / f'interpreter.{ext}'
            check_file_path(dylib)

            # TODO: Should use llvmc dir
            llvm_dir = kompiled_dir / 'llvm'
            llvm_definition = llvm_dir / 'llvm' / 'definition.kore'
            llvm_dt = llvm_dir / 'dt'

            cmd = ['kore-rpc-booster', '--llvm-backend-library', str(dylib)]
            # _gather_booster_report(llvm_dir, llvm_definition, llvm_dt, br) if br else None

            if br:
                br.add_file(llvm_definition, Path('llvm_definition/definition.kore'))
                br.add_file(llvm_dt, Path('llvm_definition/dt'))
                llvm_version = run_process('llvm-backend-version', pipe_stderr=True, logger=_LOGGER).stdout.strip()
                br.add_file_contents(llvm_version, Path('llvm_version.txt'))
        else:
            cmd = ['kore-rpc']

        object.__setattr__(self, 'haskell_dir', haskell_dir)
        object.__setattr__(self, 'mir_prove', mir_prove)
        object.__setattr__(self, 'backend_cmd', cmd)
        object.__setattr__(self, 'bug_report', br)

    # start the kore server, `backend_cmd` decide which server to start.
    def set_kore_server(
        self,
        *,
        port: int | None = None,  # it is a positional argument for KoreClient and cannot be None.
        smt_timeout: int | None = None,
        smt_retry_limit: int | None = None,
    ) -> KoreServer:
        # Old way of handling KCFGExplore, to be removed
        return KoreServer(
            self.haskell_dir,
            self.mir_prove.main_module,
            port=port,
            command=self.backend_cmd,
            bug_report=self.bug_report,
            smt_timeout=smt_timeout,
            smt_retry_limit=smt_retry_limit,
        )

    @contextmanager
    def rpc_session(self, server: KoreServer, claim_id: str, trace_rewrites: bool = False) -> Iterator[KCFGExplore]:
        with server as server:
            with KoreClient('localhost', server.port, bug_report=self.bug_report) as client:
                yield KCFGExplore(
                    kprint=self.mir_prove,
                    kore_client=client,
                    kcfg_semantics=KMIRSemantics(),
                    id=claim_id,
                    trace_rewrites=trace_rewrites,
                )

    # A wrapper on KProve's get_claims
    def get_all_claims(self, spec_file: Path) -> list[KClaim]:
        return self.mir_prove.get_claims(spec_file)

    def initialise_a_proof(
        self,
        claim: KClaim,
        kcfg_explore: KCFGExplore,
        *,
        save_directory: Optional[Path] = None,
        reinit: bool = False,
    ) -> Proof:
        # TODO: rewrite
        proof_problem: Proof
        kprove = self.mir_prove

        if is_functional(claim):
            if save_directory is not None and not reinit and EqualityProof.proof_exists(claim.label, save_directory):
                proof_problem = EqualityProof.read_proof_data(save_directory, claim.label)
            else:
                proof_problem = EqualityProof.from_claim(claim, kprove.definition, proof_dir=save_directory)
        else:
            if save_directory is not None and not reinit and APRProof.proof_exists(claim.label, save_directory):
                proof_problem = APRProof.read_proof_data(save_directory, claim.label)

            else:
                _LOGGER.info(f'Converting claim to KCFG: {claim.label}')
                kcfg, init_node_id, target_node_id = KCFG.from_claim(kprove.definition, claim)

                new_init = ensure_ksequence_on_k_cell(kcfg.node(init_node_id).cterm)
                new_target = ensure_ksequence_on_k_cell(kcfg.node(target_node_id).cterm)

                _LOGGER.info(f'Computing definedness constraint for initial node: {claim.label}')
                new_init = kcfg_explore.cterm_assume_defined(new_init)

                _LOGGER.info(f'Simplifying initial and target node: {claim.label}')
                new_init, _ = kcfg_explore.cterm_simplify(new_init)
                new_target, _ = kcfg_explore.cterm_simplify(new_target)
                if CTerm._is_bottom(new_init.kast):
                    raise ValueError('Simplifying initial node led to #Bottom, are you sure your LHS is defined?')
                if CTerm._is_top(new_target.kast):
                    raise ValueError('Simplifying target node led to #Bottom, are you sure your RHS is defined?')

                kcfg.replace_node(init_node_id, new_init)
                kcfg.replace_node(target_node_id, new_target)

                # Unsure if terminal should be empty
                proof_problem = APRProof(
                    claim.label, kcfg, [], init_node_id, target_node_id, {}, proof_dir=save_directory
                )
        return proof_problem


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    parser: Path
    interpreter: Path
    prover: Optional[KMIRProve] = None
    bug_report: Optional[BugReport] = None

    def __init__(
        self,
        llvm_dir: Path,
        *,
        haskell_dir: Optional[Path] = None,
        use_booster: bool = False,
        # use_directory: Optional[Path] = None,
        bug_report: Optional[BugReport] = None,  # TODO: shall we make the bug report by default?
    ):
        # the parser executor for mir syntax
        parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
        if not parser.is_file():
            raise RuntimeError("GLR parser 'parser_Mir_MIR-SYNTAX' not found in 'llvm' directory")

        # the run executor for interpreting mir programs
        interpreter = llvm_dir / 'interpreter'

        prover = KMIRProve(haskell_dir, use_booster, bug_report) if haskell_dir else None

        object.__setattr__(self, 'llvm_dir', llvm_dir)
        object.__setattr__(self, 'parser', parser)
        object.__setattr__(self, 'interpreter', interpreter)
        object.__setattr__(self, 'bug_report', bug_report)
        object.__setattr__(self, 'prover', prover)

    def mir_to_kore(
        self,
        mir_file: Path,
    ) -> CompletedProcess:
        args = [str(self.parser), str(mir_file)]

        try:
            # proc_res.stdout would always be KORE
            # check is by default True, which raises runrime error if proc_res.returncode is nonzero
            # what is exec_process? Debugger?
            proc_res = run_process(args, logger=_LOGGER)
        except CalledProcessError as err:
            raise RuntimeError(f'kmir parser failed with status {err.returncode}: {err.stderr}') from err
        return proc_res

    def interpret_mir_to_kore(
        self,
        pgm: str | Pattern,
        depth: int | None = None,
    ) -> CompletedProcess:
        if not isinstance(pgm, Pattern):
            pgm = KoreParser(pgm).pattern()

        depth = depth if depth is not None else -1
        args = [str(self.interpreter), '/dev/stdin', str(depth), '/dev/stdout']

        init_config = top_cell_initializer({'$PGM': inj(SortApp('SortMir'), SORT_K_ITEM, pgm)})
        try:
            res = run_process(args, input=init_config.text, logger=_LOGGER, pipe_stderr=True)
        except CalledProcessError as err:
            raise RuntimeError(f'kmir interpreter failed with status {err.returncode}: {err.stderr}') from err

        return res

    def print_kore_to_xxx(self, kore_text: str, output: str) -> None:
        output_format = PrintOutput(output)

        match output_format:
            case PrintOutput.NONE:
                pass
            case PrintOutput.KORE:
                print(kore_text)
            case PrintOutput.JSON | PrintOutput.PRETTY | PrintOutput.PROGRAM | PrintOutput.KAST | PrintOutput.LATEX | PrintOutput.BINARY:
                kore_pattern = KoreParser(kore_text).pattern()
                # args = ['kore-print', '/dev/stdin', str(self.llvm_dir), output, '/dev/stdout']
                try:
                    # TODO: Is it necessary to pass the logger in? Like the others
                    text = kore_print(kore_pattern, definition_dir=self.llvm_dir, output=output_format, color=True)
                    print(text)
                except CalledProcessError as err:
                    raise RuntimeError(f'kmir print failed with status {err.returncode}: {err.stderr}') from err
            case _:
                raise ValueError('Output format not supported.')

    def prove_driver(
        self,
        proof: Proof,
        rpc_session: KCFGExplore,
        *,
        max_depth: int | None = 1000,
        max_iterations: int | None = None,
        terminal_rules: Iterable[str] = (),
        cut_point_rules: Iterable[str] = (),  # TODO
        extract_branches: Callable[[CTerm], Iterable[KInner]] | None = None,
        abstract_node: Callable[[CTerm], CTerm] | None = None,
    ) -> tuple[str, str]:
        prover: Prover
        # case APRProof:
        if isinstance(proof, APRProof):
            prover = APRProver(proof, rpc_session)
            prover.advance_proof(
                max_iterations=max_iterations,
                execute_depth=max_depth,
                terminal_rules=terminal_rules,
                cut_point_rules=cut_point_rules,
            )
            passed = proof.status
        elif isinstance(proof, EqualityProof):
            # case EqualityProof:
            prover = EqualityProver(proof, rpc_session)
            prover.advance_proof()
            passed = proof.status
        else:
            # case _:  # APRBMCProof not supported for now
            raise ValueError(f'Do not know how to build a prover for the proof: {proof.id}')

        _LOGGER.info('Claim {proof.id} is {passed.value} with a summary {proof.summary} ')
        # if passed is ProofStatus.FAILED:
        #    _LOGGER.info('The failure reoprt this claim is {proof.failure_info}')

        return (proof.id, passed.value)
