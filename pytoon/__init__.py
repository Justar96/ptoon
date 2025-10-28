"""
Toon: Token-Oriented Object Notation for LLMs.

This package provides `encode()` to convert Python values into the TOON text
format optimized for LLM token efficiency, and `decode()` to parse TOON strings
back to Python values.
"""

from typing import Any

from .constants import DEFAULT_DELIMITER, DELIMITERS
from .decoder import Decoder
from .encoder import Encoder
from .types import JsonArray, JsonObject, JsonPrimitive, JsonValue


_default_encoder: Encoder | None = None
_default_decoder: Decoder | None = None


def encode(input: Any, options: dict | None = None) -> str:
    opts = options or {}
    indent = int(opts.get("indent", 2))
    delimiter = opts.get("delimiter", DEFAULT_DELIMITER)
    length_marker = bool(opts.get("length_marker", False))
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
    # options reserved for future use to align with encode signature
    if options is None:
        global _default_decoder
        if _default_decoder is None:
            _default_decoder = Decoder()
        return _default_decoder.decode(input)
    decoder = Decoder()
    return decoder.decode(input)


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
]
