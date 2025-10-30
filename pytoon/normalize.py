import datetime
import math
from collections.abc import Mapping
from typing import Any

from .types import JsonArray, JsonValue


_MAX_SAFE_INTEGER = 2**53 - 1


def is_json_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def is_json_array(value: Any) -> bool:
    return isinstance(value, list)


def is_json_object(value: Any) -> bool:
    return isinstance(value, dict)


def is_array_of_primitives(value: JsonArray) -> bool:
    if not value:
        return True
    return all(is_json_primitive(item) for item in value)


def is_array_of_arrays(value: JsonArray) -> bool:
    if not value:
        return True
    return all(is_json_array(item) for item in value)


def is_array_of_objects(value: JsonArray) -> bool:
    if not value:
        return True
    return all(is_json_object(item) for item in value)


def normalize_value(value: Any) -> JsonValue:
    if value is None:
        return None

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value

    if isinstance(value, int):
        # Convert very large integers (beyond JS safe integer range) to string
        if abs(value) > _MAX_SAFE_INTEGER:
            return str(value)
        return value

    if isinstance(value, float):
        # Handle non-finite first
        if not math.isfinite(value) or value != value:  # includes inf, -inf, NaN
            return None
        if value == 0.0 and math.copysign(1.0, value) == -1.0:
            return 0
        return value

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    if isinstance(value, list):
        if not value:
            return []
        return [normalize_value(item) for item in value]

    if isinstance(value, set):
        try:
            return [normalize_value(item) for item in sorted(value)]
        except TypeError:
            # Fall back to stable conversion for heterogeneous sets
            return [
                normalize_value(item) for item in sorted(value, key=lambda x: repr(x))
            ]

    # Handle generic mapping types (Map-like) and dicts
    if isinstance(value, Mapping):
        return {str(k): normalize_value(v) for k, v in value.items()}

    # Fallback for other types
    return None


# is_plain_object removed as unused after normalize refactor
