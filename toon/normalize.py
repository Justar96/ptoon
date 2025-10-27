import datetime
import math
from collections.abc import Mapping
from typing import Any, List, Dict, Union
from .types import JsonPrimitive, JsonArray, JsonObject, JsonValue

def is_json_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))

def is_json_array(value: Any) -> bool:
    return isinstance(value, list)

def is_json_object(value: Any) -> bool:
    return isinstance(value, dict)

def is_array_of_primitives(value: JsonArray) -> bool:
    return all(is_json_primitive(item) for item in value)

def is_array_of_arrays(value: JsonArray) -> bool:
    return all(is_json_array(item) for item in value)

def is_array_of_objects(value: JsonArray) -> bool:
    return all(is_json_object(item) for item in value)

def normalize_value(value: Any) -> JsonValue:
    if value is None:
        return None

    if isinstance(value, (str, bool)):
        return value

    if isinstance(value, float):
        # Canonicalize -0.0 to 0
        if value == 0.0 and math.copysign(1.0, value) == -1.0:
            return 0
        # In Python, float('inf') and float('-inf') are valid, but not in JSON.
        # The TS implementation converts them to null.
        if value == float('inf') or value == float('-inf') or value != value:  # NaN check
            return None
        return value

    if isinstance(value, int):
        # Convert very large integers (beyond JS safe integer range) to string
        MAX_SAFE = 2**53 - 1
        if value < -MAX_SAFE or value > MAX_SAFE:
            return str(value)
        return value

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [normalize_value(item) for item in value]

    if isinstance(value, set):
        return [normalize_value(item) for item in sorted(list(value))] # Sorting to have a deterministic output

    # Handle generic mapping types (Map-like)
    if isinstance(value, Mapping) and not isinstance(value, dict):
        return {str(k): normalize_value(v) for k, v in value.items()}

    if isinstance(value, dict):
        if is_plain_object(value):
            return {str(k): normalize_value(v) for k, v in value.items()}
        # Treat dict subclasses as mapping-like
        return {str(k): normalize_value(v) for k, v in value.items()}

    # Fallback for other types (e.g. functions, custom objects) is to return None, similar to the TS version.
    return None

def is_plain_object(value: Any) -> bool:
    return isinstance(value, dict) and value.__class__ is dict
