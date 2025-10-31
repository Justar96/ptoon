from ptoon import decode, encode


def test_preserves_key_order_in_objects():
    obj = {"id": 123, "name": "Ada", "active": True}
    expected = "id: 123\nname: Ada\nactive: true"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_null_values_in_objects():
    obj = {"id": 123, "value": None}
    expected = "id: 123\nvalue: null"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_empty_objects_as_empty_string():
    assert encode({}) == ""
    assert decode("") == {}


def test_quotes_string_values_with_special_characters():
    obj = {"a": "x:y", "b": "a,b", "c": "line1\nline2", "d": '"q"'}
    out = encode(obj)
    assert 'a: "x:y"' in out
    assert 'b: "a,b"' in out
    assert 'c: "line1\\nline2"' in out
    assert 'd: "\\"q\\""' in out
    assert decode(out) == obj


def test_quotes_string_values_with_leading_trailing_spaces():
    obj1 = {"text": " padded "}
    obj2 = {"text": "  "}
    assert encode(obj1) == 'text: " padded "'
    assert encode(obj2) == 'text: "  "'


def test_quotes_string_values_that_look_like_booleans_numbers():
    assert encode({"v": "true"}) == 'v: "true"'
    assert encode({"v": "42"}) == 'v: "42"'


def test_quotes_keys_with_special_characters():
    assert encode({"order:id": 7}).startswith('"order:id": 7')


def test_quotes_keys_with_spaces_or_leading_hyphens():
    assert encode({"full name": "Ada"}) == '"full name": Ada'
    assert encode({"-lead": 1}) == '"-lead": 1'


def test_quotes_numeric_keys():
    assert encode({123: "x"}) == '"123": x'


def test_quotes_empty_string_key():
    assert encode({"": 1}) == '"": 1'


def test_escapes_control_characters_in_keys():
    out = encode({"line\nkey": 1, "tab\tkey": 2})
    assert '"line\\nkey": 1' in out
    assert '"tab\\tkey": 2' in out


def test_escapes_quotes_in_keys():
    assert encode({'he said "hi"': 1}) == '"he said \\"hi\\"": 1'


def test_encodes_deeply_nested_objects():
    obj = {"a": {"b": {"c": "deep"}}}
    expected = "a:\n  b:\n    c: deep"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_encodes_empty_nested_object():
    obj = {"user": {}}
    expected = "user:"
    assert encode(obj) == expected
    assert decode(expected) == {"user": {}}
