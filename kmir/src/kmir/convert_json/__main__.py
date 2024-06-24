from __future__ import annotations

import json
import sys

from .convert import from_dict


def main() -> None:
    if len(sys.argv) != 2:
        exit(1)
    f = open(sys.argv[1])
    data = json.load(f)
    print(from_dict(data))
