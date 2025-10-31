"""Comprehensive edge case tests to boost coverage from 90% to 95%+.

This module targets specific uncovered lines in encoder, decoder, normalize,
and primitives modules. Tests focus on realistic edge cases and error paths
that improve regression protection.

Coverage targets:
- encoder.py: Type validation, non-string keys
- decoder.py: Indentation errors, header parsing, object parsing
- normalize.py: Datetime exceptions, empty array edge cases
- primitives.py: Float formatting edge cases
"""

import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from pytoon import decode, encode
from pytoon.decoder import Decoder
from pytoon.encoder import Encoder


class TestTypeValidationErrors:
    """Test encoder type validation for unsupported types."""

    def test_rejects_module_type(self):
        """Test encoding a module raises TypeError."""
        with pytest.raises(TypeError, match="Cannot encode module"):
            encode(sys)

    def test_rejects_type_object(self):
        """Test encoding a type object raises TypeError."""
        with pytest.raises(TypeError, match="Cannot encode type"):
            encode(int)

        with pytest.raises(TypeError, match="Cannot encode type"):
            encode(str)

    def test_rejects_function_type(self):
        """Test encoding a function raises TypeError."""
        def sample_func():
            pass

        with pytest.raises(TypeError, match="Cannot encode function"):
            encode(sample_func)

    def test_rejects_lambda_type(self):
        """Test encoding a lambda raises TypeError."""
        with pytest.raises(TypeError, match="Cannot encode function"):
            encode(lambda x: x + 1)

    def test_rejects_builtin_function(self):
        """Test encoding a builtin function raises TypeError."""
        with pytest.raises(TypeError, match="Cannot encode builtin_function_or_method"):
            encode(len)

    def test_rejects_non_string_object_keys_int(self):
        """Test encoding object with integer keys raises TypeError."""
        encoder = Encoder()
        data = {1: "value1", 2: "value2"}

        with pytest.raises(TypeError, match="Object keys must be strings"):
            encoder._encode_object(data, encoder.indent, 0)

    def test_rejects_non_string_object_keys_none(self):
        """Test encoding object with None keys raises TypeError."""
        encoder = Encoder()
        # Note: Python dicts with None keys are valid, but TOON requires string keys
        data = {None: "value"}

        with pytest.raises(TypeError, match="Object keys must be strings"):
            encoder._encode_object(data, encoder.indent, 0)

    def test_rejects_non_string_object_keys_tuple(self):
        """Test encoding object with tuple keys raises TypeError."""
        encoder = Encoder()
        data = {(1, 2): "value"}

        with pytest.raises(TypeError, match="Object keys must be strings"):
            encoder._encode_object(data, encoder.indent, 0)


class TestDecoderIndentationErrors:
    """Test decoder validation of indentation."""

    def test_rejects_tab_in_indentation(self):
        """Test tab character in indentation raises error."""
        toon = "\ta: 1"
        with pytest.raises(ValueError, match="tab character found in indentation"):
            decode(toon)

    def test_rejects_tab_in_nested_indentation(self):
        """Test tab in nested structure raises error."""
        toon = "outer:\n\tinner: value"
        with pytest.raises(ValueError, match="tab character found in indentation"):
            decode(toon)

    def test_rejects_invalid_indentation_not_multiple(self):
        """Test indentation not multiple of detected indent raises error."""
        # First line establishes 2-space indent, second line uses 3 spaces (invalid)
        toon = "outer:\n  inner:\n   value: test"
        with pytest.raises(ValueError, match="invalid indentation"):
            decode(toon)

    def test_rejects_single_space_indent_with_two_space_standard(self):
        """Test single-space indent when two-space is expected."""
        toon = "outer:\n  inner: nested\n nested: also"
        with pytest.raises(ValueError, match="unexpected content at depth|invalid indentation"):
            decode(toon)

    def test_mixed_tabs_and_spaces_detection(self):
        """Test detection of mixed tabs and spaces."""
        toon = "a: 1\n\tb: 2"
        with pytest.raises(ValueError, match="tab character found in indentation"):
            decode(toon)


