from toon import decode, encode


def test_encodes_string_arrays_inline():
    obj = {"tags": ["reading", "gaming"]}
    expected = "tags[2]: reading,gaming"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_number_arrays_inline():
    obj = {"nums": [1, 2, 3]}
    expected = "nums[3]: 1,2,3"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_mixed_primitive_arrays_inline():
    obj = {"data": ["x", "y", True, 10]}
    expected = "data[4]: x,y,true,10"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_empty_arrays():
    obj = {"items": []}
    expected = "items[0]:"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_handles_empty_string_in_arrays():
    assert encode({"items": [""]}) == 'items[1]: ""'
    assert encode({"items": ["a", "", "b"]}) == 'items[3]: a,"",b'


def test_handles_whitespace_only_strings_in_arrays():
    assert encode({"items": [" ", "  "]}) == 'items[2]: " ","  "'


def test_quotes_array_strings_with_special_characters():
    assert encode({"items": ["a", "b,c", "d:e"]}) == 'items[3]: a,"b,c","d:e"'


def test_quotes_strings_that_look_like_booleans_numbers_in_arrays():
    assert (
        encode({"items": ["x", "true", "42", "-3.14"]})
        == 'items[4]: x,"true","42","-3.14"'
    )


def test_quotes_strings_with_structural_meanings_in_arrays():
    assert (
        encode({"items": ["[5]", "- item", "{key}"]})
        == 'items[3]: "[5]","- item","{key}"'
    )
