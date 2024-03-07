import logging
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Final

from pyk.cli.args import LoggingOptions
from pyk.cli.cli import CLI, Command
from pyk.cli.utils import dir_path, file_path
from pyk.proof import APRProof
from pyk.proof.reachability import APRFailureInfo
from pyk.utils import BugReport, check_dir_path, check_file_path

from . import VERSION
from .cli import KCFGShowProofOptions
from .kmir import KMIR
from .parse import parse
from .prove import get_claim_labels, prove, show_proof, view_proof
from .run import run

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def main() -> None:
    kmir_cli = CLI(
        {VersionCommand, ParseCommand, ParseCommand, RunCommand, ProveCommand, ShowProofCommand, ViewProofCommand}
    )
    cmd = kmir_cli.get_command()
    assert isinstance(cmd, LoggingOptions)
    logging.basicConfig(level=_loglevel(cmd), format=_LOG_FORMAT)
    cmd.exec()


class VersionCommand(Command, LoggingOptions):
    @staticmethod
    def name() -> str:
        return 'version'

    @staticmethod
    def help_str() -> str:
        return 'Display KMIR version'

    def exec(self) -> None:
        print(f'KMIR Version: {VERSION}')


class ParseCommand(Command, LoggingOptions):
    mir_file: Path
    definition_dir: Path
    input: str
    output: str

    @staticmethod
    def name() -> str:
        return 'parse'

    @staticmethod
    def help_str() -> str:
        return 'Parse a MIR file'

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'input': 'program',
            'output': 'pretty',
        }

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument(
            'mir_file',
            type=file_path,
            help='Path to .mir file',
        )
        parser.add_argument(
            '--definition-dir',
            type=dir_path,
            help='Path to LLVM definition to use.',
        )
        parser.add_argument(
            '--input',
            type=str,
            help='Input mode',
            choices=['program', 'binary', 'json', 'kast', 'kore'],
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output mode',
            choices=['pretty', 'program', 'json', 'kore', 'kast', 'binary', 'latex', 'none'],
        )

    def exec(self) -> None:
        check_file_path(self.mir_file)

        if self.definition_dir is None:
            raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
        else:
            # llvm_dir = Path(definition_dir)
            check_dir_path(self.definition_dir)

        kmir = KMIR(self.definition_dir)
        # _LOGGER.log( 'Call parser at {definition_dir}')
        parse(kmir, self.mir_file, output=self.output)
        # print(proc_res.stdout) if output != 'none' else None


class RunCommand(Command, LoggingOptions):
    mir_file: Path
    definition_dir: Path
    output: str
    bug_report: bool
    depth: int | None

    @staticmethod
    def name() -> str:
        return 'run'

    @staticmethod
    def help_str() -> str:
        return 'Run a MIR program'

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'output': 'pretty',
            'bug_report': False,
            'depth': None,
        }

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument(
            'mir_file',
            type=file_path,
            help='Path to .mir file',
        )
        parser.add_argument(
            '--definition-dir',
            type=dir_path,
            help='Path to LLVM definition to use.',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output mode',
            choices=['pretty', 'program', 'json', 'kore', 'latex', 'kast', 'binary', 'none'],
        )
        parser.add_argument(
            '--bug-report',
            action='store_true',
            help='Generate a haskell-backend bug report for the execution',
        )
        parser.add_argument(
            '--depth',
            type=int,
            help='Stop execution after `depth` rewrite steps',
        )

    def exec(self) -> None:
        # mir_file = Path(input_file)
        check_file_path(self.mir_file)

        if self.definition_dir is None:
            raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
        else:
            # llvm_dir = Path(definition_dir)
            check_dir_path(self.definition_dir)

        if self.depth is not None:
            assert self.depth < 0, ValueError(f'Argument "depth" must be non-negative, got: {self.depth}')

        if self.bug_report:
            br = BugReport(self.mir_file.with_suffix('.bug_report.tar'))
            kmir = KMIR(self.definition_dir, bug_report=br)
        else:
            kmir = KMIR(self.definition_dir)

        run(kmir, self.mir_file, depth=self.depth, output=self.output)


