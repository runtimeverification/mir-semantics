
def intersperse(element, list):
  had_elements = False
  for e in list:
    if had_elements:
      yield element
    yield e

class LemmaParser(object):
  DEFAULT = 0
  LEMMA = 1
  LEMMA_PROVES_LHS = 2
  LEMMA_PROVES_RHS = 3
  LEMMA_REQUIRES = 4
  LEMMA_ATTRIBUTES = 5
  LEMMA_END = 6

  def stateName(state):
    if state == LemmaParser.DEFAULT:
      return 'DEFAULT'
    if state == LemmaParser.LEMMA:
      return 'LEMMA'
    if state == LemmaParser.LEMMA_PROVES_LHS:
      return 'LEMMA_PROVES_LHS'
    if state == LemmaParser.LEMMA_PROVES_RHS:
      return 'LEMMA_PROVES_RHS'
    if state == LemmaParser.LEMMA_REQUIRES:
      return 'LEMMA_REQUIRES'
    if state == LemmaParser.LEMMA_ATTRIBUTES:
      return 'LEMMA_ATTRIBUTES'
    if state == LemmaParser.LEMMA_END:
      return 'LEMMA_END'
    assert False, "Unknown state: %s." % state

  DOUBLE_ARROW = '=>'
  EQUALS_K = '==K'

  def __init__(self, file_name):
    self.__state_start = -1
    self.__file_name = file_name

    self.__state = LemmaParser.DEFAULT
    self.__lemma_space_before = ""
    self.__prover = []
    self.__lhs = []
    self.__rhs = []
    self.__requires_space_before = ""
    self.__requires = []
    self.__attributes = []

  def toTrusted(self):
    result = []

    result.append(self.__lemma_space_before)
    result.append('rule\n')

    result.append('\n' * len(self.__prover))
    result.append('\n')

    result.extend(intersperse('\n', self.__lhs))
    result.append(LemmaParser.DOUBLE_ARROW)
    result.extend(intersperse('\n', self.__rhs))

    result.append(self.__requires_space_before)
    result.append('requires\n')
    result.extend(intersperse('\n', self.__requires))

    result.extend(intersperse('\n', self.__attributes))

    return ''.join(result)

  def toClaim(self):
    result = []
    result.append(self.__lemma_space_before)
    result.append('claim\n')

    result.extend(intersperse('\n', self.__prover))

    result.append(self.__requires_space_before)
    result.append('requires\n')
    result.extend(intersperse('\n', self.__requires))

    result.append(self.__requires_space_before)
    result.append('ensures\n')
    result.extend(intersperse('\n', self.__lhs))
    result.append(LemmaParser.EQUALS_K)
    result.extend(intersperse('\n', self.__rhs))
    result.append('\n' * len(self.__attributes))
    result.append('\n')
    return ''.join(result)

  def isParsing(self):
    return self.__state != LemmaParser.DEFAULT

  def finishedParsing(self):
    return self.__state == LemmaParser.LEMMA_END

  def reset(self):
    self.__state = LemmaParser.DEFAULT

  def processLine(self, line, normalized, line_number):
    previous_state = self.__state
    try:
      if self.__state == LemmaParser.DEFAULT:
        if normalized == 'lemma':
          self.__state = LemmaParser.LEMMA
          self.__lemma_space_before = ' ' * (len(line) - len(line.lstrip()))
          self.__prover = []
          self.__lhs = []
          self.__rhs = []
          self.__requires_space_before = None
          self.__requires = []
          self.__attributes = []
      elif self.__state == LemmaParser.LEMMA:
        if normalized == 'proves':
          assert self.__state == LemmaParser.LEMMA
          self.__state = LemmaParser.LEMMA_PROVES_LHS
        else:
          self.__prover.append(line)
      elif self.__state == LemmaParser.LEMMA_PROVES_LHS:
          pos = line.find(LemmaParser.DOUBLE_ARROW)
          if pos >= 0:
            self.__lhs.append(line[:pos])
            self.__rhs.append(line[pos + 2:])
            self.__state = LemmaParser.LEMMA_PROVES_RHS
          else:
            self.__lhs.append(line)
      elif self.__state == LemmaParser.LEMMA_PROVES_RHS:
        if normalized == 'requires':
          self.__requires_space_before = ' ' * (len(line) - len(line.lstrip()))
          self.__state = LemmaParser.LEMMA_REQUIRES
        else:
          self.__rhs.append(line)
      elif self.__state == LemmaParser.LEMMA_REQUIRES:
        if normalized == 'endlemma':
          self.__state = LemmaParser.LEMMA_END
        elif normalized.startswith('['):
          self.__attributes.append(line)
          self.__state = LemmaParser.LEMMA_ATTRIBUTES
        else:
          self.__requires.append(line)
      elif self.__state == LemmaParser.LEMMA_ATTRIBUTES:
        if normalized == 'endlemma':
          self.__state = LemmaParser.LEMMA_END
        else:
          self.__attributes.append(line)
      else:
        assert False
    finally:
      if previous_state != self.__state:
        self.__state_start = line_number

  def checkDefault(self):
    assert self.__state == LemmaParser.DEFAULT, (
        "Unexpected lemma parsing state at the end of file: %s. This state started here: %s:%s."
        % (LemmaParser.stateName(self.__state), self.__file_name, self.__state_start)
    )


DEFAULT = 0
PROOF = 1
TRUSTED = 2

def makeTrusted(file_name, lines):
  lemma_parser = LemmaParser(file_name)
  state = DEFAULT
  for (line_number, line) in lines:
    normalized = line.strip()

    lemma_parser.processLine(line, normalized, line_number)
    if lemma_parser.isParsing():
      if lemma_parser.finishedParsing():
        yield lemma_parser.toTrusted()
        lemma_parser.reset()
      continue
    if normalized.startswith('//@'):
      if state == DEFAULT:
        if normalized == '//@ proof':
          state = PROOF
        else:
          raise Exception(
            "Unexpected trusted directive, only '//@ proof' allowed here.\n%s:%d"
            % (file_name, line_number))
      elif state == PROOF:
        if normalized == '//@ trusted':
          state = TRUSTED
        else:
          raise Exception(
            "Unexpected trusted directive, only '//@ trusted' allowed here.\n%s:%d"
            % (file_name, line_number))
      elif state == TRUSTED:
        if normalized == '//@ end':
          state = DEFAULT
        else:
          raise Exception(
            "Unexpected trusted directive, only '//@ end' allowed here.\n%s:%d"
            % (file_name, line_number))
    else:
      if state == DEFAULT:
        pass
      else:
        unindented = line.lstrip()
        indentation = ' ' * (len(line) - len(unindented))
        if state == PROOF:
          line = indentation + '// ' + unindented
        elif state == TRUSTED:
          if unindented.startswith('// '):
            line = indentation + unindented[3:]
          else:
            raise Exception(
              "Expected trusted lines to be commented.\n%s:%d"
              % (file_name, line_number))
    yield line
  lemma_parser.checkDefault()
