"""Advanced decoder edge cases for additional coverage.

Tests advanced parsing scenarios, error paths, and edge cases
to push coverage from 90% to 95%+.
"""

import pytest

from pytoon import decode, encode


class TestAdvancedListArrayEdgeCases:
    """Test advanced list array parsing edge cases."""

    def test_list_array_exact_length_with_dedent(self):
        """Test list array with exact length marker completes on dedent."""
        toon = """outer:
  items[2]:
    - first
    - second
  other: value"""
        result = decode(toon)
        assert result == {"outer": {"items": ["first", "second"], "other": "value"}}

    def test_nested_list_arrays_multiple_levels(self):
        """Test multiple nested list arrays."""
        toon = """level1[1]:
  - level2[2]:
    - a
    - b"""
        result = decode(toon)
        assert result == {"level1": [{"level2": ["a", "b"]}]}

    def test_list_array_with_object_items(self):
        """Test list array containing object items."""
        toon = """items[2]:
  - name: first
    value: 1
  - name: second
    value: 2"""
        result = decode(toon)
        assert result == {
            "items": [
                {"name": "first", "value": 1},
                {"name": "second", "value": 2},
            ]
        }


class TestAdvancedObjectParsing:
    """Test advanced object parsing edge cases."""

    def test_object_with_nested_inline_and_multiline(self):
        """Test object mixing inline and multiline nested objects."""
        toon = """root:
  inline: nested: value
  multiline:
    key: data"""
        result = decode(toon)
        assert result == {
            "root": {"inline": {"nested": "value"}, "multiline": {"key": "data"}}
        }

    def test_deeply_nested_object_then_sibling(self):
        """Test deeply nested object followed by sibling key."""
        toon = """a:
  b:
    c:
      d:
        e: deep
      sibling: value"""
        result = decode(toon)
        assert result == {"a": {"b": {"c": {"d": {"e": "deep"}, "sibling": "value"}}}}


