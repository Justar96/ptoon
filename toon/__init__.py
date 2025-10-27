"""
Toon: Token-Oriented Object Notation for LLMs.

This package provides `encode()` to convert Python values into the TOON text
format optimized for LLM token efficiency, and `decode()` to parse TOON strings
back to Python values.
"""

from typing import Any

from .encoder import Encoder
from .decoder import Decoder
from .constants import DEFAULT_DELIMITER, DELIMITERS
from .types import JsonPrimitive, JsonArray, JsonObject, JsonValue

def encode(input: Any, options: dict | None = None) -> str:
    opts = options or {}
    indent = int(opts.get("indent", 2))
    delimiter = opts.get("delimiter", DEFAULT_DELIMITER)
    length_marker = bool(opts.get("length_marker", False))
    encoder = Encoder(indent=indent, delimiter=delimiter, length_marker=length_marker)
    return encoder.encode(input)

def decode(input: str, options: dict | None = None) -> JsonValue:
    # options reserved for future use to align with encode signature
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
