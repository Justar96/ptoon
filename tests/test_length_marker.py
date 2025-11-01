from ptoon import decode, encode


def test_adds_length_marker_to_primitive_arrays():
    obj = {"tags": ["reading", "gaming", "coding"]}
    expected = "tags[#3]: reading,gaming,coding"
    assert encode(obj, {"length_marker": True}) == expected
    assert decode(expected, {"length_marker": True}) == obj


def test_handles_empty_arrays_with_length_marker():
    obj = {"items": []}
    expected = "items[#0]:"
    assert encode(obj, {"length_marker": True}) == expected
    assert decode(expected, {"length_marker": True}) == obj


def test_adds_length_marker_to_tabular_arrays():
    obj = {"rows": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
    expected = "rows[#2]{a,b}:\n  1,2\n  3,4"
    assert encode(obj, {"length_marker": True}) == expected


def test_adds_length_marker_to_nested_arrays():
    obj = {"pairs": [[1, 2], [3]]}
    expected = "pairs[#2]:\n  - [#2]: 1,2\n  - [#1]: 3"
    assert encode(obj, {"length_marker": True}) == expected


def test_works_with_delimiter_option():
    obj = {"tags": ["reading", "gaming", "coding"]}
    expected = "tags[#3|]: reading|gaming|coding"
    assert encode(obj, {"length_marker": True, "delimiter": "|"}) == expected


def test_default_is_false_no_length_marker():
    obj = {"tags": ["a", "b"]}
    assert encode(obj) == "tags[2]: a,b"
