#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from fileinput import FileInput
from pathlib import Path

from pyk.cli_utils import check_file_path

LINE_COMMENT_REGEXP = re.compile(r'^((?:[^/"]|/[^/"]|/?"(?:[^\\"]|\\.)*")*)//.*$')
HEX_CLEANUP_SUFFIX = re.compile(r'^(\s*(?: ([0-9a-fA-F][0-9a-fA-F]|#\(-*alloc[0-9]+-*\)#))+)\s+│.*$')
HEX_CLEANUP_SEPARATOR = re.compile(r'^(\s+0x[0-9a-fA-F]+\s+)│(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$')


def preprocess(program_text: str) -> str:
    return '\n'.join(process_line(line) for line in program_text.splitlines())


def process_line(line: str) -> str:
    line = line.rstrip()
    line = remove_comments(line)
    line = cleanup_hex_dump(line)
    line = line.rstrip()
    return line


def remove_comments(line: str) -> str:
    m = LINE_COMMENT_REGEXP.match(line)
    if not m:
        return line
    return m.group(1)


def cleanup_hex_dump(line: str) -> str:
    line = line.replace('╾', '#(').replace('─', '-').replace('╼', ')#')
    m = HEX_CLEANUP_SUFFIX.match(line)
    if not m:
        m = HEX_CLEANUP_SEPARATOR.match(line)
        if not m:
            return line
        return '%s|%s' % (m.group(1), m.group(2))
    return m.group(1)


def main() -> None:
    parser = ArgumentParser(description='KMIR preprocessor')
    parser.add_argument('file', metavar='FILE', nargs='?', default='-', help='input file')
    args = parser.parse_args()

    input_file = Path(args.file) if args.file != '-' else None
    if input_file:
        check_file_path(input_file)

    with FileInput(input_file) as f:
        for line in f:
            print(process_line(line))


if __name__ == '__main__':
    main()
