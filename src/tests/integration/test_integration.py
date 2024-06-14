from mir_semantics.hello import hello


def test_hello() -> None:
    assert hello('World') == 'Hello, World!'
