from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from pyk.kcfg.kcfg import KCFG

if TYPE_CHECKING:
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
    # Deduplicate while preserving original ordering
    ordered_unique_edges: list[tuple[int, int]] = list(dict.fromkeys(edges))

    lines: list[str] = []
    divider = '-' * 80
    for src, dst in ordered_unique_edges:
        edge = proof.kcfg.edge(src, dst)
        ndbranches = proof.kcfg.ndbranches(source_id=src, target_id=dst)
        ndbranch = ndbranches[0] if len(ndbranches) == 1 else None

        selected = edge if edge is not None else ndbranch

        print(f'selected: {selected}')

        match selected:
            case KCFG.Edge(rules=rules):
                title = f'Rules applied on edge {src} -> {dst}:'
                rules_to_print = list(rules)
            case KCFG.NDBranch(_targets=targets, rules=rules):
                title = f'NDBranch applied on edge {src} -> {dst}:'
                # pick rule by the index of the matched target
                # TODO: the rules applied for ndbranches is not stored.
                try:
                    target_index = next(i for i, t in enumerate(targets) if t.id == dst)
                except StopIteration:
                    continue
                if target_index < len(rules):
                    rules_to_print = [rules[target_index]]
                else:
                    rules_to_print = []
            case _:
                continue

        lines.append(title)
        lines.append(f'Total rules: {len(rules_to_print)}')
        lines.append(divider)
        for rule in rules_to_print:
            lines.append(_rule_to_markdown_link(rule))
            lines.append(divider)

    return lines
