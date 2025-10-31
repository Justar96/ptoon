"""Tests for ptoon.normalize edge cases and error handling.

Tests special cases in value normalization including negative zero,
datetime conversion, heterogeneous sets, and unsupported types.
"""

import datetime
import logging
import math
from collections import OrderedDict, UserDict
from collections.abc import Mapping

import pytest

from ptoon import encode
from ptoon.normalize import normalize_value


class TestNegativeZero:
    """Test handling of negative zero float."""

    def test_converts_negative_zero_to_positive_zero(self):
        """Test that -0.0 is normalized to 0."""
        result = normalize_value(-0.0)
        assert result == 0
        # Ensure it's positive zero
        assert math.copysign(1.0, result) == 1.0

    def test_negative_zero_in_list(self):
        """Test negative zero normalization in lists."""
        result = normalize_value([-0.0, 1.0])
        assert result[0] == 0
        assert math.copysign(1.0, result[0]) == 1.0

    def test_negative_zero_in_dict(self):
        """Test negative zero normalization in dicts."""
        result = normalize_value({"value": -0.0})
        assert result["value"] == 0
        assert math.copysign(1.0, result["value"]) == 1.0

    def test_negative_zero_via_encode(self):
        """Test negative zero through encode() function."""
        result = encode(-0.0)
        assert result == "0"


class TestDatetimeConversion:
    """Test datetime conversion edge cases."""

    def test_datetime_with_timezone(self):
        """Test datetime with timezone converts to ISO format."""
        dt = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        result = normalize_value(dt)
        assert isinstance(result, str)
        assert "2024-01-01" in result
        assert "12:00:00" in result

    def test_datetime_without_timezone(self):
        """Test datetime without timezone converts to ISO format."""
        dt = datetime.datetime(2024, 6, 15, 18, 30, 45)
        result = normalize_value(dt)
        assert isinstance(result, str)
        assert "2024-06-15" in result
        assert "18:30:45" in result

    def test_datetime_with_microseconds(self):
        """Test datetime with microseconds converts correctly."""
        dt = datetime.datetime(2024, 1, 1, 0, 0, 0, 123456)
        result = normalize_value(dt)
        assert isinstance(result, str)
        assert "123456" in result or "0.123456" in result

    def test_datetime_in_nested_structure(self):
        """Test datetime normalization in nested structures."""
        dt = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
        result = normalize_value({"timestamp": dt, "nested": [dt]})
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["nested"][0], str)


class TestHeterogeneousSet:
    """Test set handling with mixed types."""

    def test_homogeneous_set_sorts_naturally(self):
        """Test set with uniform types sorts naturally."""
        result = normalize_value({3, 1, 2})
        assert result == [1, 2, 3]

    def test_homogeneous_string_set(self):
        """Test set of strings sorts alphabetically."""
        result = normalize_value({"zebra", "apple", "banana"})
        assert result == ["apple", "banana", "zebra"]

    def test_heterogeneous_set_uses_repr_fallback(self):
        """Test set with mixed types falls back to repr() sorting."""
        # Mix types that can't be compared directly
        result = normalize_value({1, "a", 2.5})
        # Should not raise, should use repr() for sorting
        assert isinstance(result, list)
        assert len(result) == 3
        assert 1 in result
        assert "a" in result
        assert 2.5 in result

    def test_set_with_none(self):
        """Test set containing None value."""
        result = normalize_value({None, "value", 42})
        assert isinstance(result, list)
        assert len(result) == 3
        assert None in result

    def test_empty_set(self):
        """Test empty set normalizes to empty list."""
        result = normalize_value(set())
        assert result == []

    def test_nested_set(self):
        """Test set normalization in nested structure."""
        result = normalize_value({"items": {3, 1, 2}})
        assert result == {"items": [1, 2, 3]}


class TestMappingConversion:
    """Test generic mapping type conversion."""

    def test_converts_ordered_dict(self):
        """Test OrderedDict converts to dict."""
        ordered = OrderedDict([("z", 1), ("a", 2), ("m", 3)])
        result = normalize_value(ordered)
        assert isinstance(result, dict)
        assert result["z"] == 1
        assert result["a"] == 2
        assert result["m"] == 3

    def test_converts_user_dict(self):
        """Test UserDict converts to dict."""

        class MyDict(UserDict):
            pass

        my_dict = MyDict({"key": "value", "num": 42})
        result = normalize_value(my_dict)
        assert isinstance(result, dict)
        assert result == {"key": "value", "num": 42}

    def test_normalizes_mapping_values_recursively(self):
        """Test mapping values are recursively normalized."""
        ordered = OrderedDict({"datetime": datetime.datetime(2024, 1, 1), "set": {1, 2, 3}})
        result = normalize_value(ordered)
        assert isinstance(result["datetime"], str)
        assert isinstance(result["set"], list)

    def test_converts_non_string_keys_to_strings(self):
        """Test mapping with non-string keys converts them to strings."""

        class IntKeyMapping(Mapping):
            def __init__(self):
                self._data = {1: "one", 2: "two", 3: "three"}

            def __getitem__(self, key):
                return self._data[key]

            def __iter__(self):
                return iter(self._data)

            def __len__(self):
                return len(self._data)

        mapping = IntKeyMapping()
        result = normalize_value(mapping)
        assert isinstance(result, dict)
        assert result["1"] == "one"
        assert result["2"] == "two"
        assert result["3"] == "three"

    def test_mapping_with_complex_values(self):
        """Test mapping with nested complex values."""
        ordered = OrderedDict({
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "set": {4, 5},
        })
        result = normalize_value(ordered)
        assert result["list"] == [1, 2, 3]
        assert result["dict"] == {"nested": "value"}
        assert result["set"] == [4, 5]


