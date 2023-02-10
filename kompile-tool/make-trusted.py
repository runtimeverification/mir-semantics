#!/usr/bin/env python3
import sys

import trusted

def naturalNumbers():
  i = 1
  while True:
    yield i
    i += 1

def makeProof(file_name, lines):
  lemma_parser = trusted.LemmaParser(file_name)
  for (line_number, line) in lines:
    normalized = line.strip()

    lemma_parser.processLine(line, normalized, line_number)
    if lemma_parser.isParsing():
      if lemma_parser.finishedParsing():
        yield lemma_parser.toClaim()
        lemma_parser.reset()
      continue

    yield line

def main(argv):
  if len(argv) != 3:
    raise Exception('Wrong number of arguments, expected: trusted/proof, an input and an output file name.')
  if argv[0] == 'trusted':
    with open(argv[1], 'r') as f:
      with open(argv[2], 'w') as g:
        g.writelines(trusted.makeTrusted(argv[1], zip(naturalNumbers(), f)))
  elif argv[0] == 'proof':
    with open(argv[1], 'r') as f:
      with open(argv[2], 'w') as g:
        g.writelines(makeProof(argv[1], zip(naturalNumbers(), f)))
  else:
    raise Exception('The first argument must be one of "trusted" and "proof".')

if __name__ == '__main__':
  main(sys.argv[1:])
