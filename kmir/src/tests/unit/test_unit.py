from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kmir.smir import compute_closure

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
