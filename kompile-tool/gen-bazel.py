#!/usr/bin/env python3

import os
import subprocess
import sys

import trusted

def naturalNumbers():
  i = 1
  while True:
    yield i
    i += 1

class KFile(object):
  def __init__(self, name, require, timeout, breadth):
    self.__name = name
    self.__require = require
    self.__timeout = timeout
    self.__breadth = breadth

  def name(self):
    return self.__name

  def require(self):
    for i in self.__require:
      yield i

  def timeout(self):
    return self.__timeout

  def breadth(self):
    return self.__breadth

def eq_tr(expected, state):
  def f(actual):
    if expected == actual:
      return state
    return None
  return f

def cond_tr(cond, state):
  def f(actual):
    if cond(actual):
      return state
    return None
  return f

def space_tr(state):
  def f(actual):
    if actual.isspace():
      return state
    return None
  return f

def tr(state):
  def f(_):
    return state
  return f

def lambda_tr(transition, l):
  def f(actual):
    state = transition(actual)
    if state is not None:
      l(actual)
    return state
  return f

def err_tr(transition):
  def f(actual):
    state = transition(actual)
    assert state is None
    return state
  return f

class StringRecorder(object):
  def __init__(self):
    self.__strings = []
    self.__current_string = []

  def start(self, _):
    assert not self.__current_string
    self.__current_string = []

  def add(self, c):
    self.__current_string.append(c)

  def end(self, _):
    self.__strings.append(''.join(self.__current_string))
    self.__current_string = []

  def strings(self):
    assert not self.__current_string
    return self.__strings

def loadFile(directory, name):
  with open(os.path.join(directory, name), 'r') as f:
    contents = f.read()
    return loadFileContents(contents, name)

def loadFileAsTrusted(directory, name, trusted_name):
  with open(os.path.join(directory, name), 'r') as f:
    contents = ''.join(trusted.makeTrusted(name, zip(naturalNumbers(), f)))
    return loadFileContents(contents, trusted_name)