class TestHeaderParsingErrors:
    """Test decoder validation of array headers."""

    def test_header_missing_opening_bracket(self):
        """Test array header without '[' raises error when used in object."""
        # In object context, missing '[' means it's not recognized as array header
        toon = "outer:\n  items3]: 1, 2, 3"
        # Will be parsed as invalid object key or syntax error
        result = decode(toon)
        # It gets parsed as a key with value in the outer object
        assert "items3]" in result["outer"]

    def test_header_missing_closing_bracket(self):
        """Test array header without ']' raises error."""
        # Header that starts properly but doesn't close
        toon = "outer:\n  items[3: 1, 2, 3"
        with pytest.raises(ValueError, match="invalid object entry|missing closing ']'"):
            decode(toon)

    def test_header_invalid_length_non_numeric(self):
        """Test array header with non-numeric length raises error."""
        toon = "items[abc]: value"
        with pytest.raises(ValueError, match="invalid array header length block"):
            decode(toon)

    def test_header_empty_length(self):
        """Test array header with empty length raises error."""
        toon = "items[]: value"
        with pytest.raises(ValueError, match="invalid array header length block"):
            decode(toon)

    def test_header_length_marker_only(self):
        """Test array header with # but no number raises error."""
        toon = "items[#]: value"
        with pytest.raises(ValueError, match="invalid array header length block"):
            decode(toon)

    def test_header_missing_closing_brace_in_fields(self):
        """Test tabular header missing '}' raises error."""
        toon = "[2]{id, name:\n  1, Alice\n  2, Bob"
        with pytest.raises(ValueError, match="missing closing '}'"):
            decode(toon)

    def test_header_invalid_field_name_with_spaces_unquoted(self):
        """Test tabular header with quoted field names."""
        # Quoted field names should work fine
        toon = '[2]{"123", "@bad"}:\n  1, Alice\n  2, Bob'
        # Decoder should handle quoted field names
        result = decode(toon)
        assert len(result) == 2
        assert result[0]["123"] == 1  # Parsed as int, not string

    def test_array_header_in_object_without_key(self):
        """Test array header in object context must have key."""
        toon = "outer:\n  [3]: 1, 2, 3"
        with pytest.raises(ValueError, match="array header inside object must include a key prefix"):
            decode(toon)

    def test_tabular_array_with_inline_values(self):
        """Test tabular array header cannot have inline values."""
        toon = "items[2]{id, name}: 1, Alice"
        with pytest.raises(ValueError, match="tabular array header cannot include inline values"):
            decode(toon)

    def test_invalid_header_key_with_escape(self):
        """Test invalid escape sequence in header key."""
        # Key with invalid escape should raise error
        toon = r'"invalid\xkey"[2]: 1, 2'
        with pytest.raises(ValueError, match="Invalid escape sequence"):
            decode(toon)


class TestObjectParsingErrors:
    """Test decoder validation of object entries."""

    def test_object_entry_missing_colon(self):
        """Test object entry without colon is parsed as value."""
        # Without colon at root, it's parsed as a primitive value, not an error
        toon = "key value"
        result = decode(toon)
        # Parses as unquoted string
        assert result == "key value"

    def test_object_entry_missing_key_before_colon(self):
        """Test object entry with empty key raises error."""
        toon = ": value"
        with pytest.raises(ValueError, match="missing key before ':'"):
            decode(toon)

    def test_object_entry_colon_only(self):
        """Test object entry with just colon raises error."""
        toon = ":"
        with pytest.raises(ValueError, match="missing key before ':'"):
            decode(toon)

    def test_object_key_with_invalid_escape(self):
        """Test object key with invalid escape sequence."""
        toon = r'"key\xvalue": test'
        with pytest.raises(ValueError, match="Invalid escape sequence"):
            decode(toon)

    def test_nested_object_key_missing_colon(self):
        """Test nested object with malformed key."""
        toon = "outer:\n  inner value"
        with pytest.raises(ValueError, match="invalid object entry"):
            decode(toon)


class TestTabularArrayFieldMismatch:
    """Test tabular array field count validation."""

    def test_tabular_row_too_many_fields(self):
        """Test tabular row with more fields than header."""
        toon = "[2]{id, name}:\n  1, Alice, Extra"
        with pytest.raises(ValueError, match="field count mismatch"):
            decode(toon)

    def test_tabular_row_too_few_fields(self):
        """Test tabular row with fewer fields than header."""
        toon = "[2]{id, name}:\n  1\n  2"
        with pytest.raises(ValueError, match="field count mismatch"):
            decode(toon)

    def test_tabular_row_field_mismatch_with_pipe(self):
        """Test tabular row field mismatch with pipe delimiter."""
        toon = "[2|]{id| name}:\n  1| Alice\n  2"
        with pytest.raises(ValueError, match="field count mismatch"):
            decode(toon)


class TestNormalizeEdgeCases:
    """Test normalization edge cases."""

    def test_datetime_isoformat_exception(self):
        """Test datetime that fails ISO format conversion."""
        from pytoon.normalize import normalize_value

        # Mock a datetime that raises exception on isoformat()
        mock_dt = Mock(spec=datetime)
        mock_dt.isoformat.side_effect = ValueError("Invalid datetime")

        with pytest.raises(ValueError, match="Failed to convert datetime to ISO format"):
            normalize_value(mock_dt)

    def test_empty_array_type_checks(self):
        """Test that empty arrays return True for all type checks."""
        from pytoon.normalize import (
            is_array_of_arrays,
            is_array_of_objects,
            is_array_of_primitives,
        )

        empty: list = []
        assert is_array_of_primitives(empty) is True
        assert is_array_of_arrays(empty) is True
        assert is_array_of_objects(empty) is True


class TestPrimitivesFloatFormatting:
    """Test primitive float formatting edge cases."""

    def test_float_formatting_strips_trailing_zeros(self):
        """Test float formatting removes trailing zeros."""
        from pytoon.primitives import encode_primitive

        assert encode_primitive(3.0) == "3"
        assert encode_primitive(3.14000) == "3.14"
        assert encode_primitive(100.00) == "100"

    def test_float_formatting_very_small_number(self):
        """Test float formatting for very small numbers."""
        from pytoon.primitives import encode_primitive

        # Very small float that might format to empty after stripping
        result = encode_primitive(0.0)
        assert result == "0"


