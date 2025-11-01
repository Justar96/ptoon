"""Tests for pytoon API validation and error handling.

Tests input validation, option validation, and type checking
in the public encode() and decode() functions.
"""

import types

import pytest

import ptoon
from ptoon import decode, encode


class TestEncodeTypeValidation:
    """Test encode() input type validation."""

    def test_rejects_module_type(self):
        """Test encode() raises TypeError for module objects."""
        with pytest.raises(TypeError, match="Cannot encode module: TOON supports dicts, lists, and primitives"):
            encode(types)

    def test_rejects_class_type(self):
        """Test encode() raises TypeError for class/type objects."""

        class MyClass:
            pass

        with pytest.raises(TypeError, match="Cannot encode type: TOON supports dicts, lists, and primitives"):
            encode(MyClass)

    def test_rejects_function_type(self):
        """Test encode() raises TypeError for function objects."""

        def my_function():
            pass

        with pytest.raises(TypeError, match="Cannot encode function: TOON supports dicts, lists, and primitives"):
            encode(my_function)

    def test_rejects_lambda_function(self):
        """Test encode() raises TypeError for lambda functions."""
        with pytest.raises(TypeError, match="Cannot encode function: TOON supports dicts, lists, and primitives"):
            encode(lambda x: x)

    def test_rejects_method_type(self):
        """Test encode() raises TypeError for method objects."""

        class MyClass:
            def my_method(self):
                pass

        obj = MyClass()
        with pytest.raises(TypeError, match="Cannot encode method: TOON supports dicts, lists, and primitives"):
            encode(obj.my_method)

    def test_rejects_builtin_function(self):
        """Test encode() raises TypeError for builtin functions."""
        with pytest.raises(
            TypeError, match="Cannot encode builtin_function_or_method: TOON supports dicts, lists, and primitives"
        ):
            encode(len)


class TestEncodeOptionsValidation:
    """Test encode() options validation."""

    def test_rejects_non_dict_options(self):
        """Test encode() raises TypeError for non-dict options."""
        with pytest.raises(TypeError, match="options must be a dict, got str"):
            encode({"key": "value"}, options="invalid")

        with pytest.raises(TypeError, match="options must be a dict, got list"):
            encode({"key": "value"}, options=["invalid"])

        with pytest.raises(TypeError, match="options must be a dict, got int"):
            encode({"key": "value"}, options=123)

    def test_rejects_invalid_option_keys(self):
        """Test encode() raises ValueError for unsupported option keys."""
        with pytest.raises(
            ValueError,
            match="options contains unsupported keys; allowed: \\['delimiter', 'indent', 'length_marker'\\]; got: \\['invalid'\\]",
        ):
            encode({"key": "value"}, options={"invalid": True})

        with pytest.raises(
            ValueError,
            match="options contains unsupported keys.*got: \\['bad', 'wrong'\\]",
        ):
            encode({"key": "value"}, options={"bad": 1, "wrong": 2})

    def test_rejects_invalid_delimiter_value(self):
        """Test encode() raises ValueError for invalid delimiter."""
        with pytest.raises(
            ValueError,
            match="delimiter must be one of ',', '\\|' or '\\\\t'; got: ';'",
        ):
            encode({"key": "value"}, options={"delimiter": ";"})

        with pytest.raises(
            ValueError,
            match="delimiter must be one of ',', '\\|' or '\\\\t'; got: ' '",
        ):
            encode({"key": "value"}, options={"delimiter": " "})

    def test_accepts_valid_delimiters(self):
        """Test encode() accepts valid delimiter values."""
        # Should not raise
        encode([1, 2, 3], options={"delimiter": ","})
        encode([1, 2, 3], options={"delimiter": "|"})
        encode([1, 2, 3], options={"delimiter": "\t"})

    def test_rejects_negative_indent(self):
        """Test encode() raises ValueError for negative indent."""
        with pytest.raises(ValueError, match="indent must be a non-negative int; got: -1"):
            encode({"key": "value"}, options={"indent": -1})

    def test_rejects_non_int_indent(self):
        """Test encode() raises ValueError for non-integer indent."""
        with pytest.raises(ValueError, match="indent must be a non-negative int; got: 'two'"):
            encode({"key": "value"}, options={"indent": "two"})

        with pytest.raises(ValueError, match="indent must be a non-negative int; got: 2.5"):
            encode({"key": "value"}, options={"indent": 2.5})

    def test_rejects_bool_indent(self):
        """Test encode() raises ValueError for boolean indent."""
        with pytest.raises(ValueError, match="indent must be a non-negative int; got: True"):
            encode({"key": "value"}, options={"indent": True})

        with pytest.raises(ValueError, match="indent must be a non-negative int; got: False"):
            encode({"key": "value"}, options={"indent": False})

    def test_accepts_zero_indent(self):
        """Test encode() accepts indent=0."""
        # Should not raise
        result = encode({"key": "value"}, options={"indent": 0})
        assert "key: value" in result

    def test_accepts_positive_indent(self):
        """Test encode() accepts positive indent values."""
        # Should not raise
        encode({"key": "value"}, options={"indent": 2})
        encode({"key": "value"}, options={"indent": 4})
        encode({"key": "value"}, options={"indent": 8})

    def test_rejects_non_bool_length_marker(self):
        """Test encode() raises ValueError for non-boolean length_marker."""
        with pytest.raises(ValueError, match="length_marker must be a bool; got: 'yes'"):
            encode([1, 2, 3], options={"length_marker": "yes"})

        with pytest.raises(ValueError, match="length_marker must be a bool; got: 1"):
            encode([1, 2, 3], options={"length_marker": 1})

    def test_accepts_bool_length_marker(self):
        """Test encode() accepts boolean length_marker."""
        # Should not raise
        result_true = encode([1, 2, 3], options={"length_marker": True})
        result_false = encode([1, 2, 3], options={"length_marker": False})

        # With length_marker=True, should have #3
        assert "#3" in result_true
        # With length_marker=False, should not have #
        assert "#" not in result_false


