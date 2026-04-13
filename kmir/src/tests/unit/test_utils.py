from __future__ import annotations

from dataclasses import dataclass

from pyk.cterm import CSubst, CTerm
from pyk.kast.inner import KApply
from pyk.kcfg.kcfg import KCFG

from kmir.utils import render_statistics


@dataclass
class _FakeKCFG:
    nodes: tuple[KCFG.Node, ...]
    leaves: tuple[KCFG.Node, ...]
    root_ids: frozenset[int]
    successor_map: dict[int, tuple[object, ...]]

    def is_root(self, node_id: int) -> bool:
        return node_id in self.root_ids

    def successors(self, node_id: int) -> tuple[object, ...]:
        return self.successor_map.get(node_id, ())

    def is_split(self, _node_id: int) -> bool:
        return False

    def is_ndbranch(self, _node_id: int) -> bool:
        return False

    def is_stuck(self, _node_id: int) -> bool:
        return False


@dataclass
class _FakeProof:
    kcfg: _FakeKCFG
    init: int
    pending_ids: frozenset[int]

    def is_target(self, _node_id: int) -> bool:
        return False

    def is_terminal(self, _node_id: int) -> bool:
        return False

    def is_refuted(self, _node_id: int) -> bool:
        return False

    def is_bounded(self, _node_id: int) -> bool:
        return False

    def is_pending(self, node_id: int) -> bool:
        return node_id in self.pending_ids

    def is_failing(self, _node_id: int) -> bool:
        return False


def test_render_statistics_handles_zero_cost_predecessor_cycles() -> None:
    kcfg = KCFG()
    loop_target = kcfg.create_node(CTerm(KApply('<loopTarget>')))
    init = kcfg.create_node(CTerm(KApply('<init>')))
    leaf = kcfg.create_node(CTerm(KApply('<leaf>')))

    fake_kcfg = _FakeKCFG(
        nodes=(loop_target, init, leaf),
        leaves=(leaf,),
        root_ids=frozenset({init.id}),
        successor_map={
            init.id: (KCFG.Cover(init, loop_target, CSubst()),),
            loop_target.id: (
                KCFG.Cover(loop_target, init, CSubst()),
                KCFG.Edge(loop_target, leaf, 1, ()),
            ),
        },
    )
    proof = _FakeProof(fake_kcfg, init=init.id, pending_ids=frozenset({leaf.id}))

    lines = render_statistics(proof)

    assert f'  leaf {leaf.id}: shortest steps 1, path {init.id} -> {loop_target.id} -> {leaf.id}' in lines