def loadFileContents(contents, name):
  START = 0
  SLASH = 1
  MULTILINE = 2
  MULTILINE_STAR = 3
  ONELINE = 4
  R = 5
  RE = 6
  REQ = 7
  REQU = 8
  REQUI = 9
  REQUIR = 10
  REQUIRE = 11
  REQUIRE_SP = 12
  REQUIRE_SP_Q = 13
  M = 15
  MO = 16
  MOD = 17
  MODU = 18
  MODUL = 19
  MODULE = 20
  OTHER = 22
  END = 23
  SSLASH = 24
  SSLASH_SP = 25
  SSLASH_SP_T = 26
  SSLASH_SP_TI = 27
  SSLASH_SP_TIM = 28
  SSLASH_SP_TIME = 29
  SSLASH_SP_TIMEO = 30
  SSLASH_SP_TIMEOU = 31
  SSLASH_SP_TIMEOUT = 32
  SSLASH_SP_TIMEOUT_SP = 33
  SSLASH_SP_TIMEOUT_SP_EQ = 34
  SSLASH_SP_TIMEOUT_SP_EQ_SP = 35
  SSLASH_SP_TIMEOUT_SP_EQ_SP_IN = 36
  SSLASH_SP_B = 37
  SSLASH_SP_BR = 38
  SSLASH_SP_BRE = 39
  SSLASH_SP_BREA = 40
  SSLASH_SP_BREAD = 41
  SSLASH_SP_BREADT = 42
  SSLASH_SP_BREADTH = 43
  SSLASH_SP_BREADTH_SP = 44
  SSLASH_SP_BREADTH_SP_EQ = 45
  SSLASH_SP_BREADTH_SP_EQ_SP = 46
  SSLASH_SP_BREADTH_SP_EQ_SP_IN = 47

  require = StringRecorder()
  timeout = StringRecorder()
  breadth = StringRecorder()

  transitions = {
    START: [eq_tr('/', SLASH), eq_tr('r', R), eq_tr('m', M), space_tr(START), tr(OTHER)],
    SLASH: [eq_tr('/', SSLASH), eq_tr('*', SLASH), space_tr(START), tr(OTHER)],
    MULTILINE: [eq_tr('*', MULTILINE_STAR), tr(MULTILINE)],
    MULTILINE_STAR: [eq_tr('/', START), eq_tr('*', MULTILINE_STAR), tr(MULTILINE)],
    ONELINE: [eq_tr('\n', START), tr(ONELINE)],
    R: [eq_tr('/', SLASH), eq_tr('e', RE), space_tr(START), tr(OTHER)],
    RE: [eq_tr('/', SLASH), eq_tr('q', REQ), space_tr(START), tr(OTHER)],
    REQ: [eq_tr('/', SLASH), eq_tr('u', REQU), space_tr(START), tr(OTHER)],
    REQU: [eq_tr('/', SLASH), eq_tr('i', REQUI), space_tr(START), tr(OTHER)],
    REQUI: [eq_tr('/', SLASH), eq_tr('r', REQUIR), space_tr(START), tr(OTHER)],
    REQUIR: [eq_tr('/', SLASH), eq_tr('e', REQUIRE), space_tr(START), tr(OTHER)],
    REQUIRE: [eq_tr('/', SLASH), lambda_tr(eq_tr('"', REQUIRE_SP_Q), require.start), space_tr(REQUIRE_SP), tr(OTHER)],
    REQUIRE_SP: [err_tr(eq_tr('/', SLASH)), lambda_tr(eq_tr('"', REQUIRE_SP_Q), require.start), space_tr(REQUIRE_SP), err_tr(tr(OTHER))],
    REQUIRE_SP_Q: [lambda_tr(eq_tr('"', START), require.end), lambda_tr(tr(REQUIRE_SP_Q), require.add)],
    M: [eq_tr('/', SLASH), eq_tr('o', MO), space_tr(START), tr(OTHER)],
    MO: [eq_tr('/', SLASH), eq_tr('d', MOD), space_tr(START), tr(OTHER)],
    MOD: [eq_tr('/', SLASH), eq_tr('u', MODU), space_tr(START), tr(OTHER)],
    MODU: [eq_tr('/', SLASH), eq_tr('l', MODUL), space_tr(START), tr(OTHER)],
    MODUL: [eq_tr('/', SLASH), eq_tr('e', MODULE), space_tr(START), tr(OTHER)],
    MODULE: [eq_tr('/', SLASH), space_tr(END), tr(OTHER)],
    OTHER: [eq_tr('/', SLASH), space_tr(START), tr(OTHER)],
    END: [tr(END)],
    SSLASH: [eq_tr('\n', START), space_tr(SSLASH_SP), eq_tr('b', SSLASH_SP_B), eq_tr('t', SSLASH_SP_T), tr(ONELINE)],
    SSLASH_SP: [eq_tr('\n', START), space_tr(SSLASH_SP), eq_tr('b', SSLASH_SP_B), eq_tr('t', SSLASH_SP_T), tr(ONELINE)],

    SSLASH_SP_T: [eq_tr('\n', START), eq_tr('i', SSLASH_SP_TI), tr(ONELINE)],
    SSLASH_SP_TI: [eq_tr('\n', START), eq_tr('m', SSLASH_SP_TIM), tr(ONELINE)],
    SSLASH_SP_TIM: [eq_tr('\n', START), eq_tr('e', SSLASH_SP_TIME), tr(ONELINE)],
    SSLASH_SP_TIME: [eq_tr('\n', START), eq_tr('o', SSLASH_SP_TIMEO), tr(ONELINE)],
    SSLASH_SP_TIMEO: [eq_tr('\n', START), eq_tr('u', SSLASH_SP_TIMEOU), tr(ONELINE)],
    SSLASH_SP_TIMEOU: [eq_tr('\n', START), eq_tr('t', SSLASH_SP_TIMEOUT), tr(ONELINE)],
    SSLASH_SP_TIMEOUT: [eq_tr('\n', START), eq_tr('=', SSLASH_SP_TIMEOUT_SP_EQ), space_tr(SSLASH_SP_TIMEOUT_SP), tr(ONELINE)],
    SSLASH_SP_TIMEOUT_SP: [err_tr(eq_tr('\n', START)), eq_tr('=', SSLASH_SP_TIMEOUT_SP_EQ), space_tr(SSLASH_SP_TIMEOUT_SP), err_tr(tr(ONELINE))],
    SSLASH_SP_TIMEOUT_SP_EQ: [
      err_tr(eq_tr('\n', START)),
      space_tr(SSLASH_SP_TIMEOUT_SP_EQ_SP),
      lambda_tr(lambda_tr(tr(SSLASH_SP_TIMEOUT_SP_EQ_SP_IN), timeout.start), timeout.add)
    ],
    SSLASH_SP_TIMEOUT_SP_EQ_SP: [
      err_tr(eq_tr('\n', START)),
      space_tr(SSLASH_SP_TIMEOUT_SP_EQ_SP),
      lambda_tr(lambda_tr(tr(SSLASH_SP_TIMEOUT_SP_EQ_SP_IN), timeout.start), timeout.add)
    ],
    SSLASH_SP_TIMEOUT_SP_EQ_SP_IN: [
      lambda_tr(eq_tr('\n', START), timeout.end),
      lambda_tr(space_tr(SSLASH_SP_TIMEOUT_SP_EQ_SP), timeout.end),
      lambda_tr(tr(SSLASH_SP_TIMEOUT_SP_EQ_SP_IN), timeout.add)
    ],

    SSLASH_SP_B: [eq_tr('\n', START), eq_tr('r', SSLASH_SP_BR), tr(ONELINE)],
    SSLASH_SP_BR: [eq_tr('\n', START), eq_tr('e', SSLASH_SP_BRE), tr(ONELINE)],
    SSLASH_SP_BRE: [eq_tr('\n', START), eq_tr('a', SSLASH_SP_BREA), tr(ONELINE)],
    SSLASH_SP_BREA: [eq_tr('\n', START), eq_tr('d', SSLASH_SP_BREAD), tr(ONELINE)],
    SSLASH_SP_BREAD: [eq_tr('\n', START), eq_tr('t', SSLASH_SP_BREADT), tr(ONELINE)],
    SSLASH_SP_BREADT: [eq_tr('\n', START), eq_tr('h', SSLASH_SP_BREADTH), tr(ONELINE)],
    SSLASH_SP_BREADTH: [eq_tr('\n', START), eq_tr('=', SSLASH_SP_BREADTH_SP_EQ), space_tr(SSLASH_SP_BREADTH_SP), tr(ONELINE)],
    SSLASH_SP_BREADTH_SP: [err_tr(eq_tr('\n', START)), eq_tr('=', SSLASH_SP_BREADTH_SP_EQ), space_tr(SSLASH_SP_BREADTH_SP), err_tr(tr(ONELINE))],
    SSLASH_SP_BREADTH_SP_EQ: [
      err_tr(eq_tr('\n', START)),
      space_tr(SSLASH_SP_BREADTH_SP_EQ_SP),
      lambda_tr(lambda_tr(tr(SSLASH_SP_BREADTH_SP_EQ_SP_IN), breadth.start), breadth.add)
    ],
    SSLASH_SP_BREADTH_SP_EQ_SP: [
      err_tr(eq_tr('\n', START)),
      space_tr(SSLASH_SP_BREADTH_SP_EQ_SP),
      lambda_tr(lambda_tr(tr(SSLASH_SP_BREADTH_SP_EQ_SP_IN), breadth.start), breadth.add)
    ],
    SSLASH_SP_BREADTH_SP_EQ_SP_IN: [
      lambda_tr(eq_tr('\n', START), breadth.end),
      lambda_tr(space_tr(SSLASH_SP_BREADTH_SP_EQ_SP), breadth.end),
      lambda_tr(tr(SSLASH_SP_BREADTH_SP_EQ_SP_IN), breadth.add)
    ],
  }
  state = START
  for c in contents:
    ts = transitions[state]
    next_state = None
    for t in ts:
      next_state = t(c)
      if next_state is not None:
        break
    # print('%d + %s -> %d' % (state, c, next_state))
    state = next_state
    assert state is not None

  tout = None
  if timeout.strings():
    assert len(timeout.strings()) == 1
    tout = timeout.strings()[0]

  br = None
  if breadth.strings():
    assert len(breadth.strings()) == 1
    br = breadth.strings()[0]

  return KFile(name, require.strings(), tout, br)

