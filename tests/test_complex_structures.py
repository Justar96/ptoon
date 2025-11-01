from ptoon import decode, encode


def test_encodes_objects_with_mixed_arrays_and_nested_objects():
    obj = {
        "user": {
            "id": 1,
            "name": "Ada",
            "tags": ["a", "b"],
            "prefs": {"theme": "dark", "beta": True},
            "items": [],
        }
    }
    expected = "user:\n  id: 1\n  name: Ada\n  tags[2]: a,b\n  prefs:\n    theme: dark\n    beta: true\n  items[0]:"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_uses_list_format_for_arrays_mixing_primitives_and_objects():
    obj = {"items": [1, {"a": 1}, "text"]}
    expected = "items[3]:\n  - 1\n  - a: 1\n  - text"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_uses_list_format_for_arrays_mixing_objects_and_arrays():
    obj = {"items": [{"a": 1}, [1, 2]]}
    expected = "items[2]:\n  - a: 1\n  - [2]: 1,2"
    assert encode(obj) == expected
    assert decode(expected) == obj
