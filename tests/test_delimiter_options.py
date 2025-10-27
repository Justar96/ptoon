import pytest

from toon import encode, decode


# A. Basic Delimiter Usage
@pytest.mark.parametrize("delimiter,obj,expected", [
    ("\t", {"tags": ["reading", "gaming"]}, "tags[2\t]: reading\tgaming"),
    ("|", {"nums": [1, 2, 3]}, "nums[3|]: 1|2|3"),
])
def test_encodes_primitive_arrays_with_delimiter(delimiter, obj, expected):
    assert encode(obj, {"delimiter": delimiter}) == expected
    assert decode(expected, {"delimiter": delimiter}) == obj


def test_encodes_primitive_arrays_with_comma_delimiter():
    obj = {"nums": [1, 2, 3]}
    expected = "nums[3]: 1,2,3"
    assert encode(obj, {"delimiter": ","}) == expected


@pytest.mark.parametrize("delimiter,expected", [
    ("\t", "items[2\t]{a\tb}:\n  1\t2\n  3\t4"),
    ("|", "items[2|]{a|b}:\n  1|2\n  3|4"),
])
def test_encodes_tabular_arrays_with_delimiter(delimiter, expected):
    obj = {"items": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
    assert encode(obj, {"delimiter": delimiter}) == expected
    assert decode(expected, {"delimiter": delimiter}) == obj


@pytest.mark.parametrize("delimiter,obj,expected", [
    ("\t", {"pairs": [["a", "b"], ["c", "d"]]}, "pairs[2\t]:\n  - [2\t]: a\tb\n  - [2\t]: c\td"),
    ("|", {"pairs": [[1, 2], [3, 4]]}, "pairs[2|]:\n  - [2|]: 1|2\n  - [2|]: 3|4"),
])
def test_encodes_nested_arrays_with_delimiter(delimiter, obj, expected):
    assert encode(obj, {"delimiter": delimiter}) == expected
    assert decode(expected, {"delimiter": delimiter}) == obj


@pytest.mark.parametrize("delimiter,arr,expected", [
    ("\t", ["x", "y", True], "[3\t]: x\ty\ttrue"),
    ("|", [1, 2, 3], "[3|]: 1|2|3"),
])
def test_encodes_root_arrays_with_delimiter(delimiter, arr, expected):
    assert encode(arr, {"delimiter": delimiter}) == expected
    assert decode(expected, {"delimiter": delimiter}) == arr


@pytest.mark.parametrize("delimiter,expected", [
    ("\t", "[2\t]{id}:\n  1\n  2"),
    ("|", "[2|]{id}:\n  1\n  2"),
])
def test_encodes_root_arrays_of_objects_with_delimiter(delimiter, expected):
    arr = [{"id": 1}, {"id": 2}]
    assert encode(arr, {"delimiter": delimiter}) == expected
    assert decode(expected, {"delimiter": delimiter}) == arr


# B. Delimiter-Aware Quoting
@pytest.mark.parametrize("delimiter,obj,expected", [
    ("\t", {"tags": ["a\tb", "c"]}, 'tags[2\t]: "a\tb"\tc'),
    ("|", {"tags": ["a|b", "c"]}, 'tags[2|]: "a|b"|c'),
])
def test_quotes_strings_containing_delimiter(delimiter, obj, expected):
    assert encode(obj, {"delimiter": delimiter}) == expected


@pytest.mark.parametrize("delimiter,expected", [
    ("\t", 'tags[2\t]: a,b\tc'),
    ("|", 'tags[2|]: a,b|c'),
])
def test_does_not_quote_commas_with_non_comma_delimiter(delimiter, expected):
    obj = {"tags": ["a,b", "c"]}
    assert encode(obj, {"delimiter": delimiter}) == expected


def test_quotes_tabular_values_containing_the_delimiter():
    obj = {"rows": [{"a": "x|y", "b": "m"}, {"a": "n", "b": "o"}]}
    expected = (
        "rows[2|]{a|b}:\n"
        "  \"x|y\"|m\n"
        "  n|o"
    )
    assert encode(obj, {"delimiter": "|"}) == expected


def test_does_not_quote_commas_in_object_values_with_non_comma_delimiter():
    obj = {"a": "x,y"}
    assert encode(obj, {"delimiter": "|"}) == 'a: x,y'
    assert encode(obj, {"delimiter": "\t"}) == 'a: x,y'


def test_quotes_nested_array_values_containing_the_delimiter():
    obj = {"pairs": [["a|b", "c"], ["d", "e"]]}
    expected = (
        "pairs[2|]:\n"
        "  - [2|]: \"a|b\"|c\n"
        "  - [2|]: d|e"
    )
    assert encode(obj, {"delimiter": "|"}) == expected


# C. Delimiter-Independent Quoting Rules
@pytest.mark.parametrize("delim", [",", "\t", "|"])
def test_preserves_ambiguity_quoting_regardless_of_delimiter(delim):
    obj = {"v": ["true", "42"]}
    out = encode(obj, {"delimiter": delim})
    assert '"true"' in out and '"42"' in out


@pytest.mark.parametrize("delim", [",", "\t", "|"])
def test_preserves_structural_quoting_regardless_of_delimiter(delim):
    obj = {"items": ["[5]", "{key}"]}
    out = encode(obj, {"delimiter": delim})
    assert '"[5]"' in out and '"{key}"' in out


def test_quotes_keys_containing_the_delimiter():
    obj = {"a|b": 1, "x\ty": 2}
    out_pipe = encode(obj, {"delimiter": "|"})
    out_tab = encode(obj, {"delimiter": "\t"})
    assert '"a|b": 1' in out_pipe
    assert '"x\\ty": 2' in out_tab


def test_quotes_tabular_headers_containing_the_delimiter():
    obj = {"rows": [{"a|b": 1, "x\ty": 2}, {"a|b": 3, "x\ty": 4}]}
    out = encode(obj, {"delimiter": "|"})
    assert out.startswith('rows[2|]{"a|b"|"x\\ty"}:')


def test_header_uses_the_active_delimiter():
    obj = {"rows": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
    out_tab = encode(obj, {"delimiter": "\t"})
    assert out_tab.startswith('rows[2\t]{a\tb}:')
    out_pipe = encode(obj, {"delimiter": "|"})
    assert out_pipe.startswith('rows[2|]{a|b}:')


# D. Formatting Invariants with Delimiters
@pytest.mark.parametrize("delimiter", ["\t", "|"])
def test_produces_no_trailing_spaces_with_delimiter(delimiter):
    out = encode({"tags": ["a", "b"]}, {"delimiter": delimiter})
    for line in out.split("\n"):
        assert not line.endswith(" ")


@pytest.mark.parametrize("delimiter", ["\t", "|"])
def test_produces_no_trailing_newline_with_delimiter(delimiter):
    out = encode({"tags": ["a", "b"]}, {"delimiter": delimiter})
    assert not out.endswith("\n")
