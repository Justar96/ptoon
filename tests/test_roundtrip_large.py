import time

import pytest

from ptoon import decode, encode


@pytest.mark.slow
def test_large_roundtrip_stability():
    """Encode/decode a large uniform dataset without regressing on performance."""
    records = [{"id": i, "name": f"user-{i}"} for i in range(5_000)]

    start = time.perf_counter()
    encoded = encode(records)
    round_tripped = decode(encoded)
    duration = time.perf_counter() - start

    assert round_tripped == records
    assert duration < 5.0, f"Large roundtrip exceeded 5.0s budget ({duration:.2f}s)"
