"""
Primitive value encoding and string handling for TOON format.

This module handles encoding of primitive values (null, bool, int, float, str)
and provides utilities for string quoting, escaping, and key validation.

Key Functions:
    - encode_primitive: Convert primitive values to TOON string representation
    - encode_string_literal: Quote and escape strings as needed
    - encode_key: Format object keys (quoted or unquoted)
    - is_safe_unquoted: Determine if string needs quoting
    - format_header: Generate array headers with length and field info

Quoting Rules:
    Strings are quoted if they:
    - Are empty or have leading/trailing whitespace
    - Match literals (true, false, null)
    - Contain structural characters (: [ ] { } - )
    - Contain delimiters or control characters
    - Look like numbers
"""

import re
from collections.abc import Sequence
from decimal import Decimal

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
from pytoon.logging_config import get_logger
from .types import Delimiter, JsonPrimitive


# Precompiled patterns
_STRUCTURAL_CHARS_PATTERN = re.compile(STRUCTURAL_CHARS_REGEX)
_CONTROL_CHARS_PATTERN = re.compile(CONTROL_CHARS_REGEX)
_NUMERIC_PATTERN = re.compile(NUMERIC_REGEX, re.IGNORECASE)
_OCTAL_PATTERN = re.compile(OCTAL_REGEX)
_VALID_KEY_PATTERN = re.compile(VALID_KEY_REGEX, re.IGNORECASE)


logger = get_logger(__name__)


def encode_primitive(value: JsonPrimitive, delimiter: Delimiter = COMMA) -> str:
    """Encode a primitive value to TOON string representation.

    Args:
        value: Primitive value (None, bool, int, float, or str).
        delimiter: Value delimiter for context-aware string quoting (default: ',').

    Returns:
        str: TOON-encoded string representation.

    Examples:
        >>> encode_primitive(None)
        'null'
        >>> encode_primitive(True)
        'true'
        >>> encode_primitive(42)
        '42'
        >>> encode_primitive(3.14)
        '3.14'
        >>> encode_primitive("hello")
        'hello'
        >>> encode_primitive("hello, world")  # Contains delimiter
        '"hello, world"'
    """
    if value is None:
        return NULL_LITERAL
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _format_float(value)
    return encode_string_literal(str(value), delimiter)


def encode_string_literal(value: str, delimiter: Delimiter = COMMA) -> str:
    """Encode a string value, quoting if necessary.

    Determines if string needs quoting based on content and delimiter.
    Quotes strings that contain special characters, delimiters, or
    look like literals/numbers.

    Args:
        value: String to encode.
        delimiter: Value delimiter for context-aware quoting (default: ',').

    Returns:
        str: Quoted string with escapes, or unquoted if safe.

    Examples:
        >>> encode_string_literal("hello")
        'hello'
        >>> encode_string_literal("hello world")
        'hello world'
        >>> encode_string_literal("true")  # Looks like literal
        '"true"'
        >>> encode_string_literal("key: value")  # Contains colon
        '"key: value"'
    """
    if is_safe_unquoted(value, delimiter):
        return value
    logger.debug("Quoting string literal for delimiter %r: %r", delimiter, value)
    return (
        f"{DOUBLE_QUOTE}{escape_string(value, delimiter, for_key=False)}{DOUBLE_QUOTE}"
    )


def escape_string(
    value: str, delimiter: Delimiter = COMMA, for_key: bool = False
) -> str:
    """Escape special characters in a string.

    Escapes backslash, double quote, newline, carriage return, and
    optionally tab (depending on delimiter and context).

    Args:
        value: String to escape.
        delimiter: Value delimiter (default: ',').
        for_key: If True, always escape tabs (default: False).

    Returns:
        str: Escaped string (without surrounding quotes).

    Note:
        Tabs are only escaped if delimiter is not tab, or if for_key is True.
    """
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


