from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from pyk.cterm.show import CTermShow
    from pyk.kcfg.kcfg import KCFG
    from pyk.proof.reachability import APRProof


def _rule_to_markdown_link(rule: object) -> str:
    """Render a single rule as a Markdown file link if possible.

    The function tries, in order:
    - Parse the first line of str(rule) for pattern: <id>:/abs/path:(startLine, startCol, endLine, endCol)
    - Use rule attributes 'source' and 'location' when available

    Fallback to the first line of str(rule) if no path can be determined.
    """
    text_first = str(rule).splitlines()[0]

    # 1) Parse textual representation first (most robust across backends)
    m_text = re.match(r'^[^:]+:(/[^:]+):\((\d+)\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\)\s*$', text_first)
    if m_text:
        file_path = m_text.group(1)
        start_line = int(m_text.group(2))
        uri = Path(file_path).resolve().as_uri()
        label_text = f'{Path(file_path).name}:{start_line}'
        return f'[{label_text}]({uri}#L{start_line})'

    # 2) Try attributes on the rule object (when present)
    try:
        att = getattr(rule, 'att', None)
        source_file: str | None = None
        if att is not None:
            get = getattr(att, 'get', None)
            if callable(get):
                source_file = get('source')
                loc = get('location')
            else:
                try:
                    source_file = att['source']  # type: ignore[index]
                except Exception:
                    source_file = None
                try:
                    loc = att['location']  # type: ignore[index]
                except Exception:
                    loc = None

            if isinstance(loc, str):
                # Format 1: startLine:startCol-endLine:endCol
                m = re.match(r'^(\d+):(\d+)-(\d+):(\d+)$', loc)
                if m:
                    start_line = int(m.group(1))
                else:
                    # Format 2: (startLine, startCol, endLine, endCol)
                    m2 = re.match(r'^\(\s*(\d+)\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$', loc)
                    if m2:
                        start_line = int(m2.group(1))

            if source_file is not None:
                uri = Path(source_file).resolve().as_uri()
                line_anchor = f'#L{start_line}' if start_line is not None else ''
                label_text = (
                    f'{Path(source_file).name}:{start_line}' if start_line is not None else Path(source_file).name
                )
                return f'[{label_text}]({uri}{line_anchor})'
    except Exception:
        pass

    # 3) Fallback: raw first line
    return text_first


def render_rules(proof: APRProof, edges: Sequence[tuple[int, int]]) -> list[str]:
    """Render rules for a collection of edges as markdown text lines.

    - proof: APRProof containing the kcfg with edges
    - edges: iterable of (src, dst)
    """
    # Deduplicate while preserving a stable ordering
    seen: set[tuple[int, int]] = set()
    ordered_unique_edges: list[tuple[int, int]] = []
    for e in edges:
        if e not in seen:
            seen.add(e)
            ordered_unique_edges.append(e)

    lines: list[str] = []
    for src, dst in ordered_unique_edges:
        edge = proof.kcfg.edge(src, dst)
        if edge is None:
            lines.append(f'Rules applied on edge {src} -> {dst}:')
            lines.append('No edge found')
            continue
        applied = edge.rules
        lines.append(f'Rules applied on edge {src} -> {dst}:')
        lines.append(f'Total rules: {len(applied)}')
        lines.append('-' * 80)
        for rule in applied:
            lines.append(_rule_to_markdown_link(rule))
            lines.append('-' * 80)

    return lines