def removeExtension(file_name):
  assert file_name.endswith('.k'), file_name
  return file_name[:-2]

def semanticsName(file_name):
  return removeExtension(file_name)

def libraryName(file_name):
  return removeExtension(file_name) + '-files'

def proofName(file_name):
  return removeExtension(file_name)

def trustedName(file_name):
  if file_name.startswith('proof-'):
    return removeExtension('trusted' + file_name[5:])
  if file_name.startswith('lemma-'):
    return removeExtension(trustedFileName(file_name))
  assert False, file_name

def trustedFileName(file_name):
  assert file_name.startswith('lemma-'), file_name
  return 'trusted-' + file_name

def trustedLibraryName(file_name):
  return libraryName(trustedFileName(file_name))

def appendName(rule_name, out):
  out.append('  name = "')
  out.append(rule_name)
  out.append('",\n')

def appendSrcs(file_name, out):
  out.append('  srcs = ["')
  out.append(file_name)
  out.append('"],\n')

def appendDeps(name, deps, converter, dependency_resolver, is_proof, out, *, extra = []):
  if deps:
    out.append('  ')
    out.append(name)
    out.append(' = [\n')
    for r in deps:
      out.append('      "')
      out.append(converter(dependency_resolver.resolve(r, is_proof)))
      out.append('",\n')
    for r in extra:
      out.append('      "')
      out.append(r)
      out.append('",\n')
    out.append('  ],\n')
  else:
    out.append('  deps = [],\n')

