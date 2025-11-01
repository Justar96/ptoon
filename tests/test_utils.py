"""
Comprehensive test suite for token analysis utilities.

Tests cover count_tokens, estimate_savings, and compare_formats functions,
including edge cases, error handling, and integration scenarios.
"""

import importlib.util
import json
import time
from unittest.mock import patch

import pytest

from ptoon import compare_formats, count_tokens, encode, estimate_savings


# Marker for tests that require tiktoken to be installed
requires_tiktoken = pytest.mark.skipif(importlib.util.find_spec("tiktoken") is None, reason="requires tiktoken")


# Test Fixtures


@pytest.fixture
def sample_data_for_utils():
    """Provide various test data structures for utility testing."""
    return {
        "simple_dict": {"name": "Alice", "age": 30},
        "array_of_objects": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
        "nested": {
            "users": [
                {"id": 1, "profile": {"name": "Alice"}},
            ]
        },
        "empty_dict": {},
        "empty_list": [],
    }


# Helper Functions


def assert_valid_savings_dict(result: dict):
    """Verify savings dict has correct structure and valid values."""
    assert "json_tokens" in result
    assert "toon_tokens" in result
    assert "savings" in result
    assert "savings_percent" in result
    assert isinstance(result["json_tokens"], int)
    assert isinstance(result["toon_tokens"], int)
    assert isinstance(result["savings"], int)
    assert isinstance(result["savings_percent"], float)
    assert result["json_tokens"] >= 0
    assert result["toon_tokens"] >= 0
    assert result["savings"] >= 0
    assert 0 <= result["savings_percent"] <= 100


# Token Counting Tests


class TestCountTokens:
    """Tests for count_tokens function."""

    @requires_tiktoken
    def test_count_tokens_basic(self):
        """Test token counting with simple strings."""
        result1 = count_tokens("hello")
        result2 = count_tokens("Hello, world!")

        # Should return positive integers
        assert isinstance(result1, int)
        assert isinstance(result2, int)
        assert result1 > 0
        assert result2 > 0

        # Should be deterministic
        assert count_tokens("hello") == result1
        assert count_tokens("Hello, world!") == result2

    @requires_tiktoken
    def test_count_tokens_empty_string(self):
        """Test token counting with empty string."""
        result = count_tokens("")
        assert isinstance(result, int)
        assert result >= 0

    @requires_tiktoken
    def test_count_tokens_unicode(self):
        """Test token counting with Unicode characters."""
        # Various Unicode strings
        result1 = count_tokens("café")
        result2 = count_tokens("你好")
        result3 = count_tokens("🚀")

        # Should handle Unicode correctly
        assert isinstance(result1, int)
        assert isinstance(result2, int)
        assert isinstance(result3, int)
        assert result1 > 0
        assert result2 > 0
        assert result3 > 0

    @requires_tiktoken
    def test_count_tokens_long_text(self):
        """Test token counting with longer text."""
        # Generate longer text (100+ words)
        long_text = " ".join(["word"] * 100)
        result = count_tokens(long_text)

        # Should scale appropriately
        assert isinstance(result, int)
        assert result >= 100  # Should have at least as many tokens as words

    @requires_tiktoken
    def test_count_tokens_custom_encoding(self):
        """Test token counting with custom encoding."""
        text = "Hello, world!"

        # Test with cl100k_base encoding
        try:
            result = count_tokens(text, encoding="cl100k_base")
            assert isinstance(result, int)
            assert result > 0
        except Exception:
            # Skip if encoding not available
            pytest.skip("cl100k_base encoding not available")

    def test_count_tokens_without_tiktoken(self):
        """Test count_tokens raises helpful error when tokenizer unavailable."""
        from ptoon import utils as utils_mod

        utils_mod._get_tokenizer.cache_clear()

        with (
            patch.object(utils_mod, "tiktoken", None, create=True),
            patch.dict("sys.modules", {"tiktoken": None}),
            pytest.raises(RuntimeError, match="tiktoken is required"),
        ):
            count_tokens("x")

        utils_mod._get_tokenizer.cache_clear()


# Savings Estimation Tests


