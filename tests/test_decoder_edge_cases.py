"""Tests for ptoon.decoder edge cases and error handling.

Tests input validation, length marker validation, parsing errors,
malformed input handling, and complex nested structures.
"""

import pytest

from ptoon import decode, encode
from ptoon.decoder import Decoder


class TestInputValidation:
    """Test decoder input validation."""

    def test_rejects_non_string_input(self):
        """Test decoder raises TypeError for non-string input."""
        decoder = Decoder()
        with pytest.raises(TypeError, match="Expected string input"):
            decoder.decode(123)

        with pytest.raises(TypeError, match="Expected string input"):
            decoder.decode([1, 2, 3])

        with pytest.raises(TypeError, match="Expected string input"):
            decoder.decode({"key": "value"})

    def test_decodes_empty_string_as_empty_object(self):
        """Test empty string decodes to empty object."""
        assert decode("") == {}
        assert decode("   ") == {}
        assert decode("\n\n") == {}

    def test_decodes_whitespace_only_string(self):
        """Test whitespace-only string decodes to empty object."""
        assert decode("  \n  \n  ") == {}
        assert decode("\t\t\n\t\t") == {}


class TestArrayLengthMismatch:
    """Test array length marker validation."""

    def test_list_array_with_too_few_items(self):
        """Test list array with fewer items than declared raises error."""
        toon = """items[3]:
- item1
- item2"""
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)

    def test_list_array_with_too_many_items(self):
        """Test list array with more items than declared raises error."""
        toon = """items[2]:
  - item1
  - item2
  - item3"""
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)

    def test_nested_list_array_length_mismatch(self):
        """Test nested list array with length mismatch."""
        toon = """outer:
  inner[2]:
  - first"""
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)

    def test_list_array_interrupted_by_object_key(self):
        """Test list array interrupted by non-list content."""
        toon = """items[3]:
- item1
- item2
other_key: value"""
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)


class TestBlankLineHandling:
    """Test handling of blank lines in TOON."""

    def test_blank_lines_in_object(self):
        """Test blank lines between object properties are ignored."""
        toon = """a: 1

b: 2

c: 3"""
        result = decode(toon)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_blank_lines_in_list(self):
        """Test blank lines in list arrays are not allowed."""
        toon = """items[3]:
  - first

  - second"""
        # Blank lines inside arrays raise an error
        with pytest.raises(ValueError, match="Blank line encountered within array"):
            decode(toon)

    def test_multiple_consecutive_blank_lines(self):
        """Test multiple blank lines are handled."""
        toon = """a: 1


b: 2"""
        result = decode(toon)
        assert result == {"a": 1, "b": 2}


class TestInlineArrayParsing:
    """Test parsing of inline arrays within object values."""

    def test_inline_array_in_object_value(self):
        """Test object value containing inline array."""
        # Create a TOON string with an inline array
        toon = """data:
  values[3]: 1, 2, 3"""
        result = decode(toon)
        assert result == {"data": {"values": [1, 2, 3]}}

    def test_empty_inline_array_in_object(self):
        """Test empty inline array in object value."""
        toon = """data:
  items[0]:"""
        result = decode(toon)
        assert result == {"data": {"items": []}}


class TestNestedInlineObjects:
    """Test parsing of nested inline objects."""

    def test_nested_inline_object_on_same_line(self):
        """Test nested object defined inline with colon."""
        toon = """outer: inner: value"""
        result = decode(toon)
        assert result == {"outer": {"inner": "value"}}

    def test_deeply_nested_inline_objects(self):
        """Test multiple levels of inline nested objects."""
        toon = """a: b: c: 42"""
        result = decode(toon)
        assert result == {"a": {"b": {"c": 42}}}

    def test_inline_object_with_multiple_keys(self):
        """Test inline object followed by regular keys."""
        toon = """a: b: value
c: 2"""
        result = decode(toon)
        assert result == {"a": {"b": "value"}, "c": 2}


class TestMalformedInput:
    """Test handling of malformed TOON input."""

    def test_invalid_indentation_jump(self):
        """Test error on invalid indentation increase."""
        toon = """a: 1
      b: 2"""  # Too much indentation
        with pytest.raises(ValueError, match="unexpected content"):
            decode(toon)

    def test_list_item_at_wrong_depth(self):
        """Test list item at incorrect depth raises error."""
        toon = """a: 1
  - item"""  # List item in object context
        with pytest.raises(ValueError, match="unexpected.*-"):
            decode(toon)

    def test_tabular_row_without_header(self):
        """Test that pipes in values without tabular header are parsed as string."""
        # Without a tabular header, this is just a key-value parse
        toon = """key: | 1 | 2 | 3 |"""
        result = decode(toon)
        assert result == {"key": "| 1 | 2 | 3 |"}

    def test_duplicate_keys_in_object(self):
        """Test that duplicate keys result in last value winning."""
        toon = """key: first
key: second"""
        result = decode(toon)
        # Last value wins
        assert result == {"key": "second"}


