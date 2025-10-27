import datetime
from decimal import Decimal

from toon import encode


def test_converts_large_integers_to_string():
    big = 10**20
    bigger = 10**50
    assert encode(big) == f'"{big}"'
    assert encode(bigger) == f'"{bigger}"'


def test_converts_datetime_to_iso_string():
    dt = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert encode(dt) == '"2025-01-01T00:00:00+00:00"'


def test_converts_non_finite_numbers_to_null():
    assert encode(float("inf")) == "null"
    assert encode(float("-inf")) == "null"
    assert encode(float("nan")) == "null"


def test_converts_functions_to_null():
    assert encode(lambda x: x) == "null"


class _C:  # custom class
    pass


def test_converts_other_objects_to_null():
    assert encode(_C()) == "null"
    assert encode(Decimal("1.23")) == "null"
    assert encode(complex(1, 2)) == "null"
    assert encode(b"bytes") == "null"
