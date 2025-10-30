import json
from pathlib import Path

import pytest

from pytoon import decode


_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "decoder_strictness.json"
with _FIXTURE_PATH.open("r", encoding="utf-8") as fh:
    _FIXTURES = json.load(fh)


@pytest.mark.parametrize(
    ("source", "expected"),
    [(case["source"], case["expected"]) for case in _FIXTURES["leadingZeroFixtures"]],
)
def test_preserves_leading_zero_tokens(source, expected):
    assert decode(source) == expected


def test_rejects_invalid_escape_sequence():
    with pytest.raises(ValueError):
        decode(_FIXTURES["invalidEscape"])


def test_rejects_blank_line_inside_array():
    with pytest.raises(ValueError):
        decode(_FIXTURES["blankLineInArray"])


def test_requires_space_after_list_marker():
    with pytest.raises(ValueError):
        decode(_FIXTURES["missingSpaceAfterHyphen"])


def test_rejects_tab_indentation():
    with pytest.raises(ValueError):
        decode(_FIXTURES["tabIndentedDoc"])