def is_safe_unquoted(value: str, delimiter: Delimiter = COMMA) -> bool:
    """Check if string can be safely represented without quotes.

    A string is safe unquoted if it:
    - Is non-empty and has no leading/trailing whitespace
    - Doesn't match literals (true, false, null)
    - Doesn't contain structural characters (: [ ] { } - )
    - Doesn't contain delimiters, quotes, or control characters
    - Doesn't look like a number

    Args:
        value: String to check.
        delimiter: Value delimiter for context-aware checking (default: ',').

    Returns:
        bool: True if string can be unquoted, False if quoting required.

    Examples:
        >>> is_safe_unquoted("hello")
        True
        >>> is_safe_unquoted("true")
        False
        >>> is_safe_unquoted("123")
        False
        >>> is_safe_unquoted("hello world")
        True
        >>> is_safe_unquoted(" hello")  # Leading space
        False
    """
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
    """Check if string looks like a number.

    Matches integers, floats, scientific notation, and octal-like strings.
    Used to determine if string needs quoting to avoid ambiguity.

    Args:
        value: String to check.

    Returns:
        bool: True if string matches numeric pattern.

    Examples:
        >>> is_numeric_like("123")
        True
        >>> is_numeric_like("3.14")
        True
        >>> is_numeric_like("1e10")
        True
        >>> is_numeric_like("05")  # Octal-like
        True
        >>> is_numeric_like("abc")
        False
    """
    # Octal-like strings such as 05 should be quoted
    return bool(_OCTAL_PATTERN.fullmatch(value)) or bool(
        _NUMERIC_PATTERN.fullmatch(value)
    )


def _format_float(value: float) -> str:
    """Format float value without trailing zeros.

    Uses Decimal for precise formatting, removes trailing zeros
    and decimal point if not needed.

    Args:
        value: Float value to format.

    Returns:
        str: Formatted float string.

    Examples:
        >>> _format_float(3.14)
        '3.14'
        >>> _format_float(3.0)
        '3'
        >>> _format_float(3.14000)
        '3.14'
    """
    decimal_value = Decimal(str(value))
    formatted = format(decimal_value, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    if not formatted:
        return "0"
    return formatted


def encode_key(key: str) -> str:
    """Encode an object key, quoting if necessary.

    Keys are unquoted if they match pattern: [A-Z_][\\w.]* (case-insensitive).
    Otherwise, keys are quoted and escaped.

    Args:
        key: Object key string.

    Returns:
        str: Quoted or unquoted key.

    Examples:
        >>> encode_key("name")
        'name'
        >>> encode_key("user_id")
        'user_id'
        >>> encode_key("first name")  # Contains space
        '"first name"'
        >>> encode_key("123")  # Starts with digit
        '"123"'
    """
    if is_valid_unquoted_key(key):
        return key
    return f"{DOUBLE_QUOTE}{escape_string(key, for_key=True)}{DOUBLE_QUOTE}"


def is_valid_unquoted_key(key: str) -> bool:
    """Check if key can be represented without quotes.

    Valid unquoted keys match: [A-Z_][\\w.]* (case-insensitive)
    - Start with letter or underscore
    - Contain only letters, digits, underscores, dots

    Args:
        key: Key string to check.

    Returns:
        bool: True if key can be unquoted.

    Examples:
        >>> is_valid_unquoted_key("name")
        True
        >>> is_valid_unquoted_key("user_id")
        True
        >>> is_valid_unquoted_key("user.name")
        True
        >>> is_valid_unquoted_key("123")
        False
        >>> is_valid_unquoted_key("first-name")
        False
    """
    return bool(_VALID_KEY_PATTERN.fullmatch(key))


def join_encoded_values(
    values: Sequence[JsonPrimitive], delimiter: Delimiter = COMMA
) -> str:
    """Join multiple primitive values with delimiter.

    Encodes each value and joins with the specified delimiter.
    Used for inline arrays and tabular rows.

    Args:
        values: Sequence of primitive values.
        delimiter: Value separator (default: ',').

    Returns:
        str: Delimiter-joined encoded values.

    Examples:
        >>> join_encoded_values([1, 2, 3])
        '1, 2, 3'
        >>> join_encoded_values(["a", "b", "c"], delimiter="|")
        'a| b| c'
    """
    return delimiter.join(encode_primitive(v, delimiter) for v in values)


def format_header(
    length: int,
    key: str | None = None,
    fields: list[str] | None = None,
    delimiter: Delimiter = COMMA,
    length_marker: bool = False,
) -> str:
    """Format an array header with length and optional fields.

    Generates TOON array headers in format:
    - Simple: [N]:
    - With key: key[N]:
    - With length marker: key[#N]:
    - With delimiter: key[N|]:
    - Tabular: key[N]{field1, field2}:

    Args:
        length: Array length.
        key: Optional key prefix.
        fields: Optional field names for tabular format.
        delimiter: Value delimiter (default: ',').
        length_marker: Include # prefix in length (default: False).

    Returns:
        str: Formatted array header ending with colon.

    Examples:
        >>> format_header(3)
        '[3]:'
        >>> format_header(3, key="items")
        'items[3]:'
        >>> format_header(3, key="items", length_marker=True)
        'items[#3]:'
        >>> format_header(2, key="users", fields=["id", "name"])
        'users[2]{id, name}:'
        >>> format_header(3, delimiter="|")  # Non-default delimiter
        '[3|]:'
    """
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
