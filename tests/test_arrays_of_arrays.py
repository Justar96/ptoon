from ptoon import decode, encode


def test_encodes_nested_arrays_of_primitives():
    obj = {"pairs": [["a", "b"], ["c", "d"]]}
    expected = "pairs[2]:\n  - [2]: a,b\n  - [2]: c,d"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_quotes_strings_containing_delimiters_in_nested_arrays():
    obj = {"pairs": [["a,b", "x:y"], ["d", "e"]]}
    expected = 'pairs[2]:\n  - [2]: "a,b","x:y"\n  - [2]: d,e'
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_handles_empty_inner_arrays():
    obj = {"pairs": [[], []]}
    expected = "pairs[2]:\n  - [0]:\n  - [0]:"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_handles_mixed_length_inner_arrays():
    obj = {"pairs": [[1], [2, 3]]}
    expected = "pairs[2]:\n  - [1]: 1\n  - [2]: 2,3"
    assert encode(obj) == expected
    assert decode(expected) == obj