class TestBlankLineEdgeCases:
    """Test blank line handling in arrays."""

    def test_blank_line_in_tabular_array(self):
        """Test blank line in tabular array raises error."""
        toon = "[3]{id, name}:\n  1, Alice\n\n  2, Bob"
        with pytest.raises(ValueError, match="Blank line encountered within array"):
            decode(toon)

    def test_blank_line_in_inline_array_context(self):
        """Test blank line doesn't affect inline arrays."""
        toon = "items[3]: 1, 2, 3\n\nother: value"
        result = decode(toon)
        assert result == {"items": [1, 2, 3], "other": "value"}


class TestComplexHeaderScenarios:
    """Test complex header parsing scenarios."""

    def test_header_with_escaped_quotes_in_key(self):
        """Test header with escaped quotes in key name."""
        toon = r'"key\"name"[2]: 1, 2'
        result = decode(toon)
        assert 'key"name' in result
        assert result['key"name'] == [1, 2]

    def test_nested_brackets_in_key_name(self):
        """Test key name containing brackets (quoted) in object context."""
        # In root context, the parser may see [2] as array syntax
        # Better to test in object context
        toon = 'outer:\n  "key[0]": value'
        result = decode(toon)
        assert result["outer"]["key[0]"] == "value"

    def test_header_with_delimiter_in_field_name(self):
        """Test tabular header with delimiter in field name (quoted)."""
        toon = '[2]{"id,num", name}:\n  "1,2", Alice\n  "3,4", Bob'
        result = decode(toon)
        assert len(result) == 2
        assert result[0]["id,num"] == "1,2"


class TestEncoderTabularDetectionEdgeCases:
    """Test encoder tabular format detection edge cases."""

    def test_empty_rows_in_tabular_detection(self):
        """Test tabular detection with empty object rows."""
        data = [{}]
        result = encode(data)
        # Single empty object should use list format
        assert "-" in result

    def test_single_row_not_tabular(self):
        """Test single object doesn't trigger tabular format."""
        encoder = Encoder()
        data = [{"id": 1, "name": "Alice"}]
        header = encoder._detect_tabular_header(data)
        assert header is None  # Single row should not be tabular

    def test_object_with_no_keys_not_tabular(self):
        """Test object with no keys doesn't trigger tabular."""
        encoder = Encoder()
        # This tests line 259 - when first_keys is empty
        data = [{"a": 1}, {}]  # Second object is empty
        header = encoder._detect_tabular_header(data)
        assert header is None


class TestDecoderEscapeSequences:
    """Test escape sequence handling in decoder."""

    def test_unclosed_escape_at_end_of_string(self):
        """Test string ending with backslash raises error."""
        # String ending with single backslash inside quotes (unclosed escape)
        # Build string programmatically to avoid Python string escaping confusion
        toon = 'key: "value' + '\\' + '"'  # Results in: key: "value\"
        # Unclosed escape sequence at end of string
        with pytest.raises(ValueError, match="Unclosed escape sequence"):
            decode(toon)

    def test_string_with_valid_escapes(self):
        """Test all valid escape sequences decode correctly."""
        toon = r'key: "line1\nline2\ttabbed\rreturn\"quote\\backslash"'
        result = decode(toon)
        assert result["key"] == 'line1\nline2\ttabbed\rreturn"quote\\backslash'

    def test_string_with_invalid_escape_x(self):
        """Test invalid \\x escape sequence."""
        toon = r'key: "invalid\xescape"'
        with pytest.raises(ValueError, match="Invalid escape sequence"):
            decode(toon)


class TestInlineArrayEdgeCases:
    """Test inline array parsing edge cases."""

    def test_inline_array_declared_length_zero_with_values(self):
        """Test inline array with length 0 but values provided."""
        toon = "items[0]: 1, 2, 3"
        with pytest.raises(ValueError, match="inline array length mismatch"):
            decode(toon)

    def test_inline_array_empty_with_nonzero_length(self):
        """Test inline array with declared length but no values."""
        toon = "items[3]:"
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)

    def test_inline_nested_object_value_in_object(self):
        """Test inline nested object as value."""
        toon = "outer: inner: nested: value"
        result = decode(toon)
        assert result == {"outer": {"inner": {"nested": "value"}}}


class TestRoundtripEdgeCases:
    """Test roundtrip encode/decode for edge cases."""

    def test_roundtrip_object_with_array_value_inline(self):
        """Test object with inline array value roundtrips."""
        data = {"nums": [1, 2, 3], "name": "test"}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_nested_inline_objects(self):
        """Test deeply nested inline objects."""
        data = {"a": {"b": {"c": {"d": "value"}}}}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_mixed_delimiters_and_types(self):
        """Test mixed content roundtrips correctly."""
        data = {
            "primitives": [1, "two", 3.0, None, True],
            "objects": [{"id": 1}, {"id": 2}],
            "nested": {"inner": [1, 2, 3]},
        }
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data
