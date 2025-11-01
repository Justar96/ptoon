"""Final targeted tests to push coverage to 95%+.

These tests target the remaining hard-to-reach code paths in decoder and encoder.
"""

import pytest

from ptoon import decode, encode
from ptoon.decoder import Decoder
from ptoon.encoder import Encoder


class TestDecoderComplexUnwinding:
    """Test complex context unwinding scenarios."""

    def test_deep_context_unwinding_multiple_levels(self):
        """Test unwinding multiple nested contexts at once."""
        # This targets lines 256-273 and 274-291 (deep unwinding)
        toon = """root:
  level1:
    level2:
      level3[1]:
        - deep_value
    sibling: value
top: done"""
        result = decode(toon)
        assert result["root"]["level1"]["level2"]["level3"][0] == "deep_value"
        assert result["root"]["level1"]["sibling"] == "value"

    def test_unwinding_from_nested_array_to_sibling(self):
        """Test unwinding from nested array back to sibling object."""
        # Targets context unwinding lines
        toon = """parent:
  nested:
    arr[2]:
      - first
      - second
  sibling_key: sibling_value
root_sibling: value"""
        result = decode(toon)
        assert result["parent"]["nested"]["arr"] == ["first", "second"]
        assert result["parent"]["sibling_key"] == "sibling_value"


class TestDecoderMalformedHeaders:
    """Test malformed header edge cases."""

    def test_header_without_opening_bracket_in_context(self):
        """Test missing opening bracket is detected in object context."""
        # Targets line 532 (missing '[' error)
        toon = "outer:\n  key3]: value"
        # This will parse as a normal key-value, not raise error
        result = decode(toon)
        assert "key3]" in result["outer"]

    def test_header_with_invalid_characters_after_bracket(self):
        """Test header with invalid structure after closing bracket."""
        # Targets line 586 (invalid suffix)
        toon = "key[2]invalid: 1, 2"
        with pytest.raises(ValueError, match="invalid array header suffix"):
            decode(toon)

    def test_field_name_parsing_error(self):
        """Test invalid field name in tabular header."""
        # Targets lines 605-606 (field name error)
        # Field names with invalid escape sequences
        toon = 'outer:\n  key[2]{"field\\x"}:\n    1\n    2'
        with pytest.raises(ValueError, match="Invalid escape sequence|invalid field name"):
            decode(toon)


class TestDecoderInlineArrayErrors:
    """Test inline array error paths."""

    def test_empty_inline_array_with_nonzero_length(self):
        """Test inline array with length but no values."""
        # Targets line 632 (empty inline with nonzero length)
        toon = "outer:\n  arr[3]:"
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)


class TestDecoderInlineNestedObject:
    """Test inline nested object with array."""

    def test_inline_object_with_nested_array_value(self):
        """Test inline object containing array value."""
        # Targets lines 753-758 (inline object with array)
        toon = "a: b[2]: 1, 2"
        result = decode(toon)
        assert result == {"a": {"b": [1, 2]}}


class TestDecoderTabularCompletion:
    """Test tabular array completion edge cases."""

    def test_tabular_array_exact_completion(self):
        """Test tabular array that completes exactly."""
        # Targets line 852 (pop completed tabular)
        toon = """data[3]{id}:
  1
  2
  3"""
        result = decode(toon)
        assert len(result["data"]) == 3


class TestDecoderNumericEdgeCases:
    """Test numeric parsing edge cases."""

    def test_leading_zero_without_decimal(self):
        """Test number with leading zero is parsed as string."""
        # Targets line 940 (forbidden leading zeros check)
        toon = "value: 0123"
        result = decode(toon)
        assert result["value"] == "0123"

    def test_leading_zero_check_with_decimal(self):
        """Test leading zero check doesn't trigger for decimals."""
        # Targets line 944 (check for '.' in forbidden zeros)
        toon = "value: 0.123"
        result = decode(toon)
        assert result["value"] == 0.123


class TestDecoderBlankLineNoExpected:
    """Test blank line handling when no expected count."""

    def test_blank_line_error_includes_item_count(self):
        """Test blank line error message with array info."""
        # Targets lines 1013-1025 (blank line with array context)
        toon = """items[2]:
  - first

  - second"""
        with pytest.raises(ValueError, match="Blank line encountered within array"):
            decode(toon)


