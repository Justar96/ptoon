import sys

from toon import encode, decode


def test_encodes_safe_strings_without_quotes():
    assert encode("hello") == "hello"
    assert encode("Ada_99") == "Ada_99"


def test_quotes_empty_string():
    assert encode("") == '""'


def test_quotes_strings_that_look_like_booleans_or_numbers():
    for s in ["true", "false", "null", "42", "-3.14", "1e-6", "05"]:
        assert encode(s) == f'"{s}"'


def test_escapes_control_characters_in_strings():
    assert encode("line1\nline2") == '"line1\\nline2"'
    assert encode("tab\tsep") == '"tab\\tsep"'
    assert encode("carriage\rret") == '"carriage\\rret"'
    assert encode("back\\slash") == '"back\\\\slash"'


def test_quotes_strings_with_structural_characters():
    for s in ["a:b", "[x]", "{y}", "- item", "a,b"]:
        assert encode(s).startswith('"') and encode(s).endswith('"')


def test_handles_unicode_and_emoji():
    for s in ["café", "你好", "🚀", "hello 👋 world"]:
        assert encode(s) == s


def test_encodes_numbers():
    assert encode(42) == "42"
    assert encode(3.14) == "3.14"
    assert encode(-7) == "-7"
    assert encode(0) == "0"


def test_handles_special_numeric_values():
    assert encode(-0.0) == "0"
    assert encode(1_000_000) == "1000000"
    assert encode(0.000001) in ("1e-06", "0.000001")
    assert encode(10**20) == f'"{10**20}"'
    assert encode(sys.maxsize) == f'"{sys.maxsize}"'


def test_encodes_booleans():
    assert encode(True) == "true"
    assert encode(False) == "false"


def test_encodes_none():
    assert encode(None) == "null"