class TestUnsupportedTypes:
    """Test handling of unsupported types."""

    def test_complex_number_becomes_null(self):
        """Test complex numbers convert to null."""
        result = normalize_value(complex(1, 2))
        assert result is None

    def test_bytes_becomes_null(self):
        """Test bytes objects convert to null."""
        result = normalize_value(b"bytes")
        assert result is None

    def test_custom_class_becomes_null(self):
        """Test custom class instances convert to null."""

        class CustomClass:
            pass

        result = normalize_value(CustomClass())
        assert result is None

    def test_unsupported_type_in_list(self):
        """Test unsupported types in lists become null."""
        result = normalize_value([1, complex(1, 2), "valid"])
        assert result == [1, None, "valid"]

    def test_unsupported_type_in_dict(self):
        """Test unsupported types in dicts become null."""
        result = normalize_value({"valid": 1, "invalid": complex(1, 2)})
        assert result == {"valid": 1, "invalid": None}

    def test_unsupported_type_logs_warning(self, caplog):
        """Test unsupported types trigger warning logs."""
        with caplog.at_level(logging.WARNING, logger="ptoon.normalize"):
            normalize_value(complex(1, 2))

        # Check that a warning was logged
        assert any("Unsupported type" in record.message for record in caplog.records)
        assert any("complex" in record.message for record in caplog.records)


class TestNonFiniteNumbers:
    """Test handling of inf, -inf, and NaN."""

    def test_positive_infinity_becomes_null(self):
        """Test positive infinity converts to null."""
        result = normalize_value(float("inf"))
        assert result is None

    def test_negative_infinity_becomes_null(self):
        """Test negative infinity converts to null."""
        result = normalize_value(float("-inf"))
        assert result is None

    def test_nan_becomes_null(self):
        """Test NaN converts to null."""
        result = normalize_value(float("nan"))
        assert result is None

    def test_non_finite_in_list(self):
        """Test non-finite numbers in lists."""
        result = normalize_value([1.0, float("inf"), 2.0, float("nan")])
        assert result == [1.0, None, 2.0, None]

    def test_non_finite_in_dict(self):
        """Test non-finite numbers in dicts."""
        result = normalize_value({"a": float("inf"), "b": float("-inf"), "c": 1.0})
        assert result == {"a": None, "b": None, "c": 1.0}


class TestLargeIntegers:
    """Test handling of integers beyond JavaScript safe range."""

    def test_large_positive_integer_becomes_string(self):
        """Test large positive integers convert to strings."""
        large = 10**20  # Way beyond 2^53-1
        result = normalize_value(large)
        assert isinstance(result, str)
        assert result == str(large)

    def test_large_negative_integer_becomes_string(self):
        """Test large negative integers convert to strings."""
        large = -(10**20)
        result = normalize_value(large)
        assert isinstance(result, str)
        assert result == str(large)

    def test_safe_integer_remains_int(self):
        """Test integers within safe range remain ints."""
        safe = 2**53 - 1
        result = normalize_value(safe)
        assert isinstance(result, int)
        assert result == safe

    def test_just_over_safe_limit_becomes_string(self):
        """Test integer just over safe limit becomes string."""
        just_over = 2**53
        result = normalize_value(just_over)
        assert isinstance(result, str)

    def test_large_integer_in_nested_structure(self):
        """Test large integers in nested structures."""
        large = 10**20
        result = normalize_value({"big": large, "list": [large]})
        assert isinstance(result["big"], str)
        assert isinstance(result["list"][0], str)


class TestRecursiveNormalization:
    """Test recursive normalization of nested structures."""

    def test_deeply_nested_dict(self):
        """Test deeply nested dictionary normalization."""
        data = {
            "level1": {
                "level2": {
                    "level3": {"datetime": datetime.datetime(2024, 1, 1), "set": {1, 2}}
                }
            }
        }
        result = normalize_value(data)
        assert isinstance(result["level1"]["level2"]["level3"]["datetime"], str)
        assert isinstance(result["level1"]["level2"]["level3"]["set"], list)

    def test_mixed_nested_structure(self):
        """Test mixed nested structures (lists and dicts)."""
        data = {
            "list": [
                {"datetime": datetime.datetime(2024, 1, 1)},
                [1, {2, 3}],
            ]
        }
        result = normalize_value(data)
        assert isinstance(result["list"][0]["datetime"], str)
        assert result["list"][1] == [1, [2, 3]]

    def test_empty_nested_structures(self):
        """Test empty nested structures."""
        data = {"empty_dict": {}, "empty_list": [], "empty_set": set()}
        result = normalize_value(data)
        assert result == {"empty_dict": {}, "empty_list": [], "empty_set": []}
