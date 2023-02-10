#!/usr/bin/env python3

import os
import sys

def addRule(file_name, lines):
  assert file_name.endswith('.mir')
  name = file_name[:-4]
  lines.append('')
  lines.append('kast_test(')
  lines.append("  name = '%s-kast'," % name)
  lines.append("  src = '%s'," % file_name)
  lines.append("  semantics = '//semantics:mir',")
  lines.append("  sort = 'Mir',")
  lines.append("  size = 'small',")
  lines.append(')')

def genBuild(dir):
  file_lines = ['load("//:k.bzl", "kast_test")']
  for f in os.listdir(dir):
    path = os.path.join(dir, f)
    if os.path.isfile(path) and path.endswith('.mir'):
      addRule(f, file_lines)
  with open(os.path.join(dir, 'BUILD'), 'w') as f:
    for line in file_lines:
      print(line, file=f)

def main(argv):
  genBuild(os.path.join('tests', 'syntax'))

if __name__ == "__main__":
  main(sys.argv[1:])
