from __future__ import annotations

import datetime as _dt
import typing as _t

import pytest

from toon import encode, decode


@pytest.fixture
def sample_primitives() -> dict:
    return {
        "empty": "",
        "alpha": "hello",
        "unicode": "café",
        "emoji": "🚀",
        "int": 42,
        "neg_int": -7,
        "float": 3.14,
        "bool_t": True,
        "bool_f": False,
        "none": None,
    }


@pytest.fixture
def sample_objects() -> list:
    return [
        {"id": 1, "name": "Ada", "active": True},
        {"a": {"b": {"c": "deep"}}},
        {"text": " padded ", "note": "he said \"hi\""},
        {"order:id": 7, "full name": "Alan"},
    ]


@pytest.fixture
def sample_arrays() -> list:
    return [
        ["reading", "gaming"],
        [1, 2, 3],
        ["x", True, 10],
        [[1, 2], []],
        [{"id": 1}, {"id": 2, "name": "Ada"}],
    ]


@pytest.fixture
def delimiter_options() -> list[dict]:
    return [
        {"delimiter": ","},
        {"delimiter": "\t"},
        {"delimiter": "|"},
    ]


def assert_roundtrip(value: _t.Any, options: dict | None = None):
    s = encode(value, options or {})
    assert decode(s, options or {}) == value
    return s


def assert_no_trailing_spaces(encoded: str):
    for line in encoded.split("\n"):
        assert not line.endswith(" ")


def assert_no_trailing_newline(encoded: str):
    assert not encoded.endswith("\n")