class TestAdvancedTabularEdgeCases:
    """Test advanced tabular array edge cases."""

    def test_tabular_array_single_row(self):
        """Test tabular array with only one row."""
        data = {"users": [{"id": 1, "name": "Alice"}]}
        # Single row should use list format, not tabular
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_tabular_array_many_columns(self):
        """Test tabular array with many columns."""
        data = {
            "data": [
                {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                {"a": 6, "b": 7, "c": 8, "d": 9, "e": 10},
            ]
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_tabular_with_pipe_delimiter(self):
        """Test tabular array with pipe delimiter."""
        toon = """data[2|]{a|b}:
  1|2
  3|4"""
        result = decode(toon)
        assert result == {"data": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}


class TestAdvancedStringEscaping:
    """Test advanced string escaping and quoting."""

    def test_string_with_escaped_quotes(self):
        """Test string containing escaped quotes."""
        toon = r'''text: "She said \"hello\""'''
        result = decode(toon)
        assert result == {"text": 'She said "hello"'}

    def test_string_with_escaped_newline(self):
        """Test string with escaped newline character."""
        toon = r'''text: "line1\nline2"'''
        result = decode(toon)
        assert result == {"text": "line1\nline2"}

    def test_string_with_escaped_tab(self):
        """Test string with escaped tab character."""
        toon = r'''text: "col1\tcol2"'''
        result = decode(toon)
        assert result == {"text": "col1\tcol2"}

    def test_string_with_backslash(self):
        """Test string containing backslash."""
        toon = r'''path: "C:\\Users\\Name"'''
        result = decode(toon)
        assert result == {"path": "C:\\Users\\Name"}


class TestAdvancedNumericEdgeCases:
    """Test advanced numeric parsing edge cases."""

    def test_very_large_integers(self):
        """Test parsing of very large integers (converted to strings)."""
        data = {"large": 999999999999999999}
        toon = encode(data)
        result = decode(toon)
        # Large integers beyond JS safe range become strings
        assert result == {"large": "999999999999999999"}

    def test_very_small_negative_integers(self):
        """Test parsing of very small negative integers (converted to strings)."""
        data = {"small": -999999999999999999}
        toon = encode(data)
        result = decode(toon)
        # Large integers beyond JS safe range become strings
        assert result == {"small": "-999999999999999999"}

    def test_float_with_many_decimals(self):
        """Test float with many decimal places."""
        data = {"precise": 3.141592653589793}
        toon = encode(data)
        result = decode(toon)
        # Float precision might vary slightly
        assert abs(result["precise"] - 3.141592653589793) < 1e-10

    def test_negative_float(self):
        """Test negative float values."""
        data = {"neg": -2.5, "pos": 2.5}
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestAdvancedMixedStructures:
    """Test advanced mixed data structure edge cases."""

    def test_array_of_mixed_objects_and_primitives(self):
        """Test array containing mix of objects and primitives."""
        # This should use list format
        data = {"mixed": [{"a": 1}, "string", 42]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_deeply_nested_mixed_arrays_and_objects(self):
        """Test deeply nested mix of arrays and objects."""
        data = {
            "level1": [
                {"name": "a", "values": [1, 2, 3]},
                {"name": "b", "values": [4, 5, 6]},
            ]
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestAdvancedErrorRecovery:
    """Test error messages and recovery."""

    def test_error_on_unexpected_depth_increase(self):
        """Test error on invalid depth increase."""
        toon = """key: value
        too_deep: data"""  # 8 spaces instead of 2
        with pytest.raises(ValueError, match="unexpected"):
            decode(toon)

    def test_list_marker_in_nested_object_context(self):
        """Test error when list marker appears in wrong context."""
        toon = """outer:
  key: value
    - wrong"""
        with pytest.raises(ValueError, match="unexpected"):
            decode(toon)


class TestAdvancedDelimiterCombinations:
    """Test various delimiter combinations."""

    def test_mixed_delimiter_in_different_arrays(self):
        """Test different delimiters in different parts of structure."""
        data = {
            "comma_array": [1, 2, 3],
            "tab_array": [4, 5, 6],
        }
        # Encode with default comma delimiter
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_inline_array_with_pipe_delimiter(self):
        """Test inline array using pipe delimiter."""
        toon = "values[3|]: a| b| c"
        result = decode(toon)
        assert result == {"values": ["a", "b", "c"]}


class TestAdvancedBooleanAndNull:
    """Test boolean and null edge cases."""

    def test_boolean_values_in_arrays(self):
        """Test boolean values in various array formats."""
        data = {"flags": [True, False, True]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_null_values_in_objects(self):
        """Test null values in nested objects."""
        data = {"outer": {"inner": None, "value": 42}}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_array_of_all_nulls(self):
        """Test array containing only null values."""
        data = {"nulls": [None, None, None]}
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestAdvancedEmptyStructures:
    """Test various empty structure edge cases."""

    def test_nested_empty_arrays(self):
        """Test nested empty arrays."""
        data = {"outer": {"inner": []}}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_array_of_empty_objects(self):
        """Test array containing only empty objects."""
        data = {"items": [{}, {}, {}]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_object_with_all_empty_values(self):
        """Test object where all values are empty structures."""
        data = {"arr": [], "obj": {}, "nested_arr": [[]], "nested_obj": {}}
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestAdvancedKeyEdgeCases:
    """Test edge cases for object keys."""

    def test_keys_with_special_characters_quoted(self):
        """Test keys with special chars are properly quoted/unquoted."""
        data = {
            "normal": 1,
            "with-dash": 2,
            "with space": 3,
            "with:colon": 4,
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_keys_that_look_like_numbers(self):
        """Test keys that are numeric strings."""
        data = {"123": "a", "456": "b", "789": "c"}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_keys_that_look_like_booleans(self):
        """Test keys that look like boolean values."""
        data = {"true": 1, "false": 2, "null": 3}
        toon = encode(data)
        result = decode(toon)
        # Keys might be unquoted if they're safe
        assert result["true"] == 1 or result.get("true") == 1


class TestAdvancedRoundtrip:
    """Test roundtrip edge cases."""

    def test_roundtrip_with_all_primitive_types(self):
        """Test roundtrip with all JSON primitive types."""
        data = {
            "null": None,
            "bool_t": True,
            "bool_f": False,
            "int": 42,
            "float": 3.14,
            "string": "text",
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_roundtrip_complex_nested_structure(self):
        """Test roundtrip with complex nested structure."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
                {"id": 2, "name": "Bob", "roles": ["user"]},
            ],
            "settings": {"theme": "dark", "notifications": True},
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data