class ProveCommand(Command, LoggingOptions):
    spec_file: Path
    definition_dir: Path
    haskell_dir: Path
    claim_list: bool
    claim: str | None
    bug_report: bool
    depth: int | None
    smt_timeout: int
    smt_retry_limit: int
    trace_rewrites: bool
    save_directory: Path | None
    reinit: bool
    use_booster: bool

    @staticmethod
    def name() -> str:
        return 'prove'

    @staticmethod
    def help_str() -> str:
        return 'Prove a MIR specification, by default, it proves all the claims. Use `--claim` option to prove a selected claim.'

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'haskell_dir': os.getenv('KMIR_HASKELL_DIR'),
            'claim_list': False,
            'claim': None,
            'bug_report': False,
            'depth': None,
            'smt_timeout': 200,
            'smt_retry_limit': 4,
            'trace_rewrites': False,
            'save_directory': None,
            'reinit': False,
            'use_booster': False,  # TODO: debug the booster backend, when it is as fast as legacy, change this to be True
        }

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument(
            'spec_file',
            type=file_path,
            help='Path to specification file',
        )
        parser.add_argument(
            '--definition-dir',
            type=dir_path,
            help='Path to LLVM definition to use.',
        )
        parser.add_argument(
            '--haskell-dir',
            type=dir_path,
            help='Path to Haskell definition to use.',
        )
        parser.add_argument(
            '--claim-list',
            action='store_true',
            help='Print a list of claims in the specificatoin file',
        )
        parser.add_argument(
            '--claim',
            type=str,
            help='Provide the claim label for proving a single claim',
        )
        parser.add_argument(
            '--bug-report',
            action='store_true',
            help='Generate a haskell-backend bug report for the execution',
        )
        parser.add_argument(
            '--depth',
            type=int,
            help='Stop execution after `depth` rewrite steps',
        )
        parser.add_argument(
            '--smt-timeout',
            type=int,
            help='Timeout in ms to use for SMT queries',
        )
        parser.add_argument(
            '--smt-retry-limit',
            type=int,
            help='Number of times to retry SMT queries with scaling timeouts.',
        )
        parser.add_argument(
            '--trace-rewrites',
            action='store_true',
            help='Log traces of all simplification and rewrite rule applications.',
        )
        parser.add_argument(
            '--save-directory',
            type=dir_path,
            help='Path to KCFG proofs directory, directory must already exist.',
        )
        parser.add_argument(
            '--reinit',
            action='store_true',
            help='Reinitialise a proof.',
        )
        parser.add_argument(
            '--use-booster',
            action='store_true',
            help='Use the booster backend instead of the haskell backend',
        )

    def exec(self) -> None:
        # TODO: workers
        # TODO: md_selector doesn't work

        check_file_path(self.spec_file)

        if self.definition_dir is None:
            raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
        else:
            # llvm_dir = Path(definition_dir)
            check_dir_path(self.definition_dir)

        if self.haskell_dir is None:
            raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
        else:
            # haskell_dir = Path(haskell_dir)
            check_dir_path(self.haskell_dir)

        # if the save_directory is not provided, the proofs are saved to the same directory of spec_file

        save_directory: Path
        if self.save_directory is None:
            save_directory = self.spec_file.parent
        else:
            save_directory = self.save_directory
            check_dir_path(save_directory)

        br = BugReport(self.spec_file.with_suffix('.bug_report.tar')) if self.bug_report else None
        kmir = KMIR(self.definition_dir, haskell_dir=self.haskell_dir, use_booster=self.use_booster, bug_report=br)
        # We provide configuration of which backend to use in a KMIR object.
        # `use_booster` is by default True, where Booster Backend is always used unless turned off

        if self.claim_list:
            claim_labels = get_claim_labels(kmir, self.spec_file)
            print(*claim_labels, sep='\n')
            sys.exit(0)

        (passed, failed) = prove(
            kmir,
            self.spec_file,
            claim_label=self.claim,
            save_directory=save_directory,
            reinit=self.reinit,
            depth=self.depth,
            smt_timeout=self.smt_timeout,
            smt_retry_limit=self.smt_retry_limit,
            trace_rewrites=self.trace_rewrites,
        )

        for proof in passed:
            print(f'PROOF PASSED: {proof.id}')

        for proof in failed:
            print(f'PROOF FAILED: {proof.id}')
            if isinstance(proof, APRProof) and isinstance(proof.failure_info, APRFailureInfo):
                failure_info = '\n'.join(proof.failure_info.print())
                print(f'{failure_info}')

        total_claims = len(passed) + len(failed)
        plural = '' if total_claims == 1 else 's'
        print(f'Prover run on {total_claims} claim{plural}: {len(passed)} passed, {len(failed)} failed')

        if len(failed) != 0:
            sys.exit(1)