def render_statistics(proof: APRProof) -> list[str]:
    """Return human-readable statistics about the proof graph."""

    kcfg = proof.kcfg

    role_nodes: dict[str, list[int]] = {}

    def classify(node_id: int) -> str:
        if kcfg.is_root(node_id):
            return 'root'
        if proof.is_target(node_id):
            return 'target'
        if proof.is_terminal(node_id):
            return 'terminal'
        if proof.is_refuted(node_id):
            return 'refuted'
        if proof.is_bounded(node_id):
            return 'bounded'
        if proof.is_pending(node_id):
            return 'pending'
        if proof.is_failing(node_id):
            return 'failing'
        if kcfg.is_split(node_id) or kcfg.is_ndbranch(node_id):
            return 'split'
        if kcfg.is_stuck(node_id):
            return 'stuck'
        return 'normal'

    for node in kcfg.nodes:
        role = classify(node.id)
        role_nodes.setdefault(role, []).append(node.id)

    root_nodes = role_nodes.pop('root', [])
    total_nodes = sum(len(ids) for ids in role_nodes.values())

    role_order = (
        'target',
        'terminal',
        'bounded',
        'refuted',
        'pending',
        'failing',
        'split',
        'stuck',
        'normal',
    )

    lines: list[str] = ['STATISTICS', '-----------', f'Total nodes: {total_nodes}', '', 'Node roles (exclusive):']

    for label in role_order:
        ids = sorted(role_nodes.get(label, ()))
        if ids:
            id_str = ', '.join(str(i) for i in ids)
            lines.append(f'  {label:8s}: {len(ids)}  ids: {id_str}')

    if root_nodes:
        lines.append('  (root nodes omitted from totals: ' + ', '.join(str(i) for i in sorted(root_nodes)) + ')')

    lines.append('')
    lines.append('Leaf paths from init:')

    leaves = [node for node in kcfg.leaves if not kcfg.is_root(node.id)]
    total_steps = 0
    reachable_leaf_count = 0
    leaf_lines: list[str] = []

    def _path_nodes(source_id: int, path: Sequence[KCFG.Successor]) -> list[int]:
        from pyk.kcfg.kcfg import KCFG as _KCFG

        node_ids = [source_id]
        current = source_id
        for succ in path:
            target_id: int | None = None
            if isinstance(succ, _KCFG.EdgeLike):
                target_id = succ.target.id
            elif isinstance(succ, _KCFG.MultiEdge):
                targets = list(succ.targets)
                if len(targets) == 1:
                    target_id = targets[0].id
            if target_id is not None and target_id != current:
                node_ids.append(target_id)
                current = target_id
        return node_ids

    for leaf in sorted(leaves, key=lambda n: n.id):
        path = kcfg.shortest_path_between(proof.init, leaf.id)
        if path is None:
            leaf_lines.append(f'  leaf {leaf.id}: unreachable from init')
            continue

        steps = kcfg.path_length(path)
        total_steps += steps
        reachable_leaf_count += 1
        node_seq = _path_nodes(proof.init, path)
        seq_str = ' -> '.join(str(nid) for nid in node_seq)
        leaf_lines.append(f'  leaf {leaf.id}: steps {steps}, path {seq_str}')

    lines.append(f'  total leaves (non-root): {len(leaves)}')
    lines.append(f'  reachable leaves       : {reachable_leaf_count}')
    lines.append(f'  total steps            : {total_steps}')

    if leaf_lines:
        lines.append('')
        lines.extend(leaf_lines)

    return lines


def render_leaf_k_cells(proof: APRProof, cterm_show: CTermShow) -> list[str]:
    """Render the <k> cell for every leaf node in the proof."""

    leaves = sorted(
        [node for node in proof.kcfg.leaves if not proof.kcfg.is_root(node.id)],
        key=lambda node: node.id,
    )
    header = ['LEAF <k> CELLS', '---------------']
    if not leaves:
        return header + ['  (no leaf nodes)']

    lines: list[str] = header
    for idx, leaf in enumerate(leaves):
        lines.append(f'Node {leaf.id}:')
        try:
            k_cell = leaf.cterm.cell('K_CELL')
            k_lines = cterm_show.print_lines(k_cell)
        except KeyError:
            k_lines = ['<K_CELL unavailable>']

        if not k_lines:
            lines.append('  (empty)')
        else:
            lines.extend(f'  {k_line}' for k_line in k_lines)

        if idx != len(leaves) - 1:
            lines.append('')

    return lines
