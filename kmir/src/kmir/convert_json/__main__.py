from __future__ import annotations

import json
import sys
from pathlib import Path

from pyk.ktool.kprint import KPrint

from .convert import from_dict


def main() -> None:
    if len(sys.argv) != 2:
        exit(1)
    f = open(sys.argv[1])
    data = json.load(f)
    # print(from_dict(data))

    p = KPrint(Path('/Users/brucecollie/.cache/kdist-b6802a7/mir-semantics/llvm'))
    print(p.pretty_print(from_dict(data)))