class TestComplexNesting:
    """Test complex nested structure edge cases."""

    def test_mixed_array_types_nested(self):
        """Test mix of list and tabular arrays in same structure."""
        data = {
            "list_items": ["a", "b", "c"],
            "table_data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_deeply_nested_mixed_structures(self):
        """Test deeply nested mix of objects, lists, and primitives."""
        data = {
            "level1": {
                "level2": {
                    "items": [
                        {"name": "first", "values": [1, 2, 3]},
                        {"name": "second", "values": [4, 5, 6]},
                    ]
                }
            }
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_arrays_of_empty_objects(self):
        """Test array containing empty objects."""
        data = {"items": [{}, {}, {}]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_objects_with_all_null_values(self):
        """Test object with all null values."""
        data = {"a": None, "b": None, "c": None}
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestTabularArrayEdgeCases:
    """Test edge cases in tabular array parsing."""

    def test_tabular_array_with_single_column(self):
        """Test tabular array with only one field."""
        data = {"users": [{"id": 1}, {"id": 2}, {"id": 3}]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_tabular_array_with_length_marker(self):
        """Test tabular array with length marker validation."""
        toon = """users[#2]{id,name}:
  1,Alice
  2,Bob"""
        result = decode(toon)
        assert result == {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

    def test_tabular_array_too_many_rows(self):
        """Test tabular array with too many rows raises error."""
        toon = """users[#2]{id,name}:
  1,Alice
  2,Bob
  3,Charlie"""
        with pytest.raises(ValueError, match="unexpected content"):
            decode(toon)


class TestPrimitiveValueEdgeCases:
    """Test edge cases in primitive value parsing."""

    def test_string_value_with_colons(self):
        """Test string values containing colons are handled."""
        toon = '''url: "http://example.com:8080"'''
        result = decode(toon)
        assert result == {"url": "http://example.com:8080"}

    def test_string_value_with_brackets(self):
        """Test string values containing brackets."""
        toon = '''text: "array[0]"'''
        result = decode(toon)
        assert result == {"text": "array[0]"}

    def test_numeric_string_keys(self):
        """Test keys that are numeric strings."""
        toon = """"123": value1
"456": value2"""
        result = decode(toon)
        assert result == {"123": "value1", "456": "value2"}

    def test_empty_string_key(self):
        """Test empty string as key."""
        toon = """"": empty_key_value
normal: value"""
        result = decode(toon)
        assert result == {"": "empty_key_value", "normal": "value"}


class TestRoundtripEdgeCases:
    """Test roundtrip encode/decode for edge cases."""

    def test_roundtrip_special_characters_in_strings(self):
        """Test roundtrip with special characters."""
        data = {"text": "line1\nline2\ttab", "quote": 'she said "hello"'}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_roundtrip_mixed_numeric_types(self):
        """Test roundtrip with various numeric types."""
        data = {"int": 42, "float": 3.14, "negative": -100, "zero": 0}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_roundtrip_deeply_nested_arrays(self):
        """Test roundtrip with arrays of arrays."""
        data = {"nested": [[1, 2, 3], [4, 5, 6]]}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_roundtrip_empty_structures(self):
        """Test roundtrip with various empty structures."""
        data = {"empty_obj": {}, "empty_arr": [], "nested": {"also_empty": {}}}
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestDelimiterHandling:
    """Test handling of different delimiters."""

    def test_decode_tab_delimited_array(self):
        """Test decoding tab-delimited inline array."""
        toon = "items[3\t]: 1\t2\t3"
        result = decode(toon)
        assert result == {"items": [1, 2, 3]}

    def test_decode_pipe_delimited_array(self):
        """Test decoding pipe-delimited inline array."""
        toon = "items[3|]: 1| 2| 3"
        result = decode(toon)
        assert result == {"items": [1, 2, 3]}

    def test_decode_tabular_with_tab_delimiter(self):
        """Test decoding tabular array with tab delimiter."""
        toon = "data[2\t]{a\tb}:\n  1\t2\n  3\t4"
        result = decode(toon)
        assert result == {"data": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}


class TestContextUnwinding:
    """Test context stack unwinding edge cases."""

    def test_multiple_context_pops_on_dedent(self):
        """Test multiple contexts popped on large dedent."""
        toon = """a:
  b:
    c:
      d: 1
e: 2"""
        result = decode(toon)
        assert result == {"a": {"b": {"c": {"d": 1}}}, "e": 2}

    def test_context_unwinding_with_arrays(self):
        """Test context unwinding with mixed arrays and objects."""
        data = {"outer": {"items": [1, 2, 3]}, "next": "value"}
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_array_completion_on_dedent(self):
        """Test array automatically completes when dedenting."""
        toon = """items[2]:
  - first
  - second
next_key: value"""
        result = decode(toon)
        assert result == {"items": ["first", "second"], "next_key": "value"}
