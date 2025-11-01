import importlib.util

import pytest

from ptoon import count_tokens, decode, encode


requires_tiktoken = pytest.mark.skipif(importlib.util.find_spec("tiktoken") is None, reason="requires tiktoken")


def test_produces_no_trailing_spaces_at_end_of_lines():
    data = {
        "user": {
            "name": "Ada",
            "items": [
                {"id": 1, "name": "x"},
                {"id": 2, "name": "y"},
            ],
            "tags": ["a", "b"],
        }
    }
    out = encode(data)
    for line in out.split("\n"):
        assert not line.endswith(" ")


def test_produces_no_trailing_newline_at_end_of_output():
    data = {"a": 1, "b": [1, 2], "c": {"x": "y"}}
    out = encode(data)
    assert not out.endswith("\n")


def test_indent_zero_with_flat_object():
    """indent=0 should work for flat objects without nesting."""
    data = {"name": "Alice", "age": 30, "active": True}
    out = encode(data, options={"indent": 0})
    expected = "name: Alice\nage: 30\nactive: true"
    assert out == expected
    # Verify roundtrip
    assert decode(expected) == data


def test_indent_zero_with_flat_array():
    """indent=0 should work for flat arrays."""
    data = {"items": [1, 2, 3], "count": 3}
    out = encode(data, options={"indent": 0})
    expected = "items[3]: 1,2,3\ncount: 3"
    assert out == expected
    # Verify roundtrip
    assert decode(expected) == data


def test_indent_zero_nested_roundtrip_preserves_structure():
    """indent=0 should preserve structure for nested objects via minimal spacing."""
    data = {
        "user": {
            "profile": {"name": "Alice", "age": 30},
            "roles": ["admin", "editor"],
        }
    }
    encoded = encode(data, options={"indent": 0})
    decoded = decode(encoded)
    assert decoded == data


@requires_tiktoken
def test_indent_zero_minimizes_token_count():
    """indent=0 should never increase token usage compared to default spacing."""
    data = {
        "items": [{"id": i, "label": f"item-{i}"} for i in range(5)],
        "metadata": {"source": "unit-test", "active": True},
    }

    default_tokens = count_tokens(encode(data))
    no_indent_tokens = count_tokens(encode(data, options={"indent": 0}))

    assert no_indent_tokens <= default_tokens
    assert no_indent_tokens > 0


def test_decode_rejects_mixed_tabs_and_spaces():
    doc = "items[1]:\n \t- 1"

    with pytest.raises(ValueError, match="tab character found in indentation"):
        decode(doc)
