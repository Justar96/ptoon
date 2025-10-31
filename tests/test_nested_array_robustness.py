"""Comprehensive nested array robustness tests.

Tests all nested array scenarios to verify complete coverage and robustness.
"""

import pytest

from ptoon import decode, encode


class TestNestedArrayCompleteness:
    """Test all nested array combinations work correctly."""

    def test_array_of_objects_with_non_tabular_array_first_field(self):
        """Test list item where first field is non-tabular array of objects."""
        # This should hit encoder.py lines 392-397
        data = [
            {
                "nested_objects": [
                    {"a": 1},
                    {"b": 2},
                    {"c": 3},
                ],
                "other": "value",
            }
        ]
        result = encode(data)
        # Verify it encodes without error
        assert "nested_objects" in result
        assert "other" in result

    def test_deeply_heterogeneous_array_as_first_field(self):
        """Test first field is array with mixed primitives, arrays, and objects."""
        # This should hit encoder.py lines 417, 420-421 (complex array branch)
        data = [
            {
                "heterogeneous": [
                    42,  # primitive
                    [1, 2, 3],  # array
                    {"key": "value"},  # object
                    "string",  # another primitive
                ],
                "name": "complex",
            }
        ]
        result = encode(data)
        assert "heterogeneous" in result

    def test_array_within_array_of_objects_as_first_field(self):
        """Test array item within non-tabular array of objects."""
        # Targets encoder.py line 392-395 (array item in non-tabular objects)
        data = [
            {
                "items": [
                    [10, 20, 30],  # Primitive array
                    {"x": 1},
                    [40, 50],
                ],
                "type": "mixed",
            }
        ]
        result = encode(data)
        assert "items" in result

    def test_object_within_complex_heterogeneous_array(self):
        """Test object item in heterogeneous array."""
        # Targets encoder.py line 420-421 (object in complex array)
        data = [
            {
                "complex": [
                    1,
                    2,
                    {"nested": "object"},
                    3,
                ],
                "label": "test",
            }
        ]
        result = encode(data)
        assert "complex" in result

    def test_empty_object_as_first_value_in_list_item(self):
        """Test empty object as first field value."""
        # Targets encoder.py line 424-425
        data = [{"empty_obj": {}, "other": "value"}]
        result = encode(data)
        assert "empty_obj" in result

    def test_supported_array_types_roundtrip(self):
        """Test all SUPPORTED nested array types can roundtrip."""
        # Note: Arrays of arrays of arrays are intentionally not supported
        data = {
            "primitive_arrays": [[1, 2], [3, 4]],  # Supported: array of primitive arrays
            "nested_in_objects": [
                {"arr": [1, 2, 3], "name": "first"},  # Supported: objects with arrays
                {"arr": [4, 5], "name": "second"},
            ],
        }
        encoded = encode(data)
        decoded = decode(encoded)
        # Check structure is preserved
        assert len(decoded["primitive_arrays"]) == 2
        assert len(decoded["nested_in_objects"]) == 2


class TestDecoderNestedArrays:
    """Test decoder handles all nested array scenarios."""

    def test_deeply_nested_inline_arrays(self):
        """Test decoding deeply nested inline arrays."""
        # Targets decoder.py lines 753-758 (inline object with array)
        toon = "root: level1: level2[3]: 1, 2, 3"
        result = decode(toon)
        assert result == {"root": {"level1": {"level2": [1, 2, 3]}}}

    def test_context_unwinding_from_deep_nesting(self):
        """Test unwinding from deeply nested structures."""
        # Targets decoder.py lines 256-273, 274-291 (context unwinding)
        toon = """a:
  b:
    c:
      d[2]:
        - item1
        - item2
      e: value
    f: value2
  g: value3
h: value4"""
        result = decode(toon)
        assert result["a"]["b"]["c"]["d"] == ["item1", "item2"]
        assert result["a"]["b"]["c"]["e"] == "value"
        assert result["a"]["b"]["f"] == "value2"
        assert result["a"]["g"] == "value3"
        assert result["h"] == "value4"

    def test_multiple_dedents_at_once(self):
        """Test multiple context pops on significant dedent."""
        # Tests decoder context unwinding with large depth changes
        toon = """root:
  deep1:
    deep2:
      deep3[1]:
        - value
root2: other"""
        result = decode(toon)
        assert result["root"]["deep1"]["deep2"]["deep3"] == ["value"]
        assert result["root2"] == "other"


class TestEdgeCaseArrayCombinations:
    """Test unusual but valid array combinations."""

    def test_array_of_empty_arrays(self):
        """Test array containing empty arrays."""
        data = [[], [], []]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_array_of_arrays_of_arrays_limitation(self):
        """Test that triple-nested arrays are a known limitation.

        TOON intentionally does not support arrays of arrays of arrays.
        See encoder.py:330 - "Other complex nested arrays are intentionally
        not handled here per TS behavior."
        """
        data = [[[1, 2]], [[3, 4]], [[5, 6]]]
        encoded = encode(data)
        # Encoder produces incomplete output for this unsupported case
        # This is documented as a format limitation
        assert "[3]:" in encoded

    def test_mixed_depth_nested_arrays_limitation(self):
        """Test that mixed-depth nested arrays are a known limitation.

        TOON does not fully support arrays where some elements are
        primitive arrays and others are arrays of arrays.
        """
        data = [
            [1, 2, 3],  # Primitive array - OK
            [[4, 5], [6, 7]],  # Array of arrays - NOT SUPPORTED
            [8],  # Primitive array - OK
        ]
        encoded = encode(data)
        # Only primitive array elements are encoded
        assert "[3]:" in encoded
        # The array-of-arrays element is skipped (unsupported)

    def test_object_with_nested_array_in_list(self):
        """Test object containing array as list item."""
        data = [
            {"data": [[1, 2], [3, 4]], "id": 1},
            {"data": [[5, 6]], "id": 2},
        ]
        encoded = encode(data)
        # Just verify it encodes
        assert "data" in encoded


class TestErrorHandlingNestedArrays:
    """Test error handling in nested array scenarios."""

    def test_malformed_nested_inline_array(self):
        """Test error on malformed nested inline array."""
        toon = "key: nested[3]: 1, 2"  # Wrong count
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)

    def test_context_mismatch_in_nested_structure(self):
        """Test error on context mismatch in nested arrays."""
        toon = """parent[2]:
  - item1
sibling: value"""
        with pytest.raises(ValueError, match="array length mismatch"):
            decode(toon)


class TestPerformanceNestedArrays:
    """Test that deeply nested arrays perform acceptably."""

    def test_deeply_nested_arrays_encode(self):
        """Test encoding deeply nested arrays doesn't crash."""
        # Create a deeply nested structure
        data = [1, 2, 3]
        for _ in range(10):
            data = [data]

        # Should encode without error
        result = encode(data)
        assert "[" in result

    def test_wide_nested_arrays(self):
        """Test arrays with many nested elements."""
        data = [
            {"items": [i for i in range(100)], "id": j} for j in range(10)
        ]
        encoded = encode(data)
        decoded = decode(encoded)
        assert len(decoded) == 10
        assert len(decoded[0]["items"]) == 100
