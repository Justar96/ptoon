from typing import Union


JsonPrimitive = Union[str, int, float, bool, None]
JsonArray = list["JsonValue"]
JsonObject = dict[str, "JsonValue"]
JsonValue = Union[JsonPrimitive, JsonArray, JsonObject]

Depth = int
