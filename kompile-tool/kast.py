#!/usr/bin/env python3

import os
import subprocess
import sys

def run(args):
  print('Running', args)
  result = subprocess.run(args)
  return result.returncode

def main(argv):
  kompiled = argv[0]
  mir_file = argv[1]
  sort = argv[2]
  output = argv[3]

  (definition_dir, _definition_file) = os.path.split(kompiled)
  tool_dir = os.path.join('kompile-tool', 'k', 'bin')
  kast_tool = os.path.realpath(os.path.join(tool_dir, "kast"))

  run([ kast_tool
      , '--version'
      ])
  retv = run( [ kast_tool
              , '--definition', definition_dir
              , '--output', 'kore'
              , '--sort', sort
              , mir_file
              ])
  sys.exit(retv)

if __name__ == "__main__":
  main(sys.argv[1:])