class TestEncodeDefaultCaching:
    """Test encoder instance caching for default options."""

    def test_uses_cached_encoder_for_default_options(self):
        """Test encode() reuses default encoder instance."""
        # These should use the same cached encoder
        result1 = encode({"a": 1})
        result2 = encode({"b": 2})

        # Both should produce valid output
        assert "a: 1" in result1
        assert "b: 2" in result2

    def test_uses_cached_encoder_when_options_is_none(self):
        """Test encode() with options=None uses cached encoder."""
        result = encode({"key": "value"}, options=None)
        assert "key: value" in result

    def test_creates_new_encoder_for_custom_options(self):
        """Test encode() creates new encoder for non-default options."""
        # Custom indent should not use cached encoder
        result1 = encode({"a": 1}, options={"indent": 4})
        result2 = encode({"b": 2}, options={"delimiter": "|"})

        assert "a: 1" in result1
        assert "b: 2" in result2


class TestDecodeTypeValidation:
    """Test decode() input validation."""

    def test_rejects_non_string_input(self):
        """Test decode() raises TypeError for non-string input."""
        with pytest.raises(
            TypeError,
            match="decode\\(\\) expects a string, got dict.*Use encode\\(\\) to convert",
        ):
            decode({"key": "value"})

        with pytest.raises(
            TypeError,
            match="decode\\(\\) expects a string, got list",
        ):
            decode([1, 2, 3])

        with pytest.raises(
            TypeError,
            match="decode\\(\\) expects a string, got int",
        ):
            decode(123)

    def test_rejects_non_dict_options(self):
        """Test decode() raises TypeError for non-dict options."""
        with pytest.raises(TypeError, match="options must be a dict, got str"):
            decode("key: value", options="invalid")

        with pytest.raises(TypeError, match="options must be a dict, got list"):
            decode("key: value", options=["invalid"])

    def test_accepts_none_options(self):
        """Test decode() accepts options=None."""
        result = decode("key: value", options=None)
        assert result == {"key": "value"}

    def test_accepts_dict_options(self):
        """Test decode() accepts dict options (reserved for future use)."""
        # Currently options are reserved but should not error
        result = decode("key: value", options={})
        assert result == {"key": "value"}


class TestDecodeDefaultCaching:
    """Test decoder instance caching for default options."""

    def test_uses_cached_decoder_for_default_options(self):
        """Test decode() reuses default decoder instance."""
        # These should use the same cached decoder
        result1 = decode("a: 1")
        result2 = decode("b: 2")

        assert result1 == {"a": 1}
        assert result2 == {"b": 2}

    def test_uses_cached_decoder_when_options_is_none(self):
        """Test decode() with options=None uses cached decoder."""
        result = decode("key: value", options=None)
        assert result == {"key": "value"}

    def test_creates_new_decoder_for_custom_options(self):
        """Test decode() creates new decoder when options provided."""
        # Even though options are reserved, providing them creates new decoder
        result = decode("key: value", options={})
        assert result == {"key": "value"}


class TestPublicAPI:
    """Test public API exports."""

    def test_exports_encode_function(self):
        """Test ptoon exports encode function."""
        assert hasattr(ptoon, "encode")
        assert callable(ptoon.encode)

    def test_exports_decode_function(self):
        """Test ptoon exports decode function."""
        assert hasattr(ptoon, "decode")
        assert callable(ptoon.decode)

    def test_exports_utility_functions(self):
        """Test ptoon exports utility functions."""
        assert hasattr(ptoon, "count_tokens")
        assert hasattr(ptoon, "estimate_savings")
        assert hasattr(ptoon, "compare_formats")

    def test_exports_constants(self):
        """Test ptoon exports constants."""
        assert hasattr(ptoon, "DEFAULT_DELIMITER")
        assert hasattr(ptoon, "DELIMITERS")

    def test_exports_type_definitions(self):
        """Test ptoon exports type definitions."""
        assert hasattr(ptoon, "JsonPrimitive")
        assert hasattr(ptoon, "JsonArray")
        assert hasattr(ptoon, "JsonObject")
        assert hasattr(ptoon, "JsonValue")
        assert hasattr(ptoon, "Delimiter")
        assert hasattr(ptoon, "EncodeOptions")
