JsonPrimitive = str | int | float | bool | None
JsonArray = list["JsonValue"]
JsonObject = dict[str, "JsonValue"]
JsonValue = JsonPrimitive | JsonArray | JsonObject

Depth = int
