import pytest

from toon import encode, decode
from tests.conftest import assert_roundtrip as _assert_rt


def test_roundtrip_primitives():
    for v in ["", "hello", "café", 0, 1, -1, 3.14, True, False, None]:
        _assert_rt(v)


def test_roundtrip_simple_objects():
    _assert_rt({"id": 1, "name": "Ada", "active": True, "note": "x,y"})


def test_roundtrip_nested_objects():
    _assert_rt({"a": {"b": {"c": "deep", "n": 1}}})


def test_roundtrip_primitive_arrays():
    _assert_rt(["a", "b", True, 10])


def test_roundtrip_object_arrays_tabular():
    _assert_rt([{"id": 1}, {"id": 2}])


def test_roundtrip_object_arrays_list():
    _assert_rt([{"id": 1}, {"id": 2, "name": "Ada"}])


def test_roundtrip_arrays_of_arrays():
    _assert_rt([[1, 2], []])


def test_roundtrip_root_arrays():
    _assert_rt(["x", "true", True, 10])


def test_roundtrip_complex_structures():
    _assert_rt({
        "user": {
            "id": 1,
            "name": "Ada",
            "items": [{"sku": "A", "qty": 1}, {"sku": "B", "qty": 2}],
            "tags": ["a", "b"],
        }
    })


@pytest.mark.parametrize("delim", ["\t", "|"])
def test_roundtrip_with_delimiters(delim):
    _assert_rt({"tags": ["a", "b"]}, {"delimiter": delim})
    _assert_rt([{"id": 1}, {"id": 2}], {"delimiter": delim})


def test_roundtrip_with_length_marker():
    _assert_rt({"tags": ["a", "b"]}, {"length_marker": True})


def test_roundtrip_with_combined_options():
    _assert_rt({"tags": ["a", "b"]}, {"delimiter": "|", "length_marker": True})


def test_roundtrip_special_characters():
    _assert_rt({"a": 'he said "hi"', "b": "x:y", "c": "[z]", "d": "- item"})


def test_roundtrip_unicode_and_emoji():
    _assert_rt({"u": "café", "zh": "你好", "e": "🚀"})


def test_roundtrip_empty_structures():
    _assert_rt({})
    _assert_rt([])
    _assert_rt({"a": []})