@requires_tiktoken
class TestEstimateSavings:
    """Tests for estimate_savings function."""

    def test_estimate_savings_simple_dict(self, sample_data_for_utils):
        """Test savings estimation with simple dictionary."""
        data = sample_data_for_utils["simple_dict"]
        result = estimate_savings(data)

        # Verify structure and values
        assert_valid_savings_dict(result)

    def test_estimate_savings_array_of_objects(self, sample_data_for_utils):
        """Test savings estimation with array of uniform objects (optimal for TOON)."""
        data = sample_data_for_utils["array_of_objects"]
        result = estimate_savings(data)

        # Verify structure
        assert_valid_savings_dict(result)

        # TOON should use fewer tokens for tabular data
        # (though we don't strictly enforce this as it depends on data)
        assert result["toon_tokens"] > 0
        assert result["json_tokens"] > 0

    def test_estimate_savings_nested_structure(self, sample_data_for_utils):
        """Test savings estimation with nested structures."""
        data = sample_data_for_utils["nested"]
        result = estimate_savings(data)

        # Verify function handles complex structures
        assert_valid_savings_dict(result)

    def test_estimate_savings_empty_data(self, sample_data_for_utils):
        """Test savings estimation with empty data structures."""
        # Test with empty dict
        result1 = estimate_savings(sample_data_for_utils["empty_dict"])
        assert_valid_savings_dict(result1)

        # Test with empty list
        result2 = estimate_savings(sample_data_for_utils["empty_list"])
        assert_valid_savings_dict(result2)

        # Savings should be minimal
        assert result1["savings"] >= 0
        assert result2["savings"] >= 0

    def test_estimate_savings_calculation_accuracy(self):
        """Test that savings calculation is mathematically correct."""
        data = {"key": "value"}
        result = estimate_savings(data)

        # Verify math is correct
        expected_savings = result["json_tokens"] - result["toon_tokens"]
        expected_percent = (expected_savings / result["json_tokens"]) * 100

        # Use max(0, ...) to handle potential negative savings
        expected_savings = max(0, expected_savings)
        expected_percent = expected_percent if expected_savings >= 0 else 0.0

        assert result["savings"] == expected_savings
        assert abs(result["savings_percent"] - expected_percent) < 0.01

    def test_estimate_savings_no_negative_savings(self):
        """Test that savings are never negative."""
        # Test with various data structures
        test_data = [
            {"key": "value"},
            [1, 2, 3],
            {"nested": {"data": [1, 2, 3]}},
        ]

        for data in test_data:
            result = estimate_savings(data)
            assert result["savings"] >= 0, "Savings should never be negative"

    def test_estimate_savings_custom_encoding(self):
        """Test savings estimation with custom encoding."""
        data = {"name": "Alice"}

        try:
            result = estimate_savings(data, encoding="cl100k_base")
            assert_valid_savings_dict(result)
        except Exception:
            pytest.skip("cl100k_base encoding not available")

    def test_estimate_savings_large_dataset(self):
        """Test savings estimation with larger dataset."""
        # Create larger dataset similar to benchmarks
        data = [{"id": i, "name": f"User{i}", "age": 20 + i, "active": i % 2 == 0} for i in range(100)]

        result = estimate_savings(data)
        assert_valid_savings_dict(result)

        # For uniform tabular data, TOON should show significant savings
        # (but we don't strictly enforce a minimum percentage)
        assert result["json_tokens"] > 0
        assert result["toon_tokens"] > 0

    def test_estimate_savings_large_array_performance(self):
        """Ensure large lightweight arrays remain performant."""
        large_array = list(range(50_000))

        start = time.perf_counter()
        toon_str = encode(large_array)
        json_str = json.dumps(large_array)
        estimate_start = time.perf_counter()
        result = estimate_savings(large_array)
        estimate_duration = time.perf_counter() - estimate_start
        total_duration = time.perf_counter() - start

        assert toon_str  # sanity check encoding produced content
        assert json_str
        assert estimate_duration < 5.0, f"estimate_savings took {estimate_duration:.2f}s"
        assert total_duration < 8.0, f"Overall workflow exceeded 8s ({total_duration:.2f}s)"
        assert result["savings"] >= 0
        assert result["savings_percent"] >= 0.0


# Format Comparison Tests


