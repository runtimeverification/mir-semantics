import re

LINE_COMMENT_REGEXP = re.compile(r'^((?:[^/"]|/[^/"]|/?"(?:[^\\"]|\\.)*")*)//.*$')
HEX_CLEANUP_SUFFIX = re.compile(r'^(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$')
HEX_CLEANUP_SEPARATOR = re.compile(r'^(\s+0x[0-9a-fA-F]+\s+)│(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$')


def preprocess(program_text: str) -> str:
    def process_line(line: str) -> str:
        line = line.rstrip()
        line = remove_comments(line)
        line = cleanup_hex_dump(line)
        line = line.rstrip()
        return line

    return '\n'.join(process_line(line) for line in program_text.splitlines())


def remove_comments(line: str) -> str:
    m = LINE_COMMENT_REGEXP.match(line)
    if not m:
        return line
    return m.group(1)


def cleanup_hex_dump(line: str) -> str:
    m = HEX_CLEANUP_SUFFIX.match(line)
    if not m:
        m = HEX_CLEANUP_SEPARATOR.match(line)
        if not m:
            return line
        return '%s|%s' % (m.group(1), m.group(2))
    return m.group(1)
