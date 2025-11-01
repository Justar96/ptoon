from ptoon import decode, encode


def test_encodes_arrays_of_similar_objects_in_tabular_format():
    obj = {
        "items": [
            {"sku": "A", "qty": 1, "price": 9.99},
            {"sku": "B", "qty": 2, "price": 1.5},
        ]
    }
    expected = "items[2]{sku,qty,price}:\n  A,1,9.99\n  B,2,1.5"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_handles_null_values_in_tabular_format():
    obj = {"rows": [{"a": None, "b": 1}, {"a": "x", "b": None}]}
    expected = "rows[2]{a,b}:\n  null,1\n  x,null"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_quotes_strings_containing_delimiters_in_tabular_rows():
    obj = {"items": [{"k": "a,b", "v": "x:y"}, {"k": "c", "v": "d"}]}
    expected = 'items[2]{k,v}:\n  "a,b","x:y"\n  c,d'
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_quotes_ambiguous_strings_in_tabular_rows():
    obj = {"t": [{"x": "true", "y": "42"}, {"x": "false", "y": "-3.14"}]}
    expected = 't[2]{x,y}:\n  "true","42"\n  "false","-3.14"'
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_handles_tabular_arrays_with_keys_needing_quotes():
    obj = {
        "data": [
            {"order:id": 1, "full name": "Ada"},
            {"order:id": 2, "full name": "Bob"},
        ]
    }
    expected = 'data[2]{"order:id","full name"}:\n  1,Ada\n  2,Bob'
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_uses_list_format_for_objects_with_different_fields():
    obj = {"items": [{"a": 1}, {"a": 2, "b": 3}]}
    expected = "items[2]:\n  - a: 1\n  - a: 2\n    b: 3"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_uses_list_format_for_objects_with_nested_values():
    obj = {"items": [{"a": {"x": 1}}, {"a": 2}]}
    expected = "items[2]:\n  - a:\n      x: 1\n  - a: 2"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_preserves_field_order_in_list_items():
    obj = {"items": [{"name": "t", "id": 1, "active": True}]}
    expected = "items[1]:\n  - name: t\n    id: 1\n    active: true"
    assert encode(obj) == expected


def test_preserves_field_order_when_primitive_appears_first():
    obj = {"items": [{"name": "test", "nums": [1, 2, 3]}]}
    expected = "items[1]:\n  - name: test\n    nums[3]: 1,2,3"
    assert encode(obj) == expected


def test_uses_list_format_for_objects_containing_arrays_of_arrays():
    obj = {"items": [{"grid": [[1], [2, 3]]}]}
    expected = "items[1]:\n  - grid[2]:\n      - [1]: 1\n      - [2]: 2,3"
    assert encode(obj) == expected


def test_uses_tabular_format_for_nested_uniform_object_arrays():
    obj = {"items": [{"users": [{"id": 1}, {"id": 2}]}]}
    expected = "items[1]:\n  - users[2]{id}:\n      1\n      2"
    assert encode(obj) == expected


def test_uses_list_format_for_nested_object_arrays_with_mismatched_keys():
    obj = {"items": [{"users": [{"id": 1}, {"id": 2, "name": "x"}]}]}
    expected = "items[1]:\n  - users[2]:\n      - id: 1\n      - id: 2\n        name: x"
    assert encode(obj) == expected


def test_uses_list_format_for_objects_with_multiple_array_fields():
    obj = {"items": [{"a": [1], "b": [2, 3]}]}
    expected = "items[1]:\n  - a[1]: 1\n    b[2]: 2,3"
    assert encode(obj) == expected


def test_uses_list_format_for_objects_with_only_array_fields():
    obj = {"items": [{"a": [1], "b": []}]}
    expected = "items[1]:\n  - a[1]: 1\n    b[0]:"
    assert encode(obj) == expected


def test_handles_objects_with_empty_arrays_in_list_format():
    obj = {"items": [{"name": "test", "data": []}]}
    expected = "items[1]:\n  - name: test\n    data[0]:"
    assert encode(obj) == expected


def test_places_first_field_of_nested_tabular_arrays_on_hyphen_line():
    obj = {"items": [{"users": [{"id": 1}, {"id": 2}], "other": 1}]}
    expected = "items[1]:\n  - users[2]{id}:\n      1\n      2\n    other: 1"
    assert encode(obj) == expected


def test_places_empty_arrays_on_hyphen_line_when_first():
    obj = {"items": [{"data": [], "name": "x"}]}
    expected = "items[1]:\n  - data[0]:\n    name: x"
    assert encode(obj) == expected


def test_uses_field_order_from_first_object_for_tabular_headers():
    obj = {"items": [{"b": 2, "a": 1}, {"b": 3, "a": 4}]}
    expected = "items[2]{b,a}:\n  2,1\n  3,4"
    assert encode(obj) == expected
    assert decode(expected) == obj


def test_tabular_header_order_deterministic_for_mixed_insertion():
    obj = {"items": [{"b": 2, "a": 1}, {"a": 4, "b": 3}, {"b": 5, "a": 6}]}
    toon = encode(obj)
    assert toon.startswith("items[3]{b,a}:")
    assert decode(toon) == obj


def test_uses_list_format_for_one_object_with_nested_column():
    obj = {"items": [{"a": 1, "b": {"x": 1}}, {"a": 2, "b": 2}]}
    expected = "items[2]:\n  - a: 1\n    b:\n      x: 1\n  - a: 2\n    b: 2"
    assert encode(obj) == expected


def test_roundtrip_nested_object_as_second_field_in_list_item():
    """Test decoding nested objects that appear as subsequent fields (not first field) in list items."""
    obj = {"items": [{"id": 1, "nested": {"a": 1, "b": 2}}]}
    toon_str = encode(obj)
    assert decode(toon_str) == obj


def test_roundtrip_ecommerce_structure():
    """Test decoding E-Commerce-like structures with nested customer objects."""
    obj = {
        "orders": [
            {
                "orderId": "abc123",
                "customer": {"id": 7825, "name": "Alice", "email": "alice@example.com"},
                "total": 99.99,
            }
        ]
    }
    toon_str = encode(obj)
    assert decode(toon_str) == obj


def test_roundtrip_deeply_nested_objects_in_list_items():
    """Test decoding deeply nested object structures within list items."""
    obj = {"items": [{"level1": {"level2": {"level3": 123}}}]}
    toon_str = encode(obj)
    assert decode(toon_str) == obj