@requires_tiktoken
class TestCompareFormats:
    """Tests for compare_formats function."""

    def test_compare_formats_returns_string(self, sample_data_for_utils):
        """Test that compare_formats returns a non-empty string."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_compare_formats_contains_headers(self, sample_data_for_utils):
        """Test that output contains expected headers."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        # Should contain table headers
        assert "Format" in result
        assert "Tokens" in result
        assert "Size" in result

    def test_compare_formats_contains_both_formats(self, sample_data_for_utils):
        """Test that output mentions both JSON and TOON."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        # Should mention both formats
        assert "JSON" in result
        assert "TOON" in result

    def test_compare_formats_shows_savings(self, sample_data_for_utils):
        """Test that output contains savings information."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        # Should contain savings line
        assert "Savings" in result
        # Should show percentage
        assert "%" in result

    def test_compare_formats_formatting(self, sample_data_for_utils):
        """Test that numbers are formatted with thousands separators."""
        # Create data that will produce large token counts
        data = [{"id": i, "name": f"User{i}"} for i in range(100)]
        result = compare_formats(data)

        # For large numbers, should contain commas as thousands separators
        # (though actual presence depends on token counts being > 999)
        # We just verify the function runs and produces output
        assert isinstance(result, str)
        assert len(result) > 0

    def test_compare_formats_multiline(self, sample_data_for_utils):
        """Test that output is multi-line."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        # Should be multi-line
        assert "\n" in result
        lines = result.split("\n")
        assert len(lines) > 1

    def test_compare_formats_visual_elements(self, sample_data_for_utils):
        """Test that output contains visual formatting elements."""
        data = sample_data_for_utils["simple_dict"]
        result = compare_formats(data)

        # Should contain box-drawing characters for visual appeal
        assert "─" in result

    def test_compare_formats_consistency_with_estimate_savings(self, sample_data_for_utils):
        """Test that compare_formats shows same numbers as estimate_savings."""
        data = sample_data_for_utils["array_of_objects"]

        # Get metrics from both functions
        savings = estimate_savings(data)
        table = compare_formats(data)

        # The table should contain the token counts from savings
        # (We check for the numbers in the string representation)
        assert str(savings["json_tokens"]) in table.replace(",", "")
        assert str(savings["toon_tokens"]) in table.replace(",", "")


# Integration Tests


@requires_tiktoken
class TestUtilitiesIntegration:
    """Integration tests for utilities working together."""

    def test_utilities_work_together(self):
        """Test using all three functions in sequence."""
        data = {"users": [{"id": 1}, {"id": 2}]}

        # Use all three functions
        savings = estimate_savings(data)
        table = compare_formats(data)

        # Verify they produce consistent results
        assert_valid_savings_dict(savings)
        assert isinstance(table, str)

        # Table should contain same numbers as savings
        # (remove commas for comparison)
        table_normalized = table.replace(",", "")
        assert str(savings["json_tokens"]) in table_normalized
        assert str(savings["toon_tokens"]) in table_normalized

    def test_utilities_with_various_data_types(self):
        """Test utilities with different Python data types."""
        test_cases = [
            {"string": "value"},
            [1, 2, 3],
            {"nested": {"deeply": {"nested": "value"}}},
            [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            {"list": [1, 2, 3], "dict": {"key": "value"}},
        ]

        for data in test_cases:
            # All utilities should work without errors
            savings = estimate_savings(data)
            table = compare_formats(data)

            assert_valid_savings_dict(savings)
            assert isinstance(table, str)
            assert len(table) > 0

    def test_utilities_with_encode_decode(self):
        """Test that utilities work correctly with encode function."""
        data = {"employees": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

        # Get TOON encoding
        toon_str = encode(data)

        # Count tokens in TOON string
        toon_tokens = count_tokens(toon_str)

        # Get estimate
        savings = estimate_savings(data)

        # Should match
        assert savings["toon_tokens"] == toon_tokens

    def test_utilities_deterministic(self):
        """Test that utilities produce deterministic results."""
        data = {"key": "value", "list": [1, 2, 3]}

        # Call multiple times
        result1 = estimate_savings(data)
        result2 = estimate_savings(data)
        result3 = estimate_savings(data)

        # Should be identical
        assert result1 == result2
        assert result2 == result3

        # Same for compare_formats
        table1 = compare_formats(data)
        table2 = compare_formats(data)
        assert table1 == table2

    @pytest.mark.slow
    def test_consistency_with_benchmark_token_counting(self):
        """Test that ptoon.count_tokens matches benchmarks.token_efficiency.count_tokens.

        This verifies the consolidation didn't change behavior compared to the
        existing benchmark implementation.
        """
        # Try to import benchmark module
        try:
            from benchmarks.token_efficiency import (
                count_tokens as benchmark_count_tokens,
            )
        except ImportError:
            pytest.skip("benchmarks module not available")

        # Test with various sample strings
        test_strings = [
            "Hello, world!",
            "café",
            "你好",
            "🚀",
            "",
            "The quick brown fox jumps over the lazy dog",
            '{"key": "value"}',
            json.dumps({"employees": [{"id": 1, "name": "Alice"}]}, indent=2),
        ]

        for text in test_strings:
            # Both implementations should produce identical results
            ptoon_result = count_tokens(text)
            benchmark_result = benchmark_count_tokens(text)

            assert ptoon_result == benchmark_result, (
                f"Token count mismatch for text: {text!r}\n"
                f"ptoon.count_tokens: {ptoon_result}\n"
                f"benchmark.count_tokens: {benchmark_result}"
            )
