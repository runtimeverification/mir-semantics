from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

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
