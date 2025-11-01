#!/usr/bin/env python
"""
Comprehensive integration test for ptoon package from PyPI.
This script tests all public APIs and common use cases.
"""

import sys

import ptoon


def test_version():
    """Test version attribute."""
    print("[✓] Version:", ptoon.__version__)
    assert hasattr(ptoon, "__version__")
    assert isinstance(ptoon.__version__, str)


def test_basic_encode_decode():
    """Test basic encode/decode roundtrip."""
    print("\n[Test] Basic encode/decode")

    data = {"name": "Alice", "age": 30, "active": True}
    encoded = ptoon.encode(data)
    decoded = ptoon.decode(encoded)

    assert decoded == data, f"Roundtrip failed: {decoded} != {data}"
    print("[✓] Simple object roundtrip works")


def test_tabular_format():
    """Test tabular format for uniform arrays."""
    print("\n[Test] Tabular format")

    data = {
        "users": [
            {"id": 1, "name": "Alice", "score": 95},
            {"id": 2, "name": "Bob", "score": 87},
        ]
    }

    encoded = ptoon.encode(data)
    print(f"Encoded:\n{encoded}")

    # Verify tabular format is used
    assert "users[2]{id,name,score}:" in encoded.replace(" ", ""), "Tabular format not detected"

    decoded = ptoon.decode(encoded)
    assert decoded == data, "Tabular roundtrip failed"
    print("[✓] Tabular format works")


def test_inline_array():
    """Test inline array format."""
    print("\n[Test] Inline array")

    data = {"tags": ["python", "llm", "optimization"]}
    encoded = ptoon.encode(data)
    decoded = ptoon.decode(encoded)

    assert decoded == data, "Inline array roundtrip failed"
    print("[✓] Inline array works")


def test_nested_structures():
    """Test nested objects and arrays."""
    print("\n[Test] Nested structures")

    data = {"project": "ptoon", "metadata": {"version": "0.0.1", "author": "TOON Contributors"}, "stats": [10, 20, 30]}

    encoded = ptoon.encode(data)
    decoded = ptoon.decode(encoded)

    assert decoded == data, "Nested structure roundtrip failed"
    print("[✓] Nested structures work")


def test_encoding_options():
    """Test different encoding options."""
    print("\n[Test] Encoding options")

    data = {"items": ["a", "b", "c"]}

    # Test pipe delimiter
    encoded_pipe = ptoon.encode(data, {"delimiter": "|"})
    assert "|" in encoded_pipe, "Pipe delimiter not used"
    decoded_pipe = ptoon.decode(encoded_pipe)
    assert decoded_pipe == data, "Pipe delimiter roundtrip failed"

    # Test tab delimiter
    encoded_tab = ptoon.encode(data, {"delimiter": "\t"})
    assert "\t" in encoded_tab, "Tab delimiter not used"
    decoded_tab = ptoon.decode(encoded_tab)
    assert decoded_tab == data, "Tab delimiter roundtrip failed"

    # Test custom indent
    encoded_indent = ptoon.encode(data, {"indent": 4})
    decoded_indent = ptoon.decode(encoded_indent)
    assert decoded_indent == data, "Custom indent roundtrip failed"

    print("[✓] Encoding options work")


def test_special_values():
    """Test special values (None, booleans, numbers)."""
    print("\n[Test] Special values")

    data = {
        "null_value": None,
        "true_value": True,
        "false_value": False,
        "int_value": 42,
        "float_value": 3.14,
        "zero": 0,
        "negative": -10,
    }

    encoded = ptoon.encode(data)
    decoded = ptoon.decode(encoded)

    assert decoded == data, "Special values roundtrip failed"
    print("[✓] Special values work")


def test_empty_collections():
    """Test empty arrays and objects."""
    print("\n[Test] Empty collections")

    data = {"empty_array": [], "empty_object": {}, "name": "test"}

    encoded = ptoon.encode(data)
    decoded = ptoon.decode(encoded)

    assert decoded == data, "Empty collections roundtrip failed"
    print("[✓] Empty collections work")


def test_utility_functions():
    """Test utility functions for token counting."""
    print("\n[Test] Utility functions")

    data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

    # Test estimate_savings (should work without tiktoken)
    try:
        savings = ptoon.estimate_savings(data)
        print(f"Token savings: {savings['savings']} tokens ({savings['savings_percent']:.1f}%)")
        assert isinstance(savings, dict), "estimate_savings should return dict"
        assert "json_tokens" in savings, "Missing json_tokens in savings"
        assert "toon_tokens" in savings, "Missing toon_tokens in savings"
        assert "savings" in savings, "Missing savings in savings"
        print("[✓] Utility functions work (with tiktoken)")
    except RuntimeError as e:
        if "tiktoken is required" in str(e):
            print("[⚠] Utility functions require tiktoken (optional dependency)")
        else:
            raise


def test_type_exports():
    """Test that all documented types are exported."""
    print("\n[Test] Type exports")

    expected_exports = [
        "__version__",
        "encode",
        "decode",
        "DEFAULT_DELIMITER",
        "DELIMITERS",
        "JsonPrimitive",
        "JsonArray",
        "JsonObject",
        "JsonValue",
        "Delimiter",
        "EncodeOptions",
        "count_tokens",
        "estimate_savings",
        "compare_formats",
    ]

    for name in expected_exports:
        assert hasattr(ptoon, name), f"Missing export: {name}"

    print(f"[✓] All {len(expected_exports)} exports available")


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n[Test] Error handling")

    # Test decode with non-string
    try:
        ptoon.decode(123)  # type: ignore
        raise AssertionError("Should raise TypeError")
    except TypeError as e:
        assert "expects a string" in str(e)
        print("[✓] Decode rejects non-string input")

    # Test encode with invalid options
    try:
        ptoon.encode({"a": 1}, {"invalid_option": True})  # type: ignore
        raise AssertionError("Should raise ValueError")
    except ValueError as e:
        assert "unsupported keys" in str(e)
        print("[✓] Encode rejects invalid options")

    # Test invalid delimiter
    try:
        ptoon.encode({"a": 1}, {"delimiter": ";"})
        raise AssertionError("Should raise ValueError")
    except ValueError as e:
        assert "delimiter must be" in str(e)
        print("[✓] Encode rejects invalid delimiter")


def test_py_typed_marker():
    """Test that py.typed marker file exists."""
    print("\n[Test] py.typed marker")

    import os

    module_dir = os.path.dirname(ptoon.__file__)
    py_typed = os.path.join(module_dir, "py.typed")

    assert os.path.exists(py_typed), "py.typed marker file missing"
    print(f"[✓] py.typed marker exists at: {py_typed}")


def main():
    """Run all tests."""
    print("=" * 70)
    print("ptoon PyPI Integration Tests")
    print("=" * 70)

    tests = [
        test_version,
        test_basic_encode_decode,
        test_tabular_format,
        test_inline_array,
        test_nested_structures,
        test_encoding_options,
        test_special_values,
        test_empty_collections,
        test_utility_functions,
        test_type_exports,
        test_error_handling,
        test_py_typed_marker,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n[✗] {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[✗] {test.__name__} ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 All tests passed! ptoon is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
