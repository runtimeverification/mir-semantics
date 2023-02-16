#!/usr/bin/env python3

import re
import sys

from pathlib import Path

LINE_COMMENT_REGEXP = re.compile(r'^((?:[^/"]|/[^/"]|/?"(?:[^\\"]|\\.)*")*)//.*$')
HEX_CLEANUP_SUFFIX = re.compile(r'^(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$')
HEX_CLEANUP_SEPARATOR = re.compile(r'^(\s+0x[0-9a-fA-F]+\s+)│(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$')

def removeComments(line: str) -> str:
  m = LINE_COMMENT_REGEXP.match(line)
  if not m:
    return line
  return m.group(1)

def cleanupHexDump(line: str) -> str:
  m = HEX_CLEANUP_SUFFIX.match(line)
  if not m:
    m = HEX_CLEANUP_SEPARATOR.match(line)
    if not m:
      return line
    return "%s|%s" % (m.group(1), m.group(2))
  return m.group(1)

def preprocess(input_file: Path, output_file: Path) -> None:
  with open(input_file, 'r') as f:
    with open(output_file, 'w') as g:
      for line in f:
        line = removeComments(line.rstrip())
        line = cleanupHexDump(line)
        g.write(line.rstrip())
        g.write('\n')

def main(args):
  # print(removeComments('Hello World'))
  # print(removeComments('Hello // World'))
  # print(removeComments('Hello "// World"'))
  # print(removeComments('Hello "\\"// World"'))
  # print(removeComments('Hello "// World" // Here'))
  # print(cleanupHexDump('Hello world'))
  # print(cleanupHexDump('  00 00 00 00 00 00 00 00                         │ ........'))
  # print(cleanupHexDump('  0x00 │ 00 00 00 00 00 00 00 00                         │ ........'))
  if len(args) != 2:
    print('Usage: preprocessor.py input-file output-file')
    sys.exit(1)
  input_file = args[0]
  output_file = args[1]
  preprocess(input_file, output_file)

if __name__ == '__main__':
  main(sys.argv[1:])