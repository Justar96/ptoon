"""Tests for benchmark timeout functionality."""

from __future__ import annotations

import sys
import time

import pytest


# Define test functions at module level so they can be pickled for Windows multiprocessing
def _slow_function(duration: float) -> str:
    """Sleep for specified duration."""
    time.sleep(duration)
    return "completed"


def _fast_function(x: int, y: int) -> int:
    """Simple addition."""
    return x + y


def _failing_function() -> None:
    """Function that raises an exception."""
    raise ValueError("Test error")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific timeout test")
def test_windows_timeout_terminates_quickly():
    """Verify that Windows timeout returns promptly and doesn't leave running processes."""
    # Import here to avoid issues if benchmarks aren't available
    from benchmarks.stress_benchmark import measure_with_timeout

    # Test that a 5-second sleep times out after 1 second
    start = time.perf_counter()
    result, duration, timed_out = measure_with_timeout(_slow_function, 1, 5.0)
    elapsed = time.perf_counter() - start

    # Assertions
    assert timed_out is True, "Function should have timed out"
    assert result is None, "Result should be None on timeout"
    assert duration >= 1.0, "Duration should be at least the timeout period"
    assert elapsed < 3.0, f"Function should return within ~1s, but took {elapsed:.2f}s"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific timeout test")
def test_windows_timeout_success_case():
    """Verify that Windows timeout works correctly for fast functions."""
    from benchmarks.stress_benchmark import measure_with_timeout

    # Test successful completion within timeout
    result, duration, timed_out = measure_with_timeout(_fast_function, 5, 10, 20)

    # Assertions
    assert timed_out is False, "Function should not have timed out"
    assert result == 30, "Result should be correct"
    assert duration < 1.0, "Fast function should complete quickly"


@pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific timeout test")
def test_unix_timeout_with_signal():
    """Verify that Unix signal-based timeout works correctly."""
    from benchmarks.stress_benchmark import measure_with_timeout

    # Test that a 5-second sleep times out after 1 second
    start = time.perf_counter()
    result, duration, timed_out = measure_with_timeout(_slow_function, 1, 5.0)
    elapsed = time.perf_counter() - start

    # Assertions
    assert timed_out is True, "Function should have timed out"
    assert result is None, "Result should be None on timeout"
    assert duration >= 1.0, "Duration should be at least the timeout period"
    assert elapsed < 3.0, f"Function should return within ~1s, but took {elapsed:.2f}s"


def test_timeout_with_exception():
    """Verify that exceptions in timed functions are properly propagated."""
    from benchmarks.stress_benchmark import measure_with_timeout

    # Test that exceptions are properly raised
    with pytest.raises(ValueError, match="Test error"):
        measure_with_timeout(_failing_function, 5)