def appendPublic(out):
  out.append('  visibility = ["//visibility:public"],\n')

def makeSemanticsRule(file, dependency_resolver, out):
  file_name = file.name()
  rule_name = semanticsName(file_name)

  out.append('kompile(\n')
  appendName(rule_name, out)
  appendSrcs(file_name, out)
  appendDeps('deps', file.require(), libraryName, dependency_resolver, False, out)
  appendPublic(out)
  out.append(')\n')
  out.append('\n')

def makeLibraryRule(file, dependency_resolver, out):
  file_name = file.name()
  rule_name = libraryName(file_name)

  out.append('klibrary(\n')
  appendName(rule_name, out)
  appendSrcs(file_name, out)
  appendDeps('deps', file.require(), libraryName, dependency_resolver, False, out)
  appendPublic(out)
  out.append(')\n')
  out.append('\n')

def makeProofRule(file, semantics, dependency_resolver, out):
  file_name = file.name()
  rule_name = proofName(file_name)
  #print('makeProofRule(%s)' % rule_name)

  out.append('kprove_test(\n')
  appendName(rule_name, out)
  appendSrcs(file_name, out)
  appendDeps('trusted', file.require(), removeExtension, dependency_resolver, True, out)
  out.append('  semantics = "')
  out.append(semantics)
  out.append('",\n')
  if (file.timeout()):
    out.append('  timeout = "')
    out.append(file.timeout())
    out.append('",\n')
  if (file.breadth()):
    out.append('  breadth = "')
    out.append(file.breadth())
    out.append('",\n')
  out.append(')\n')
  out.append('\n')

def makeTrustedRule(file, out):
  file_name = file.name()
  rule_name = trustedName(file_name)
  out.append('ktrusted(\n')
  appendName(rule_name, out)
  appendSrcs(file_name, out)
  appendPublic(out)
  out.append(')\n')
  out.append('\n')

def makeTrustedLibraryRule(file, trusted_file, dependency_resolver, out):
  file_name = file.name()
  rule_name = libraryName(trusted_file.name())
  trusted_name = ':' + trustedName(file_name)

  out.append('klibrary(\n')
  appendName(rule_name, out)
  appendSrcs(trusted_name, out)
  appendDeps('deps', trusted_file.require(), libraryName, dependency_resolver, False, out, extra = [trusted_name])
  appendPublic(out)
  out.append(')\n')
  out.append('\n')

class DependencyResolver(object):
  def __init__(self, root, current_dir):
    self.__root = root
    self.__current_dir = current_dir

  def resolve(self, path, is_proof):
    #print("Resolving %s (%s) with cd=%s and root=%s" % (path, is_proof, self.__current_dir, self.__root))
    if is_proof:
      full_path = os.path.join(self.__current_dir, path)
    else:
      full_path = os.path.join(self.__root, path)
    full_path = os.path.normpath(full_path)

    relative_to_current = os.path.relpath(full_path, self.__current_dir)
    #print('relpath(%s, %s) = %s' % (full_path, self.__current_dir, relative_to_current))
    split = os.path.split(relative_to_current)
    #print('split: %s' % str(split))
    if split[0]:
      relative_to_root = os.path.relpath(full_path, self.__root)
      #print('root_relpath(%s, %s) = %s' % (full_path, self.__root, relative_to_root))
      split = os.path.split(relative_to_root)
      #print('split: %s' % str(split))
      # print("%s -> //%s:%s" % (relative_to_root, pieces[0], pieces[1]))
      return "//%s:%s" % (split[0], split[1])
    return ":%s" % relative_to_current

