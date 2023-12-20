import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Final, TypeVar

from pyk.cterm import CTerm
from pyk.kast.inner import KInner, Subst
from pyk.kast.manip import set_cell
from pyk.kast.outer import KApply, KClaim, KRewrite, KSequence
from pyk.kcfg import KCFG, KCFGExplore
from pyk.ktool.kprove import KProve
from pyk.proof import APRProof

# from pyk.proof.equality import EqualityProof
# from pyk.proof.proof import Proof
from pyk.utils import single

from .preprocessor import preprocess

T1 = TypeVar('T1')
T2 = TypeVar('T2')

NodeIdLike = int | str

_LOGGER: Final = logging.getLogger(__name__)


def preprocess_mir_file(program_file: Path, temp_file: Path) -> None:
    temp_file.write_text(preprocess(program_file.read_text()))


def is_functional(claim: KClaim) -> bool:
    claim_lhs = claim.body
    if type(claim_lhs) is KRewrite:
        claim_lhs = claim_lhs.lhs
    return not (type(claim_lhs) is KApply and claim_lhs.label.name == '<generatedTop>')


def get_apr_proof_for_spec(
    kprove: KProve,
    spec_file: Path,
    save_directory: Path | None,
    spec_module_name: str | None = None,
    include_dirs: Iterable[Path] = (),
    md_selector: str | None = None,
    claim_labels: Iterable[str] | None = None,
    exclude_claim_labels: Iterable[str] = (),
) -> APRProof:
    if save_directory is None:
        save_directory = Path('.')
        _LOGGER.info(f'Using default save_directory: {save_directory}')

    _LOGGER.info(f'Extracting claim from file: {spec_file}')
    claim = single(
        kprove.get_claims(
            spec_file,
            spec_module_name=spec_module_name,
            include_dirs=include_dirs,
            md_selector=md_selector,
            claim_labels=claim_labels,
            exclude_claim_labels=exclude_claim_labels,
        )
    )

    apr_proof = APRProof.read_proof_data(save_directory, claim.label)
    return apr_proof


def ensure_ksequence_on_k_cell(cterm: CTerm) -> CTerm:
    k_cell = cterm.cell('K_CELL')
    if type(k_cell) is not KSequence:
        _LOGGER.info('Introducing artificial KSequence on <k> cell.')
        return CTerm.from_kast(set_cell(cterm.kast, 'K_CELL', KSequence([k_cell])))
    return cterm


""" def print_failure_info(proof: Proof, kcfg_explore: KCFGExplore, counterexample_info: bool = False) -> list[str]:
    if type(proof) is APRProof or type(proof) is APRBMCProof:
        target = proof.kcfg.node(proof.target)

        res_lines: list[str] = []

        num_pending = len(proof.pending)
        num_failing = len(proof.failing)
        res_lines.append(
            f'{num_pending + num_failing} Failure nodes. ({num_pending} pending and {num_failing} failing)'
        )
        if num_pending > 0:
            res_lines.append('')
            res_lines.append('Pending nodes:')
            for node in proof.pending:
                res_lines.append('')
                res_lines.append(f'ID: {node.id}:')
        if num_failing > 0:
            res_lines.append('')
            res_lines.append('Failing nodes:')
            for node in proof.failing:
                res_lines.append('')
                res_lines.append(f'  Node id: {str(node.id)}')

                try:
                    simplified_node, _ = kcfg_explore.cterm_simplify(node.cterm)
                except Exception as err:
                    process_exception(
                        err,
                        res_lines,
                        '    ERROR PRINTING FAILURE INFO: Could not simplify "node.cterm", see stack trace above',
                    )
                try:
                    simplified_target, _ = kcfg_explore.cterm_simplify(target.cterm)
                except Exception as err:
                    process_exception(
                        err,
                        res_lines,
                        '   ERROR PRINTING FAILURE INFO: Could not simplify "target.cterm", see stack trace above',
                    )

                res_lines.append('  Failure reason:')
                try:
                    _, reason = kcfg_explore.implication_failure_reason(simplified_node, simplified_target)
                    res_lines += [f'    {line}' for line in reason.split('\n')]
                except Exception as err:
                    process_exception(
                        err,
                        res_lines,
                        '   ERROR PRINTING FAILURE INFO: Could not create "implication_failure_reason", see stack trace above',
                    )

                res_lines.append('  Path condition:')
                try:
                    res_lines += [f'    {kcfg_explore.kprint.pretty_print(proof.path_constraints(node.id))}']
                except Exception as err:
                    process_exception(
                        err,
                        res_lines,
                        '   ERROR PRINTING FAILURE INFO: Could not pretty print "proof.path_constraints(node.id)", see stack trace above',
                    )

                if counterexample_info:
                    res_lines.extend(print_model(node, kcfg_explore))

        res_lines.append('')
        res_lines.append(
            'Join the Runtime Verification Discord server for support: https://discord.com/invite/CurfmXNtbN'
        )

        return res_lines
    elif type(proof) is EqualityProof:
        return ['EqualityProof failed.']
    else:
        raise ValueError('Unknown proof type.')
 """


def process_exception(err: Exception, curr_output: list[str], err_msg: str) -> None:
    curr_output.append(err_msg)
    print(err, flush=True, file=sys.stderr)
    print(traceback.format_exc(), flush=True, file=sys.stderr)


def print_model(node: KCFG.Node, kcfg_explore: KCFGExplore) -> list[str]:
    res_lines: list[str] = []
    result_subst = kcfg_explore.cterm_get_model(node.cterm)
    if type(result_subst) is Subst:
        res_lines.append('  Model:')
        for var, term in result_subst.to_dict().items():
            term_kast = KInner.from_dict(term)
            res_lines.append(f'    {var} = {kcfg_explore.kprint.pretty_print(term_kast)}')
    else:
        res_lines.append('  Failed to generate a model.')

    return res_lines


def node_id_like(s: str) -> NodeIdLike:
    try:
        return int(s)
    except ValueError:
        return s


def arg_pair_of(
    fst_type: Callable[[str], T1], snd_type: Callable[[str], T2], delim: str = ','
) -> Callable[[str], tuple[T1, T2]]:
    def parse(s: str) -> tuple[T1, T2]:
        elems = s.split(delim)
        length = len(elems)
        if length != 2:
            raise ValueError(f'Expected 2 elements, found {length}')
        return fst_type(elems[0]), snd_type(elems[1])

    return parse
