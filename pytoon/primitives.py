import re

from .constants import (
    BACKSLASH,
    COMMA,
    CONTROL_CHARS_REGEX,
    DEFAULT_DELIMITER,
    DOUBLE_QUOTE,
    ESCAPE_SEQUENCES,
    FALSE_LITERAL,
    LIST_ITEM_MARKER,
    NULL_LITERAL,
    NUMERIC_REGEX,
    OCTAL_REGEX,
    STRUCTURAL_CHARS_REGEX,
    TRUE_LITERAL,
    VALID_KEY_REGEX,
)
from .types import JsonPrimitive


# Precompiled patterns
_STRUCTURAL_CHARS_PATTERN = re.compile(STRUCTURAL_CHARS_REGEX)
_CONTROL_CHARS_PATTERN = re.compile(CONTROL_CHARS_REGEX)
_NUMERIC_PATTERN = re.compile(NUMERIC_REGEX, re.IGNORECASE)
_OCTAL_PATTERN = re.compile(OCTAL_REGEX)
_VALID_KEY_PATTERN = re.compile(VALID_KEY_REGEX, re.IGNORECASE)


def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    if value is None:
        return NULL_LITERAL
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    return encode_string_literal(str(value), delimiter)


def encode_string_literal(value: str, delimiter: str = COMMA) -> str:
    if is_safe_unquoted(value, delimiter):
        return value
    return (
        f"{DOUBLE_QUOTE}{escape_string(value, delimiter, for_key=False)}{DOUBLE_QUOTE}"
    )


def escape_string(value: str, delimiter: str = COMMA, for_key: bool = False) -> str:
    # Single-pass escaping to reduce allocations
    out: list[str] = []
    escape_tab = for_key or (delimiter != "\t")
    for ch in value:
        if ch == BACKSLASH:
            out.append(ESCAPE_SEQUENCES[BACKSLASH])
        elif ch == '"':
            out.append(ESCAPE_SEQUENCES[DOUBLE_QUOTE])
        elif ch == "\n":
            out.append(ESCAPE_SEQUENCES["\n"])
        elif ch == "\r":
            out.append(ESCAPE_SEQUENCES["\r"])
        elif ch == "\t" and escape_tab:
            out.append(ESCAPE_SEQUENCES["\t"])
        else:
            out.append(ch)
    return "".join(out)


def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    if not value:
        return False
    if value != value.strip():
        return False
    if value in (TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL):
        return False
    if ":" in value:
        return False
    if '"' in value or "\\" in value:
        return False
    if delimiter in value:
        return False
    if value.startswith(LIST_ITEM_MARKER):
        return False
    if _STRUCTURAL_CHARS_PATTERN.search(value):
        return False
    if _CONTROL_CHARS_PATTERN.search(value):
        return False
    return not is_numeric_like(value)


def is_numeric_like(value: str) -> bool:
    # Octal-like strings such as 05 should be quoted
    return bool(_OCTAL_PATTERN.fullmatch(value)) or bool(
        _NUMERIC_PATTERN.fullmatch(value)
    )


def encode_key(key: str) -> str:
    if is_valid_unquoted_key(key):
        return key
    return f"{DOUBLE_QUOTE}{escape_string(key, for_key=True)}{DOUBLE_QUOTE}"


def is_valid_unquoted_key(key: str) -> bool:
    return bool(_VALID_KEY_PATTERN.fullmatch(key))


def join_encoded_values(values: list[JsonPrimitive], delimiter: str = COMMA) -> str:
    return delimiter.join(encode_primitive(v, delimiter) for v in values)


def format_header(
    length: int,
    key: str | None = None,
    fields: list[str] | None = None,
    delimiter: str = COMMA,
    length_marker: bool = False,
) -> str:
    header = ""
    if key:
        header += encode_key(key)

    length_marker_str = "#" if length_marker else ""
    delimiter_str = delimiter if delimiter != DEFAULT_DELIMITER else ""
    header += f"[{length_marker_str}{length}{delimiter_str}]"

    if fields:
        quoted_fields = [encode_key(f) for f in fields]
        header += f"{{{delimiter.join(quoted_fields)}}}"

    header += ":"
    return header
