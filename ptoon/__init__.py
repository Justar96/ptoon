"""
Toon: Token-Oriented Object Notation for LLMs.

This package provides `encode()` to convert Python values into the TOON text
format optimized for LLM token efficiency, and `decode()` to parse TOON strings
back to Python values.

TOON achieves 30-60% token savings compared to JSON for structured data,
particularly effective for:
- Arrays of uniform objects (tabular data)
- Nested structures with repeated keys
- Large datasets sent to LLM APIs

Token analysis utilities (`count_tokens`, `estimate_savings`, `compare_formats`)
help measure and compare token efficiency between JSON and TOON formats.

Quick Start:
    >>> import ptoon
    >>> data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    >>> toon_str = ptoon.encode(data)
    >>> print(toon_str)
    users[2]{id, name}:
      1, Alice
      2, Bob
    >>> ptoon.decode(toon_str)
    {'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}

Debug Mode:
    Enable detailed logging with environment variable:
    $ PTOON_DEBUG=1 python your_script.py

See Also:
    - SPEC.md: Complete format specification
    - examples/: Integration examples with OpenAI, Anthropic, etc.
    - README.md: Installation and usage guide
"""

import types as stdlib_types
from typing import Any

from .constants import DEFAULT_DELIMITER, DELIMITERS
from .decoder import Decoder
from .encoder import Encoder
from .types import (
    Delimiter,
    EncodeOptions,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
)


_default_encoder: Encoder | None = None
_default_decoder: Decoder | None = None


def encode(input: Any, options: EncodeOptions | dict | None = None) -> str:
    """Encode Python values to TOON format.

    Converts Python dicts, lists, and primitives into TOON (Token-Oriented
    Object Notation) format, optimized for LLM token efficiency.

    Args:
        input: Python value to encode. Supports:
            - Primitives: None, bool, int, float, str
            - Collections: dict, list
            - Special types: datetime (converted to ISO string), set (converted to sorted list)
            - Nested structures of the above
        options: Optional encoding configuration (EncodeOptions TypedDict or dict) with keys:
            - indent (int): Spaces per indentation level (default: 2)
            - delimiter (str): Value separator - ',', '|', or '\\t' (default: ',')
            - length_marker (bool): Include #N length markers in headers (default: False)

    Returns:
        str: TOON-formatted string representation of the input.

    Raises:
        TypeError: If input contains non-serializable types (functions, classes, modules)
                   or if options is not a dict.
        ValueError: If input contains circular references, invalid structures,
                    or invalid option values.

    Examples:
        >>> import ptoon
        >>> ptoon.encode({"name": "Alice", "age": 30})
        'name: Alice\\nage: 30'

        >>> ptoon.encode([{"id": 1}, {"id": 2}])
        '[2]{id}:\\n  1\\n  2'

        >>> ptoon.encode({"users": ["Alice", "Bob"]}, options={"delimiter": "|"})
        'users[2|]: Alice| Bob'

    Note:
        - Non-finite floats (inf, -inf, NaN) are converted to null
        - Large integers (>2^53-1) are converted to strings
        - Sets are converted to sorted lists
        - Datetime objects are converted to ISO format strings
        - Enable debug logging with PTOON_DEBUG=1 environment variable

    See Also:
        decode: Parse TOON strings back to Python values
        estimate_savings: Compare token efficiency vs JSON
    """
    # Input validation
    if isinstance(input, stdlib_types.ModuleType):
        raise TypeError(
            f"Cannot encode {type(input).__name__}: TOON supports dicts, lists, and primitives."
        )
    if isinstance(input, type):
        raise TypeError(
            f"Cannot encode {type(input).__name__}: TOON supports dicts, lists, and primitives."
        )
    if isinstance(
        input,
        (
            stdlib_types.FunctionType,
            stdlib_types.MethodType,
            stdlib_types.BuiltinFunctionType,
        ),
    ):
        raise TypeError(
            f"Cannot encode {type(input).__name__}: TOON supports dicts, lists, and primitives."
        )

    if options is not None and not isinstance(options, dict):
        raise TypeError(f"options must be a dict, got {type(options).__name__}")

    if options:
        valid_keys = {"indent", "delimiter", "length_marker"}
        invalid = set(options.keys()) - valid_keys
        if invalid:
            raise ValueError(
                "options contains unsupported keys; allowed: "
                f"{sorted(valid_keys)}; got: {sorted(invalid)}"
            )
        if "delimiter" in options:
            delimiter_option = options["delimiter"]
            accepted = [DEFAULT_DELIMITER, "|", "\t"]
            if delimiter_option not in accepted:
                raise ValueError(
                    "delimiter must be one of ',', '|' or '\\t'; "
                    f"got: {repr(delimiter_option)}"
                )

    opts = options or {}

    # Validate and extract indent
    indent_val = opts.get("indent", 2)
    if (
        isinstance(indent_val, bool)
        or not isinstance(indent_val, int)
        or indent_val < 0
    ):
        raise ValueError(
            f"indent must be a non-negative int; got: {indent_val!r}"
        )
    indent = indent_val

    delimiter = opts.get("delimiter", DEFAULT_DELIMITER)

    # Validate and extract length_marker
    length_marker_val = opts.get("length_marker", False)
    if not isinstance(length_marker_val, bool):
        raise ValueError(
            f"length_marker must be a bool; got: {length_marker_val!r}"
        )
    length_marker = length_marker_val
    if options is None or (
        indent == 2 and delimiter == DEFAULT_DELIMITER and not length_marker
    ):
        global _default_encoder
        if _default_encoder is None:
            _default_encoder = Encoder(
                indent=2, delimiter=DEFAULT_DELIMITER, length_marker=False
            )
        return _default_encoder.encode(input)
    encoder = Encoder(indent=indent, delimiter=delimiter, length_marker=length_marker)
    return encoder.encode(input)


