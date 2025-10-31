"""Manual test script for timeout functionality.

Run this script directly to verify timeout behavior:
    python -m benchmarks.test_timeout_manual
"""

from __future__ import annotations

import sys
import time

from .stress_benchmark import measure_with_timeout


def test_timeout_with_sleep():
    """Test that timeout works with a long-running sleep."""
    print(f"Platform: {sys.platform}")
    print("\n1. Testing timeout with 5-second sleep (1-second timeout)...")

    start = time.perf_counter()
    result, duration, timed_out = measure_with_timeout(time.sleep, 1, 5)
    elapsed = time.perf_counter() - start

    print(f"   Result: {result}")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Timed out: {timed_out}")
    print(f"   Total elapsed: {elapsed:.2f}s")

    if timed_out and elapsed < 3.0:
        print("   ✓ PASS: Timeout worked correctly and returned promptly")
    else:
        print(f"   ✗ FAIL: Expected timeout=True and elapsed<3s, got timeout={timed_out}, elapsed={elapsed:.2f}s")


def test_success_case():
    """Test that successful execution works correctly."""
    print("\n2. Testing successful execution (fast function)...")

    def add(x: int, y: int) -> int:
        return x + y

    result, duration, timed_out = measure_with_timeout(add, 5, 10, 20)

    print(f"   Result: {result}")
    print(f"   Duration: {duration:.6f}s")
    print(f"   Timed out: {timed_out}")

    if result == 30 and not timed_out:
        print("   ✓ PASS: Successful execution works correctly")
    else:
        print(f"   ✗ FAIL: Expected result=30, timed_out=False, got result={result}, timed_out={timed_out}")


def test_exception_propagation():
    """Test that exceptions are properly propagated."""
    print("\n3. Testing exception propagation...")

    def failing_func():
        raise ValueError("Test error")

    try:
        result, duration, timed_out = measure_with_timeout(failing_func, 5)
        print("   ✗ FAIL: Expected ValueError to be raised")
    except ValueError as e:
        if "Test error" in str(e):
            print("   ✓ PASS: Exception properly propagated")
        else:
            print(f"   ✗ FAIL: Wrong exception message: {e}")


def test_no_zombie_processes():
    """Test that no zombie processes are left after timeout."""
    import subprocess

    print("\n4. Testing for zombie processes after timeout...")

    # Get initial process count
    if sys.platform == "win32":
        # On Windows, check for python processes
        cmd = 'tasklist /FI "IMAGENAME eq python.exe" /FO CSV'
    else:
        # On Unix, check for child processes
        cmd = "ps aux | grep python | grep -v grep | wc -l"

    initial_count = len(subprocess.check_output(cmd, shell=True).decode().strip().split("\n"))

    # Run timeout test
    result, duration, timed_out = measure_with_timeout(time.sleep, 1, 5)

    # Wait a moment for cleanup
    time.sleep(0.5)

    # Check final process count
    final_count = len(subprocess.check_output(cmd, shell=True).decode().strip().split("\n"))

    print(f"   Initial process count: {initial_count}")
    print(f"   Final process count: {final_count}")

    if final_count <= initial_count + 1:  # Allow for 1 extra for this process
        print("   ✓ PASS: No zombie processes detected")
    else:
        print(f"   ✗ WARNING: Possible zombie processes (delta: {final_count - initial_count})")


def main():
    """Run all manual tests."""
    print("=" * 70)
    print("Manual Timeout Test Suite")
    print("=" * 70)

    test_timeout_with_sleep()
    test_success_case()
    test_exception_propagation()

    # Skip zombie check on Windows as tasklist is complex to parse
    if sys.platform != "win32":
        test_no_zombie_processes()

    print("\n" + "=" * 70)
    print("Tests complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
