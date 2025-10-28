from typing import Any

from .constants import DEFAULT_DELIMITER, LIST_ITEM_PREFIX
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
from .types import Depth, JsonArray, JsonObject, JsonValue
from .writer import LineWriter


class Encoder:
    def __init__(
        self,
        indent: int = 2,
        delimiter: str = DEFAULT_DELIMITER,
        length_marker: bool = False,
    ):
        self.indent = indent
        self.delimiter = delimiter
        self.length_marker = length_marker

    def encode(self, value: Any) -> str:
        normalized_value = normalize_value(value)
        return self._encode_value(normalized_value)

    def _encode_value(self, value: JsonValue) -> str:
        if is_json_primitive(value):
            return encode_primitive(value, self.delimiter)

        writer = LineWriter(self.indent)

        if is_json_array(value):
            self._encode_array(None, value, writer, 0)
        elif is_json_object(value):
            self._encode_object(value, writer, 0)

        return writer.to_string()

    def _encode_object(self, value: JsonObject, writer: LineWriter, depth: Depth):
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
            self._encode_inline_primitive_array(key, value, writer, depth)
            return

        if is_array_of_arrays(value):
            # The TS implementation has a special case for array of primitive arrays.
            if all(is_array_of_primitives(arr) for arr in value):
                self._encode_array_of_arrays_as_list_items(key, value, writer, depth)
                return

        if is_array_of_objects(value):
            header_fields = self._detect_tabular_header(value)
            if header_fields:
                self._encode_array_of_objects_as_tabular(
                    key, value, header_fields, writer, depth
                )
            else:
                self._encode_mixed_array_as_list_items(key, value, writer, depth)
            return

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
        joined_value = join_encoded_values(values, self.delimiter)
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
            inline = self._format_inline_array(arr, None)
            writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")

    def _detect_tabular_header(self, rows: JsonArray) -> list[str] | None:
        if not rows:
            return None
        # Use tabular format only when there are at least 2 rows
        if len(rows) < 2:
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
            values = [row[key] for key in header]
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
            elif is_json_array(item) and is_array_of_primitives(item):
                inline = self._format_inline_array(item, None)
                writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
            elif is_json_object(item):
                self._encode_object_as_list_item(item, writer, depth + 1)
            # Other complex nested arrays are intentionally not handled here per TS behavior.

    def _encode_object_as_list_item(
        self, obj: JsonObject, writer: LineWriter, depth: Depth
    ):
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
                        elif is_json_array(it) and is_array_of_primitives(it):
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
                    elif is_json_array(it) and is_array_of_primitives(it):
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
