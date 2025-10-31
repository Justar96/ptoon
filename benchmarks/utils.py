"""Shared utility functions for benchmarks."""

from __future__ import annotations


def format_bytes(n: int) -> str:
    """Format byte count as human-readable string.

    Args:
        n: Number of bytes

    Returns:
        Formatted string (e.g., "1.23 MB", "456 KB", "789 B")
    """
    if n < 1024:
        return f"{n} B"
    kb = n / 1024.0
    if kb < 1024:
        return f"{kb:.2f} KB"
    mb = kb / 1024.0
    return f"{mb:.2f} MB"


def format_time(seconds: float) -> str:
    """Format time duration as human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1.23 ms", "456.78 µs")
    """
    ms = seconds * 1000.0
    if ms < 1.0:
        return f"{ms * 1000.0:.2f} µs"
    return f"{ms:.2f} ms"