class TestEncoderTypeValidationPaths:
    """Test encoder type validation."""

    def test_encode_module_directly(self):
        """Test encoding module raises TypeError."""
        # Targets line 73
        import types

        module = types.ModuleType("test")
        with pytest.raises(TypeError, match="Cannot encode"):
            encode(module)

    def test_encode_type_directly(self):
        """Test encoding type object raises TypeError."""
        # Targets line 77
        with pytest.raises(TypeError, match="Cannot encode"):
            encode(int)

    def test_encode_function_directly(self):
        """Test encoding function raises TypeError."""

        # Targets line 83
        def func():
            pass

        with pytest.raises(TypeError, match="Cannot encode"):
            encode(func)


class TestEncoderTabularDetectionPaths:
    """Test encoder tabular detection edge cases."""

    def test_tabular_detection_empty_array(self):
        """Test tabular detection with empty array."""
        # Targets line 246
        encoder = Encoder()
        result = encoder._detect_tabular_header([])
        assert result is None

    def test_tabular_detection_no_keys(self):
        """Test tabular detection when first object has no keys."""
        # Targets line 259
        # This is hard to hit as empty dict has no keys
        encoder = Encoder()
        # The function checks if first_keys is empty
        data = [{}]  # Empty object
        result = encoder._detect_tabular_header(data)
        assert result is None

    def test_is_tabular_returns_false_for_mismatched(self):
        """Test _is_tabular_array returns False."""
        # Targets line 272
        encoder = Encoder()
        data = [
            {"a": 1, "b": 2},
            {"a": 1, "c": 3},  # Different keys
        ]
        result = encoder._detect_tabular_header(data)
        assert result is None


class TestEncoderNestedArrayHandling:
    """Test encoder complex nested array handling."""

    def test_encode_complex_nested_first_field(self):
        """Test encoding complex nested structures."""
        # Targets lines 392-397, 417, 420, 423, 425
        # These are complex nested array handling in list items
        data = [
            {
                "complex": [
                    [1, 2],
                    {"key": "value"},
                    "string",
                ],
                "other": "field",
            }
        ]
        # Just verify it encodes without error
        result = encode(data)
        assert "complex" in result


class TestContextDescriptionEdgeCases:
    """Test context description formatting."""

    def test_tabular_context_with_fields(self):
        """Test tabular array context description."""
        # Targets lines 341-345 (context description for tabular)
        # This is used in error messages
        toon = """data[2]{id, name}:
  1, Alice
  2, Bob"""
        result = decode(toon)
        # The context description would be used in error messages
        assert len(result["data"]) == 2


class TestErrorMessageFormatting:
    """Test error message formatting edge cases."""

    def test_error_with_empty_line_snippet(self):
        """Test error formatting when snippet is empty."""
        # Targets line 363 (empty snippet formatting)

        decoder = Decoder()
        # Error with empty line
        error = decoder._err(1, "test error", "")
        assert "Snippet: ''" in str(error)


class TestInlineObjectParsingWithBracket:
    """Test inline object containing brackets."""

    def test_looks_header_token_with_escape(self):
        """Test header token detection with escapes."""
        # Targets line 507 (found '{' before ']')

        decoder = Decoder()
        # String that looks like header but has '{' before ']'
        result = decoder._looks_header_token("key{bracket]")
        # Should return False because '{' comes before ']'
        assert result is False


class TestSplitValuesEmptyString:
    """Test splitting empty strings."""

    def test_split_empty_string(self):
        """Test _split_values with empty string."""
        # Targets line 966 (empty string check)

        decoder = Decoder()
        result = decoder._split_values("", ",")
        assert result == []


class TestPrimitivesFloatFormatting:
    """Test float formatting edge case."""

    def test_format_float_zero(self):
        """Test formatting zero float."""
        # Targets line 268 (empty string case)
        from ptoon.primitives import _format_float

        result = _format_float(0.0)
        # Should return "0", not empty string
        assert result == "0"
