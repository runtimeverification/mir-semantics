import pytest

from kmir.preprocessor import cleanup_hex_dump

CLEANUP_HEX_DUMP_TEST_DATA = (
    ('Hello World', 'Hello World'),
    ('  00 00 00 00 00 00 00 00                         │ ........', '  00 00 00 00 00 00 00 00'),
    ('  0x00 │ 00 00 00 00 00 00 00 00                         │ ........', '  0x00 | 00 00 00 00 00 00 00 00'),
)


@pytest.mark.parametrize(
    ('text', 'expected'),
    CLEANUP_HEX_DUMP_TEST_DATA,
    ids=[text for text, _ in CLEANUP_HEX_DUMP_TEST_DATA],
)
def test_cleanup_hex_dump(text: str, expected: str) -> None:
    # When
    actual = cleanup_hex_dump(text)

    # Then
    assert actual == expected
