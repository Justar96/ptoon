import types
from typing import Any, cast

from .constants import DEFAULT_DELIMITER, LIST_ITEM_PREFIX
from ptoon.logging_config import get_logger
from .normalize import (
    is_array_of_arrays,
    is_array_of_objects,
    is_array_of_primitives,
    is_json_array,
    is_json_object,
    is_json_primitive,
    normalize_value,
)
from .primitives import encode_key, encode_primitive, format_header, join_encoded_values
from .types import Delimiter, Depth, JsonArray, JsonObject, JsonPrimitive, JsonValue
from .writer import LineWriter


# Module logger
logger = get_logger(__name__)


class Encoder:
    """TOON format encoder.

    Converts normalized JSON values to TOON string representation.
    Supports multiple output formats:

    - Inline arrays for primitives: [N]: val1, val2, val3
    - Tabular format for uniform objects: [N]{field1, field2}
    - List format for mixed content: hyphen-prefixed items

    Attributes:

        indent: Spaces per indentation level (default: 2).
        delimiter: Value separator - ',', '|', or '\t' (default: ',').
        length_marker: Include #N in array headers (default: False).

    Examples:
        >>> encoder = Encoder(indent=2, delimiter=",")
        >>> encoder.encode({"name": "Alice", "age": 30})
        'name: Alice\\nage: 30'

        >>> encoder = Encoder(delimiter="|", length_marker=True)
        >>> encoder.encode([1, 2, 3])
        '[#3|]: 1| 2| 3'
    """

    def __init__(
        self,
        indent: int = 2,
        delimiter: Delimiter = DEFAULT_DELIMITER,
        length_marker: bool = False,
    ):
        self.indent = indent
        self.delimiter: Delimiter = delimiter
        self.length_marker = length_marker

    def encode(self, value: Any) -> str:
        """Encode a value to TOON format.

        Args:
            value: Python value to encode (will be normalized).

        Returns:
            str: TOON-formatted string.

        Raises:
            TypeError: If value contains non-serializable types.
            ValueError: If value contains circular references.
        """
        # Input validation
        if isinstance(value, types.ModuleType):
            raise TypeError(
                f"Cannot encode {type(value).__name__}: TOON supports dicts, lists, and primitives."
            )
        if isinstance(value, type):
            raise TypeError(
                f"Cannot encode {type(value).__name__}: TOON supports dicts, lists, and primitives."
            )
        if isinstance(
            value, (types.FunctionType, types.MethodType, types.BuiltinFunctionType)
        ):
            raise TypeError(
                f"Cannot encode {type(value).__name__}: TOON supports dicts, lists, and primitives."
            )

        try:
            normalized_value = normalize_value(value)
        except RecursionError as e:
            raise ValueError(
                "Detected circular reference during normalization/encoding. Ensure input structures are acyclic."
            ) from e
        except (TypeError, ValueError) as e:
            raise type(e)(
                f"Failed to normalize input of type {type(value).__name__}: {str(e)}. Ensure all values are JSON-compatible."
            ) from e

        logger.debug(
            f"Normalized input: type={type(normalized_value).__name__}, size={self._estimate_size(normalized_value)}"
        )
        result = self._encode_value(normalized_value)
        logger.debug(f"Encoded to {len(result)} characters")
        return result

    def _encode_value(self, value: JsonValue) -> str:
        if is_json_primitive(value):
            logger.debug(f"Encoding primitive: {value}")
            return encode_primitive(value, self.delimiter)

        writer = LineWriter(self.indent)

        if is_json_array(value):
            logger.debug(
                f"Encoding root array: length={len(value)}, type={self._detect_array_type(value)}"
            )
            self._encode_array(None, value, writer, 0)
        elif is_json_object(value):
            logger.debug(f"Encoding root object: {len(value)} keys")
            self._encode_object(value, writer, 0)

        return writer.to_string()

    def _encode_object(self, value: JsonObject, writer: LineWriter, depth: Depth):
        # Validate object keys
        for key in value:
            if not isinstance(key, str):
                raise TypeError(
                    f"Object keys must be strings, got {type(key).__name__}: {key}. Convert non-string keys to strings before encoding."
                )

        for key, item in value.items():
            self._encode_key_value_pair(key, item, writer, depth)

    def _encode_key_value_pair(
        self, key: str, value: JsonValue, writer: LineWriter, depth: Depth
    ):
        encoded_key = encode_key(key)

        if is_json_primitive(value):
            writer.push(
                depth, f"{encoded_key}: {encode_primitive(value, self.delimiter)}"
            )
        elif is_json_array(value):
            self._encode_array(key, value, writer, depth)
        elif is_json_object(value):
            if not value:
                writer.push(depth, f"{encoded_key}:")
            else:
                writer.push(depth, f"{encoded_key}:")
                self._encode_object(value, writer, depth + 1)

    def _encode_array(
        self, key: str | None, value: JsonArray, writer: LineWriter, depth: Depth
    ):
        if not value:
            header = format_header(
                0, key=key, delimiter=self.delimiter, length_marker=self.length_marker
            )
            writer.push(depth, header)
            return

        if is_array_of_primitives(value):
            logger.debug(f"Encoding inline primitive array: {len(value)} items")
            self._encode_inline_primitive_array(key, value, writer, depth)
            return

        if is_array_of_arrays(value):
            # Check if all nested arrays are primitive arrays
            all_primitive_arrays = all(
                is_json_array(arr) and is_array_of_primitives(arr) for arr in value
            )
            if all_primitive_arrays:
                # Special case for array of primitive arrays: encode each array as a list item
                self._encode_array_of_arrays_as_list_items(key, value, writer, depth)
                return

        if is_array_of_objects(value):
            header_fields = self._detect_tabular_header(value)
            if header_fields:
                logger.debug(
                    f"Detected tabular array: {len(value)} rows, {len(header_fields)} columns: {header_fields}"
                )
                self._encode_array_of_objects_as_tabular(
                    key, value, header_fields, writer, depth
                )
            else:
                logger.debug(
                    "Array not tabular (mixed types or <2 rows), using list format"
                )
                self._encode_mixed_array_as_list_items(key, value, writer, depth)
            return

        logger.debug(f"Encoding mixed array as list items: {len(value)} items")
        self._encode_mixed_array_as_list_items(key, value, writer, depth)

    def _encode_inline_primitive_array(
        self, prefix: str | None, values: JsonArray, writer: LineWriter, depth: Depth
    ):
        formatted = self._format_inline_array(values, prefix)
        writer.push(depth, formatted)

    def _format_inline_array(self, values: JsonArray, prefix: str | None) -> str:
        header = format_header(
            len(values),
            key=prefix,
            delimiter=self.delimiter,
            length_marker=self.length_marker,
        )
        # Cast to JsonPrimitive sequence - values are validated as primitives by caller
        joined_value = join_encoded_values(
            cast(list[JsonPrimitive], values), self.delimiter
        )
        return f"{header} {joined_value}" if values else header

    def _encode_array_of_arrays_as_list_items(
        self, prefix: str | None, values: JsonArray, writer: LineWriter, depth: Depth
    ):
        header = format_header(
            len(values),
            key=prefix,
            delimiter=self.delimiter,
            length_marker=self.length_marker,
        )
        writer.push(depth, header)
        for arr in values:
            # Type guard: validated as array of arrays by caller
            if is_json_array(arr):
                inline = self._format_inline_array(arr, None)
                writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")

    def _detect_tabular_header(self, rows: JsonArray) -> list[str] | None:
        """Detect if array of objects can use tabular format.

        Tabular format requires:
        - At least 2 rows
        - All rows are objects with identical keys
        - All values are primitives

        Args:
            rows: Array to check.

        Returns:
            list[str] | None: Field names if tabular, None otherwise.
        """
        if not rows:
            return None
        # Use tabular format only when there are at least 2 rows
        if len(rows) < 2:
            logger.debug(
                f"Checking if array is tabular: {len(rows)} rows (need at least 2)"
            )
            return None
        first_row = rows[0]
        if not isinstance(first_row, dict) or not first_row:
            return None

        first_keys = list(first_row.keys())
        if not first_keys:
            return None
        first_keys_len = len(first_keys)

        if self._is_tabular_array(rows, first_keys, first_keys_len):
            return first_keys
        logger.debug("Not tabular: rows have different keys or non-primitive values")
        return None

    def _is_tabular_array(
        self, rows: JsonArray, header: list[str], header_len: int
    ) -> bool:
        for row in rows:
            if not isinstance(row, dict):
                return False
            if len(row) != header_len:
                return False
            if not all(key in row and is_json_primitive(row[key]) for key in header):
                return False
        return True

    def _encode_array_of_objects_as_tabular(
        self,
        prefix: str | None,
        rows: JsonArray,
        header: list[str],
        writer: LineWriter,
        depth: Depth,
    ):
        header_str = format_header(
            len(rows),
            key=prefix,
            fields=header,
            delimiter=self.delimiter,
            length_marker=self.length_marker,
        )
        writer.push(depth, header_str)
        self._write_tabular_rows(rows, header, writer, depth + 1)

    def _write_tabular_rows(
        self, rows: JsonArray, header: list[str], writer: LineWriter, depth: Depth
    ):
        for row in rows:
            # Type guard: rows validated as array of objects with primitive values
            assert is_json_object(row), "Row must be an object in tabular format"
            values = [cast(JsonPrimitive, row[key]) for key in header]
            joined_value = join_encoded_values(values, self.delimiter)
            writer.push(depth, joined_value)

    def _encode_mixed_array_as_list_items(
        self, prefix: str | None, items: JsonArray, writer: LineWriter, depth: Depth
    ):
        header = format_header(
            len(items),
            key=prefix,
            delimiter=self.delimiter,
            length_marker=self.length_marker,
        )
        writer.push(depth, header)

        for item in items:
            if is_json_primitive(item):
                writer.push(
                    depth + 1,
                    f"{LIST_ITEM_PREFIX}{encode_primitive(item, self.delimiter)}",
                )
            elif is_json_array(item):
                if is_array_of_primitives(item):
                    inline = self._format_inline_array(item, None)
                    writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
                else:
                    # Complex nested array (e.g., array of arrays of arrays)
                    nesting_depth = self._calculate_nesting_depth(item)
                    if nesting_depth >= 2:
                        logger.warning(
                            f"Skipping deeply nested array (depth {nesting_depth + 1}). "
                            f"TOON format supports up to 2 levels of array nesting. "
                            f"Consider flattening this data structure."
                        )
            elif is_json_object(item):
                self._encode_object_as_list_item(item, writer, depth + 1)
            # Other complex nested arrays are intentionally not handled here per TS behavior.

    def _encode_object_as_list_item(
        self, obj: JsonObject, writer: LineWriter, depth: Depth
    ):
        """Encode object as list item with first field on hyphen line.

        TOON format places first key-value pair on same line as '- ' prefix,
        with remaining fields indented below.

        Args:
            obj: Object to encode.
            writer: Line writer for output.
            depth: Current indentation depth.
        """
        if not obj:
            writer.push(depth, LIST_ITEM_PREFIX)
            return

        keys = list(obj.keys())
        first_key = keys[0]
        first_value = obj[first_key]

        # First key-value on the same line as "- "
        encoded_key = encode_key(first_key)

        if is_json_primitive(first_value):
            writer.push(
                depth,
                f"{LIST_ITEM_PREFIX}{encoded_key}: {encode_primitive(first_value, self.delimiter)}",
            )
        elif is_json_array(first_value):
            if is_array_of_primitives(first_value):
                formatted = self._format_inline_array(first_value, first_key)
                writer.push(depth, f"{LIST_ITEM_PREFIX}{formatted}")
            elif is_array_of_objects(first_value):
                header_fields = self._detect_tabular_header(first_value)
                if header_fields:
                    header_str = format_header(
                        len(first_value),
                        key=first_key,
                        fields=header_fields,
                        delimiter=self.delimiter,
                        length_marker=self.length_marker,
                    )
                    writer.push(depth, f"{LIST_ITEM_PREFIX}{header_str}")
                    # Rows under a list item's first field should be indented two levels
                    self._write_tabular_rows(
                        first_value, header_fields, writer, depth + 2
                    )
                else:
                    # Complex array of objects (non-tabular): write header and encode each object as list item
                    header = format_header(
                        len(first_value),
                        key=first_key,
                        delimiter=self.delimiter,
                        length_marker=self.length_marker,
                    )
                    writer.push(depth, f"{LIST_ITEM_PREFIX}{header}")
                    for it in first_value:
                        if is_json_object(it):
                            self._encode_object_as_list_item(it, writer, depth + 2)
                        elif is_json_array(it):
                            if is_array_of_primitives(it):
                                inline = self._format_inline_array(it, None)
                                writer.push(depth + 2, f"{LIST_ITEM_PREFIX}{inline}")
                        elif is_json_primitive(it):
                            writer.push(
                                depth + 2,
                                f"{LIST_ITEM_PREFIX}{encode_primitive(it, self.delimiter)}",
                            )
            else:  # other complex arrays
                # Write header with key and length on the hyphen line, then encode supported item types
                header = format_header(
                    len(first_value),
                    key=first_key,
                    delimiter=self.delimiter,
                    length_marker=self.length_marker,
                )
                writer.push(depth, f"{LIST_ITEM_PREFIX}{header}")
                for it in first_value:
                    if is_json_primitive(it):
                        writer.push(
                            depth + 2,
                            f"{LIST_ITEM_PREFIX}{encode_primitive(it, self.delimiter)}",
                        )
                    elif is_json_array(it):
                        if is_array_of_primitives(it):
                            inline = self._format_inline_array(it, None)
                            writer.push(depth + 2, f"{LIST_ITEM_PREFIX}{inline}")
                    elif is_json_object(it):
                        self._encode_object_as_list_item(it, writer, depth + 2)

        elif is_json_object(first_value):
            if not first_value:
                writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_key}:")
            else:
                writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_key}:")
                # Nested object content under list item's first field indents by two levels
                self._encode_object(first_value, writer, depth + 2)

        # Remaining keys on indented lines
        for key in keys[1:]:
            self._encode_key_value_pair(key, obj[key], writer, depth + 1)

    def _estimate_size(self, value: JsonValue) -> str:
        """Return human-readable size estimate for logging.

        Args:
            value: Value to estimate size of.

        Returns:
            str: Size description like "5 keys" or "10 items" or "primitive".
        """
        if is_json_object(value):
            return f"{len(value)} keys"
        elif is_json_array(value):
            return f"{len(value)} items"
        else:
            return "primitive"

    def _detect_array_type(self, value: JsonArray) -> str:
        """Return array type description for logging.

        Args:
            value: Array to analyze.

        Returns:
            str: Type description like "empty", "primitives", "objects (tabular)", etc.
        """
        if not value:
            return "empty"
        if is_array_of_primitives(value):
            return "primitives"
        if is_array_of_objects(value):
            if self._detect_tabular_header(value):
                return "objects (tabular)"
            return "objects (mixed)"
        if is_array_of_arrays(value):
            return "arrays"
        return "mixed"

    def _calculate_nesting_depth(self, arr: JsonArray) -> int:
        """Calculate maximum array nesting depth.

        Args:
            arr: Array to analyze.

        Returns:
            int: Maximum nesting depth (1 for flat array, 2 for array of arrays, etc.).

        Examples:
            [1, 2, 3] → 1
            [[1, 2], [3, 4]] → 2
            [[[1]]] → 3
            [[1], [[[2]]]] → 4 (mixed depth, returns max)
        """
        if not is_json_array(arr):
            return 0
        if not arr:
            return 1

        max_depth = 1
        for item in arr:
            if is_json_array(item):
                max_depth = max(max_depth, 1 + self._calculate_nesting_depth(item))

        return max_depth
