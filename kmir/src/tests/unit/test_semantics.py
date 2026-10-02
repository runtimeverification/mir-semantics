from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pyk.cterm import CTerm
from pyk.kast.inner import KApply, KSequence, KToken, KVariable

from kmir.kmir import KMIR, KMIRSemantics

if TYPE_CHECKING:
    from pyk.kast.inner import KInner


def _int(i: int) -> KToken:
    return KToken(str(i), 'Int')


def _ty(i: int) -> KApply:
    return KApply('ty', [_int(i)])


def _switch_targets(then_block: int, else_block: int) -> KApply:
    # Mirrors `switchTargets(branch(0, basicBlockIdx(N)) .Branches, basicBlockIdx(M))`; only equality matters here.
    return KApply(
        'switchTargets', [KApply('branch', [_int(0), KApply('basicBlockIdx', [_int(then_block)])]), _int(else_block)]
    )


def _select_block(targets: KInner, condition: KInner) -> KApply:
    return KApply(KMIR.Symbols.SELECT_BLOCK, [targets, condition])


def _frame(caller: int, local_value: int) -> KApply:
    # A stand-in for a `StackFrame(...)`: its contents (here a local's value) differ between iterations.
    return KApply('ListItem', [KApply('StackFrame', [_ty(caller), _int(local_value)])])


def _stack(*items: KInner) -> KInner:
    if not items:
        return KApply('.List')
    stack = items[-1]
    for item in reversed(items[:-1]):
        stack = KApply('_List_', [item, stack])
    return stack


def _config(k: KInner, *, func: int = 7, stack: KInner | None = None) -> CTerm:
    k_cell = k if isinstance(k, KSequence) else KSequence([k, KVariable('REST_K')])
    return CTerm(
        KApply(
            '<generatedTop>',
            [
                KApply(
                    '<kmir>',
                    [
                        KApply('<k>', [k_cell]),
                        KApply('<currentFunc>', [_ty(func)]),
                        KApply('<stack>', [stack if stack is not None else _stack(_frame(1, 0))]),
                    ],
                )
            ],
        )
    )


LOOP_HEAD = _config(_select_block(_switch_targets(3, 2), KVariable('COND')))

IS_LOOP_TESTS = [
    ('select-block', LOOP_HEAD, True),
    ('select-block-alone', _config(KSequence([_select_block(_switch_targets(3, 2), _int(1))])), True),
    ('end-program', _config(KMIR.Symbols.END_PROGRAM), False),
    ('exec-block', _config(KApply('#execBlockIdx', [KApply('basicBlockIdx', [_int(3)])])), False),
    (
        'select-block-not-first',
        _config(KSequence([KApply('#foo'), _select_block(_switch_targets(3, 2), _int(1))])),
        False,
    ),
    ('empty-k', _config(KSequence([])), False),
]


@pytest.mark.parametrize('cterm,expected', [(c, e) for _, c, e in IS_LOOP_TESTS], ids=[i for i, _, _ in IS_LOOP_TESTS])
def test_is_loop(cterm: CTerm, expected: bool) -> None:
    assert KMIRSemantics().is_loop(cterm) == expected


SAME_LOOP_TESTS = [
    (
        'same-loop-next-iteration',
        # Same switch, function and depth; the condition and the frame's locals differ.
        _config(_select_block(_switch_targets(3, 2), KVariable('COND1')), stack=_stack(_frame(1, 0))),
        _config(_select_block(_switch_targets(3, 2), KVariable('COND2')), stack=_stack(_frame(1, 5))),
        True,
    ),
    (
        'same-loop-concrete-condition',
        LOOP_HEAD,
        _config(_select_block(_switch_targets(3, 2), _int(0))),
        True,
    ),
    (
        'different-switch',
        LOOP_HEAD,
        _config(_select_block(_switch_targets(5, 4), KVariable('COND'))),
        False,
    ),
    (
        'different-function',
        LOOP_HEAD,
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), func=8),
        False,
    ),
    (
        'different-call-depth',
        # e.g. the same loop inside a recursive call
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack(_frame(1, 0))),
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack(_frame(7, 0), _frame(1, 0))),
        False,
    ),
    (
        'empty-stacks',
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack()),
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack()),
        True,
    ),
    (
        'symbolic-stack',
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack(_frame(1, 0), KVariable('S'))),
        _config(_select_block(_switch_targets(3, 2), KVariable('COND')), stack=_stack(_frame(1, 9), KVariable('S'))),
        True,
    ),
    (
        'first-not-loop-head',
        _config(KMIR.Symbols.END_PROGRAM),
        LOOP_HEAD,
        False,
    ),
    (
        'second-not-loop-head',
        LOOP_HEAD,
        _config(KMIR.Symbols.END_PROGRAM),
        False,
    ),
    (
        'neither-loop-head',
        _config(KMIR.Symbols.END_PROGRAM),
        _config(KMIR.Symbols.END_PROGRAM),
        False,
    ),
]


@pytest.mark.parametrize(
    'c1,c2,expected', [(c1, c2, e) for _, c1, c2, e in SAME_LOOP_TESTS], ids=[i for i, _, _, _ in SAME_LOOP_TESTS]
)
def test_same_loop(c1: CTerm, c2: CTerm, expected: bool) -> None:
    semantics = KMIRSemantics()
    assert semantics.same_loop(c1, c2) == expected
    assert semantics.same_loop(c2, c1) == expected  # symmetric