def decode(input: str, options: dict | None = None) -> JsonValue:
    """Decode TOON format strings to Python values.

    Parses TOON (Token-Oriented Object Notation) format strings back into
    Python dicts, lists, and primitives.

    Args:
        input: TOON-formatted string to decode.
        options: Reserved for future use (currently unused).

    Returns:
        JsonValue: Decoded Python value. Can be:

            - Primitives: None, bool, int, float, str
            - Collections: dict, list
            - Nested structures of the above

        For empty or whitespace-only input strings, an empty dict ({}) is returned.

    Raises:
        TypeError: If input is not a string or if options is not a dict.
        ValueError: If input contains invalid TOON syntax:
            - Invalid indentation (must be consistent spaces, no tabs)
            - Mismatched array lengths (declared vs actual)
            - Invalid headers or delimiters
            - Malformed escape sequences
            - Unexpected structure or nesting

    Examples:
        >>> import ptoon
        >>> ptoon.decode('name: Alice\\nage: 30')
        {'name': 'Alice', 'age': 30}

        >>> ptoon.decode('[2]{id}:\\n  1\\n  2')
        [{'id': 1}, {'id': 2}]

        >>> ptoon.decode('[3]: Alice, Bob, Carol')
        ['Alice', 'Bob', 'Carol']

    Note:
        - Empty or whitespace-only input returns an empty dict ({})
        - Indentation must be consistent (2 or 4 spaces recommended)
        - Tabs are not allowed for indentation
        - Blank lines are only allowed between top-level structures
        - Array length markers (#N) are validated if present
        - Enable debug logging with PTOON_DEBUG=1 environment variable

    See Also:
        encode: Convert Python values to TOON format
        SPEC.md: Full TOON format specification
    """
    # Input validation
    if not isinstance(input, str):
        raise TypeError(
            f"decode() expects a string, got {type(input).__name__}. Use encode() to convert Python values to TOON."
        )
    if options is not None and not isinstance(options, dict):
        raise TypeError(f"options must be a dict, got {type(options).__name__}")

    # options reserved for future use to align with encode signature
    if options is None:
        global _default_decoder
        if _default_decoder is None:
            _default_decoder = Decoder()
        return _default_decoder.decode(input)
    decoder = Decoder()
    return decoder.decode(input)


# Import utilities after defining encode/decode to avoid circular imports
from .utils import compare_formats, count_tokens, estimate_savings  # noqa: E402


__all__ = [
    # API
    "encode",
    "decode",
    # Constants
    "DEFAULT_DELIMITER",
    "DELIMITERS",
    # Types
    "JsonPrimitive",
    "JsonArray",
    "JsonObject",
    "JsonValue",
    "Delimiter",
    "EncodeOptions",
    # Utils
    "count_tokens",
    "estimate_savings",
    "compare_formats",
]
