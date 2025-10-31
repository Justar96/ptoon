from typing import Literal, TypedDict


JsonPrimitive = str | int | float | bool | None
JsonArray = list["JsonValue"]
JsonObject = dict[str, "JsonValue"]
JsonValue = JsonPrimitive | JsonArray | JsonObject

Depth = int
Delimiter = Literal[",", "|", "\t"]


class EncodeOptions(TypedDict, total=False):
    """Options for encoding Python values to TOON format.

    All fields are optional.

    Attributes:
        indent: Spaces per indentation level (must be non-negative).
        delimiter: Value separator - ',', '|', or '\\t'.
        length_marker: Include #N length markers in headers.
    """

    indent: int
    delimiter: Delimiter
    length_marker: bool