def loadConfig(name):
  semantics = None
  skip = False
  with open(name, 'r') as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith('#'):
        continue
      (key, _, value) = line.partition(':')
      key = key.strip()
      value = value.strip()
      if key == 'semantics':
        semantics = value
      elif key == 'skip':
        skip = bool(value)
      else:
        assert False, "Unrecognized configuration key: '%s'." % key
  return (skip, semantics)

def generateBuildFile(current_dir, bazel_root):
  semantics = None
  skip = False
  config_file = os.path.join(current_dir, '.gen-bazel')
  print('Generating for: %s' % current_dir)
  if os.path.exists(config_file):
    skip, semantics = loadConfig(config_file)
  if skip:
    return

  dependency_resolver = DependencyResolver(bazel_root, current_dir)
  out = []
  libraries = []
  proofs = []
  lemmas = []
  main = None
  for fname in os.listdir(current_dir):
    if os.path.isdir(fname):
      continue
    if not fname.endswith('.k'):
      continue
    if fname.startswith('proof'):
      proofs.append(fname)
      continue
    if fname.startswith('lemma-'):
      lemmas.append(fname)
      continue
    if fname.endswith('-execute.k'):
      assert not main, [main, fname]
      main = fname
      continue
    libraries.append(fname)

  to_load = ['"//:k.bzl"']
  if main:
    assert not semantics, [current_dir, semantics, main]
    semantics = semanticsName(main)
    to_load.append('"kompile"')
    to_load.append('"klibrary"')
  elif libraries:
    to_load.append('"klibrary"')
  if proofs:
    to_load.append('"kprove_test"')
    to_load.append('"ktrusted"')
  if lemmas:
    to_load.append('"kprove_test"')
    to_load.append('"ktrusted"')
    to_load.append('"klibrary"')

  if not main and not libraries and not proofs and not lemmas:
    with open(os.path.join(current_dir, 'BUILD'), 'w') as f:
      f.write('')
    return

  assert semantics, "Semantics rule not present in the config file and no semantics could be found in the current directory (%s)." % current_dir

  out.append('load(')
  out.append(', '.join(sorted(set(to_load))))
  out.append(')\n')
  out.append('\n')

  if main:
    contents = loadFile(current_dir, main)
    makeSemanticsRule(contents, dependency_resolver, out)
    makeLibraryRule(contents, dependency_resolver, out)

  for l in sorted(libraries):
    contents = loadFile(current_dir, l)
    makeLibraryRule(contents, dependency_resolver, out)

  for p in sorted(proofs):
    contents = loadFile(current_dir, p)
    makeProofRule(contents, semantics, dependency_resolver, out)
    makeTrustedRule(contents, out)

  for l in sorted(lemmas):
    contents = loadFile(current_dir, l)
    trusted_contents = loadFileAsTrusted(current_dir, l, trustedFileName(l))

    makeProofRule(contents, semantics, dependency_resolver, out)
    makeTrustedRule(contents, out)
    makeTrustedLibraryRule(contents, trusted_contents, dependency_resolver, out)

  with open(os.path.join(current_dir, 'BUILD'), 'w') as f:
    f.write(''.join(out))

def recursiveGenBuild(current_dir, bazel_root):
  generateBuildFile(current_dir, bazel_root)
  for fname in os.listdir(current_dir):
    if fname.endswith('-kompiled'):
      continue
    if fname.startswith('tmp'):
      continue
    if fname == 'out':
      continue
    if os.path.isdir(os.path.join(current_dir, fname)):
      recursiveGenBuild(os.path.join(current_dir, fname), bazel_root)
      continue

def main(name, argv):
  # if len(argv) < 1 or len(argv) > 2:
  #   print("Usage: %s <bazel-root> [<main-semantics-rule>]" % name)
  bazel_root = subprocess.check_output('bazel info | grep "workspace:" | sed \'s/^.* //\'', shell=True)
  bazel_root = bazel_root.decode('utf-8').strip()
  recursiveGenBuild(os.path.join(bazel_root, 'protocol-correctness'), bazel_root)

if __name__ == '__main__':
  main(sys.argv[0], sys.argv[1:])
