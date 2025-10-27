from typing import Union, List, Dict, Any

JsonPrimitive = Union[str, int, float, bool, None]
JsonArray = List['JsonValue']
JsonObject = Dict[str, 'JsonValue']
JsonValue = Union[JsonPrimitive, JsonArray, JsonObject]

Depth = int
