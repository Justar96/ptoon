import time

import pytest

from ptoon import decode, encode


@pytest.mark.slow
def test_encode_decode_perf_smoke():
    """Ensure encoding/decoding a moderate payload stays within bounds."""
    payload = list(range(10_000))

    start = time.perf_counter()
    encoded = encode(payload)
    decoded = decode(encoded)
    duration = time.perf_counter() - start

    assert decoded == payload
    assert duration < 2.0, f"Encode/decode took {duration:.2f}s, exceeds 2.0s budget"
