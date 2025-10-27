import re
from .types import JsonPrimitive
from .constants import (
    NULL_LITERAL, TRUE_LITERAL, FALSE_LITERAL,
    DOUBLE_QUOTE, BACKSLASH, COMMA, LIST_ITEM_MARKER, DEFAULT_DELIMITER
)

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
    return f'{DOUBLE_QUOTE}{escape_string(value, delimiter, for_key=False)}{DOUBLE_QUOTE}'

def escape_string(value: str, delimiter: str = COMMA, for_key: bool = False) -> str:
    s = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    # For values with tab delimiter active, keep literal tabs inside quoted strings
    if for_key or delimiter != '\t':
        s = s.replace('\t', '\\t')
    return s

def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    if not value:
        return False
    if value != value.strip(): # isPaddedWithWhitespace
        return False
    if value in [TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL]:
        return False
    if is_numeric_like(value):
        return False
    if ':' in value:
        return False
    if '"' in value or '\\' in value:
        return False
    if re.search(r'[\[\]{}]', value):
        return False
    if re.search(r'[\n\r\t]', value):
        return False
    if delimiter in value:
        return False
    if value.startswith(LIST_ITEM_MARKER):
        return False
    return True

def is_numeric_like(value: str) -> bool:
    # Match standard numeric patterns OR octal-like strings such as "05", "007" (must be quoted in TOON)
    return (
        bool(re.fullmatch(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', value, re.IGNORECASE))
        or bool(re.fullmatch(r'0\d+', value))
    )

def encode_key(key: str) -> str:
    if is_valid_unquoted_key(key):
        return key
    return f'{DOUBLE_QUOTE}{escape_string(key, for_key=True)}{DOUBLE_QUOTE}'

def is_valid_unquoted_key(key: str) -> bool:
    return bool(re.fullmatch(r'[A-Z_][\w.]*', key, re.IGNORECASE))

def join_encoded_values(values: list[JsonPrimitive], delimiter: str = COMMA) -> str:
    return delimiter.join(encode_primitive(v, delimiter) for v in values)

def format_header(
    length: int,
    key: str | None = None,
    fields: list[str] | None = None,
    delimiter: str = COMMA,
    length_marker: bool = False
) -> str:
    header = ''
    if key:
        header += encode_key(key)

    length_marker_str = '#' if length_marker else ''
    delimiter_str = delimiter if delimiter != DEFAULT_DELIMITER else ''
    header += f'[{length_marker_str}{length}{delimiter_str}]'

    if fields:
        quoted_fields = [encode_key(f) for f in fields]
        header += f'{{{delimiter.join(quoted_fields)}}}'

    header += ':'
    return header