class ShowProofCommand(Command, LoggingOptions, KCFGShowProofOptions):
    claim_label: str
    proof_dir: Path | None
    definition_dir: Path
    haskell_dir: Path

    @staticmethod
    def name() -> str:
        return 'show-proof'

    @staticmethod
    def help_str() -> str:
        return 'Display tree view of a proof in KCFG'

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'proof_dir': None,
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'haskell_dir': os.getenv('KMIR_HASKELL_DIR'),
        }

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument('claim_label', type=str, help='Provide the claim label for showing the proof')
        parser.add_argument(
            '--proof-dir',
            type=dir_path,
            help='Path to KCFG proofs directory, directory must already exist.',
        )
        parser.add_argument(
            '--definition-dir',
            type=dir_path,
            help='Path to LLVM definition to use.',
        )
        parser.add_argument(
            '--haskell-dir',
            type=dir_path,
            help='Path to Haskell definition to use.',
        )

    def exec(self) -> None:
        if self.proof_dir is None:
            raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
        else:
            check_dir_path(self.proof_dir)

        if self.definition_dir is None:
            raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
        else:
            check_dir_path(self.definition_dir)

        if self.haskell_dir is None:
            raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
        else:
            check_dir_path(self.haskell_dir)

        kmir = KMIR(self.definition_dir, haskell_dir=self.haskell_dir)

        show_output = show_proof(
            kmir,
            self.claim_label,
            self.proof_dir,
            self.nodes,
            self.node_deltas,
            self.to_module,
            self.failure_info,
            self.pending,
            self.failing,
            self.counterexample_info,
        )

        print(show_output)


class ViewProofCommand(Command, LoggingOptions):
    claim_label: str
    proof_dir: Path | None
    definition_dir: Path
    haskell_dir: Path

    @staticmethod
    def name() -> str:
        return 'view-proof'

    @staticmethod
    def help_str() -> str:
        return 'Display the interative proof tree'

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'proof_dir': None,
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'haskell_dir': os.getenv('KMIR_HASKELL_DIR'),
        }

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument('claim_label', type=str, help='Provide the claim label for showing the proof')
        parser.add_argument(
            '--proof-dir',
            type=dir_path,
            help='Path to KCFG proofs directory, directory must already exist.',
        )
        parser.add_argument(
            '--definition-dir',
            type=dir_path,
            help='Path to LLVM definition to use.',
        )
        parser.add_argument(
            '--haskell-dir',
            type=dir_path,
            help='Path to Haskell definition to use.',
        )

    def exec(self) -> None:
        # TODO: include dirs

        if self.proof_dir is None:
            raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
        else:
            check_dir_path(self.proof_dir)
        if self.definition_dir is None:
            raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
        else:
            check_dir_path(self.definition_dir)
        if self.haskell_dir is None:
            raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
        else:
            check_dir_path(self.haskell_dir)

        kmir = KMIR(self.definition_dir, haskell_dir=self.haskell_dir)

        view_proof(
            kmir,
            self.claim_label,
            self.proof_dir,
        )


def _loglevel(args: LoggingOptions) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == '__main__':
    main()
