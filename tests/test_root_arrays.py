from ptoon import decode, encode


def test_encodes_arrays_of_primitives_at_root_level():
    arr = ["x", "y", "true", True, 10]
    expected = '"[5]: x,y,"true",true,10"'  # placeholder to build correctly
    expected = '[5]: x,y,"true",true,10'
    assert encode(arr) == expected
    assert decode(expected) == arr


def test_encodes_arrays_of_similar_objects_in_tabular_format():
    arr = [{"id": 1}, {"id": 2}]
    expected = "[2]{id}:\n  1\n  2"
    assert encode(arr) == expected
    assert decode(expected) == arr


def test_encodes_arrays_of_different_objects_in_list_format():
    arr = [{"id": 1}, {"id": 2, "name": "Ada"}]
    expected = "[2]:\n  - id: 1\n  - id: 2\n    name: Ada"
    assert encode(arr) == expected
    assert decode(expected) == arr


def test_encodes_empty_arrays_at_root_level():
    expected = "[0]:"
    assert encode([]) == expected
    assert decode(expected) == []


def test_encodes_arrays_of_arrays_at_root_level():
    arr = [[1, 2], []]
    expected = "[2]:\n  - [2]: 1,2\n  - [0]:"
    assert encode(arr) == expected
    assert decode(expected) == arr
