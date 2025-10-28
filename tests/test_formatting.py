from pytoon import encode


def test_produces_no_trailing_spaces_at_end_of_lines():
    data = {
        "user": {
            "name": "Ada",
            "items": [
                {"id": 1, "name": "x"},
                {"id": 2, "name": "y"},
            ],
            "tags": ["a", "b"],
        }
    }
    out = encode(data)
    for line in out.split("\n"):
        assert not line.endswith(" ")


def test_produces_no_trailing_newline_at_end_of_output():
    data = {"a": 1, "b": [1, 2], "c": {"x": "y"}}
    out = encode(data)
    assert not out.endswith("\n")
