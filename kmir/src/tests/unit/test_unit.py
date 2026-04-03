from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kmir._cse import _runtime_related_callees, _select_phase1_callees
from kmir.kmir import _freshen_quantifier_binders
from kmir.smir import compute_closure
from pyk.kast.inner import KApply, KLabel, KSort, KVariable

if TYPE_CHECKING:
    from kmir.smir import Ty

# fmt: off
GRAPH_CLOSURE_TESTS = [
    (
        'Simple Directed Graph',
        0,
        {0: [1], 1: [2], 2: [3]},
        {0, 1, 2, 3}
    ),
    (
        'Graph with a Cycle',
        0,
        {0: [1], 1: [2], 2: [0, 3], 3: [4]},
        {0, 1, 2, 3, 4}
    ),
    (
        'Disconnected Node',
        0,
        {0: [1, 2], 1: [3], 2: [], 3: [], 4: [0]},
        {0, 1, 2, 3}
    ),
    (
        'Start Node with No Outgoing Edges',
        0,
        {0: [], 1: [0, 2], 2: [1]},
        {0}
    ),
    (
        'Multiple Paths to a Node',
        0,
        {0: [1, 2], 1: [3], 2: [3], 3: [4]},
        {0, 1, 2, 3, 4}
    ),
    (
        'Self-loop in a node',
        0,
        {0: [0, 1], 1: [2]},
        {0, 1, 2}
    ),
]
# fmt: on


@pytest.mark.parametrize(
    'test_case',
    GRAPH_CLOSURE_TESTS,
    ids=[name for name, _, _, _ in GRAPH_CLOSURE_TESTS],
)
def test_compute_closure(test_case: tuple[str, Ty, dict[Ty, set[Ty]], list[Ty]]) -> None:
    _, start, edges, expected = test_case

    result = compute_closure(start, edges)
    assert result == expected


def test_runtime_related_callees_include_observed_ancestors_and_descendants() -> None:
    call_edges = {
        1: {2, 6},
        2: {3},
        3: {4},
        4: {5},
        6: {7},
    }

    related = _runtime_related_callees(call_edges, {4})

    assert related == {1, 2, 3, 4, 5}


def test_select_phase1_callees_keeps_all_root_reachable_callees_by_default() -> None:
    callee_order = [2, 3, 4, 5]
    call_edges = {
        1: {2, 3},
        2: {4},
        3: {5},
    }

    phase1 = _select_phase1_callees(
        callee_order,
        call_edges=call_edges,
        observed_runtime_seen={4},
        observe_only_mode=False,
        reuse_only_mode=False,
        restrict_to_observed_runtime=False,
    )

    assert phase1 == callee_order


def test_select_phase1_callees_can_still_restrict_to_runtime_related_subset() -> None:
    callee_order = [2, 3, 4, 5]
    call_edges = {
        1: {2, 3},
        2: {4},
        3: {5},
    }

    phase1 = _select_phase1_callees(
        callee_order,
        call_edges=call_edges,
        observed_runtime_seen={4},
        observe_only_mode=False,
        reuse_only_mode=False,
        restrict_to_observed_runtime=True,
    )

    assert phase1 == [2, 4]


def test_freshen_quantifier_binders_separates_same_generated_name_across_scopes() -> None:
    term = KApply(
        KLabel('#And', [KSort('GeneratedTopCell')]),
        [
            KApply(
                KLabel('#Exists', [KSort('F64'), KSort('GeneratedTopCell')]),
                [
                    KVariable('_Gen1', KSort('F64')),
                    KVariable('_Gen1', KSort('F64')),
                ],
            ),
            KApply(
                KLabel('#Exists', [KSort('List'), KSort('GeneratedTopCell')]),
                [
                    KVariable('_Gen1', KSort('List')),
                    KVariable('_Gen1', KSort('List')),
                ],
            ),
        ],
    )

    freshened = _freshen_quantifier_binders(term).to_dict()

    left_name = freshened['args'][0]['args'][0]['name']
    right_name = freshened['args'][1]['args'][0]['name']

    assert left_name != right_name
    assert freshened['args'][0]['args'][1]['name'] == left_name
    assert freshened['args'][1]['args'][1]['name'] == right_name
