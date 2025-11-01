from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from ptoon.logging_config import get_logger

# Precompiled regex patterns
from .constants import (
    BACKSLASH,
    CLOSE_BRACE,
    CLOSE_BRACKET,
    COLON,
    DEFAULT_DELIMITER,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    HEADER_LENGTH_REGEX,
    INTEGER_REGEX,
    LIST_ITEM_MARKER,
    LIST_ITEM_PREFIX,
    NULL_LITERAL,
    NUMERIC_REGEX,
    OPEN_BRACE,
    OPEN_BRACKET,
    PIPE,
    TAB,
    TRUE_LITERAL,
    UNESCAPE_SEQUENCES,
)


if TYPE_CHECKING:
    from .types import Delimiter, JsonArray, JsonObject, JsonValue


_HEADER_LENGTH_PATTERN = re.compile(HEADER_LENGTH_REGEX)
_INTEGER_PATTERN = re.compile(INTEGER_REGEX)
_NUMBER_PATTERN = re.compile(NUMERIC_REGEX, re.IGNORECASE)

# Module logger
logger = get_logger(__name__)


class _Ctx:
    def __init__(self, kind: str, depth: int):
        self.kind = kind  # 'object' | 'array_list' | 'array_tabular'
        self.depth = depth  # header depth for this context
        self.content_depth = depth + 1  # where child lines are expected
        self.obj: JsonObject | None = None
        self.arr: JsonArray | None = None
        self.expected: int | None = None
        self.fields: list[str] | None = None
        self.delimiter: Delimiter = DEFAULT_DELIMITER
        self.from_list_item: bool = False


class Decoder:
    """TOON format decoder.

    Parses TOON-formatted strings back to Python values using a
    stack-based parser with context tracking.

    Parsing Strategy:

    - Line-by-line processing with depth tracking
    - Context stack maintains parsing state (object, array_list, array_tabular)
    - Automatic context unwinding on dedent
    - Length validation for arrays with markers

    Supported Formats:

    - Objects: key: value pairs
    - Inline arrays: [N]: val1, val2, val3
    - Tabular arrays: [N]{field1, field2} with aligned rows
    - List arrays: items prefixed with ``-`` on separate lines
    - Nested structures with proper indentation

    Examples:

        >>> decoder = Decoder()
        >>> decoder.decode('name: Alice\\nage: 30')
        {'name': 'Alice', 'age': 30}

        >>> decoder.decode('[2]{id, name}:\\n  1, Alice\\n  2, Bob')
        [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    """

    def __init__(self):
        pass

    def decode(self, toon_string: str) -> JsonValue:
        """Decode TOON string to Python value.

        Args:
            toon_string: TOON-formatted string.

        Returns:
            JsonValue: Decoded Python value (dict, list, or primitive). Empty or
            whitespace-only input returns an empty dict (``{}``).

        Raises:
            TypeError: If input is not a string.
            ValueError: If TOON syntax is invalid (see error messages for details).
        """
        # Input validation
        if not isinstance(toon_string, str):
            raise TypeError(f"Expected string input, got {type(toon_string).__name__}")

        text = toon_string.rstrip("\n")
        if not text.strip():
            return {}

        lines = text.splitlines()
        logger.debug(f"Decoding TOON string: {len(toon_string)} characters, {len(lines)} lines")
        indent_size = self._detect_indent_size(lines)

        stack: list[_Ctx] = []
        root: JsonValue | None = None
        line_num = 0

        for raw in lines:
            line_num += 1
            if not raw.strip():
                self._handle_blank_line(stack, line_num, raw)
                continue

            depth, content = self._calc_depth_and_content(raw, indent_size, line_num)
            logger.debug(f"Line {line_num}: depth={depth}, content={content[:50]}")

            # Close tabular arrays that completed before handling new line
            self._pop_completed_tabular(stack)

            # Unwind contexts on dedent
            while stack and depth < stack[-1].content_depth:
                ctx = stack[-1]
                if (
                    ctx.kind == "array_list"
                    and ctx.arr is not None
                    and ctx.expected is not None
                    and len(ctx.arr) != ctx.expected
                ):
                    raise self._err(
                        line_num,
                        (
                            f"array length mismatch at depth {ctx.depth}; "
                            f"expected {ctx.expected} items but found {len(ctx.arr)}"
                        ),
                        raw,
                        "Check list indentation and ensure the declared item count matches actual items.",
                    )
                logger.debug(f"Popping context: {self._get_context_description(ctx)}")
                stack.pop()
                self._pop_completed_tabular(stack)

            # Close completed list arrays when next token is not a list item
            while stack and stack[-1].kind == "array_list":
                top = stack[-1]
                if top.arr is not None and top.expected is not None:
                    if len(top.arr) < top.expected and not (
                        content.startswith(LIST_ITEM_PREFIX) or content.startswith(LIST_ITEM_MARKER)
                    ):
                        # Array not complete yet, but next token is not a list item
                        raise self._err(
                            line_num,
                            (
                                f"array length mismatch at depth {top.depth}; "
                                f"expected {top.expected} items but found {len(top.arr)}"
                            ),
                            raw,
                            "Add missing '- ' items or update the declared length marker.",
                        )
                    if len(top.arr) == top.expected and not (
                        content.startswith(LIST_ITEM_PREFIX) or content.startswith(LIST_ITEM_MARKER)
                    ):
                        stack.pop()
                        continue
                break

            if not stack:
                # Root line
                if content.startswith(OPEN_BRACKET):
                    # Root array header or inline
                    header, after = self._split_first_colon(content)
                    h = self._parse_header(header, line_num, raw)
                    logger.debug(
                        f"Parsing root array: length={h['length']}, fields={h['fields']}, delimiter={repr(h['delimiter'])}"
                    )
                    if h["fields"] is not None:
                        # tabular root
                        ctx = _Ctx("array_tabular", depth)
                        ctx.arr = []
                        ctx.expected = h["length"]
                        ctx.fields = h["fields"]
                        ctx.delimiter = h["delimiter"]
                        root = ctx.arr
                        stack.append(ctx)
                        continue
                    if after:
                        arr = self._parse_inline_array(h, after, line_num, raw)
                        root = arr
                    else:
                        ctx = _Ctx("array_list", depth)
                        ctx.arr = []
                        ctx.expected = h["length"]
                        ctx.delimiter = h["delimiter"]
                        root = ctx.arr
                        stack.append(ctx)
                    continue

                if self._looks_object_line(content):
                    logger.debug("Parsing root object")
                    root = {}
                    ctx = _Ctx("object", depth)
                    ctx.obj = root  # type: ignore
                    ctx.content_depth = depth  # root object keys are at the same depth
                    stack.append(ctx)
                    self._parse_object_line_into(ctx, content, depth, stack, line_num, raw)
                    continue

                # Primitive root
                logger.debug(f"Parsing primitive root: {content[:50]}")
                root = self._parse_primitive(content, line_num, raw)
                continue

            # Non-root line, route by current context
            top = stack[-1]
            if top.kind == "object" and depth == top.content_depth:
                logger.debug(f"Parsing object line: {content[:50]}")
                self._parse_object_line_into(top, content, depth, stack, line_num, raw)
                continue

            if top.kind == "array_list" and depth == top.content_depth:
                logger.debug(f"Parsing list item: {content[:50]}")
                self._parse_list_item_into(top, content, depth, stack, line_num, raw)
                # If list reached expected and next constructs are not items, we'll close on dedent later
                continue

            if top.kind == "array_tabular" and depth == top.content_depth:
                logger.debug(f"Parsing tabular row: {len(self._split_values(content, top.delimiter))} fields")
                self._parse_tabular_row_into(top, content, line_num, raw)
                self._pop_completed_tabular(stack)
                continue

            # If line depth equals a parent after popping completed tabular, try again
            while stack and depth < stack[-1].content_depth:
                ctx = stack[-1]
                if (
                    ctx.kind == "array_list"
                    and ctx.arr is not None
                    and ctx.expected is not None
                    and len(ctx.arr) != ctx.expected
                ):
                    raise self._err(
                        line_num,
                        (
                            f"array length mismatch at depth {ctx.depth}; "
                            f"expected {ctx.expected} items but found {len(ctx.arr)}"
                        ),
                        raw,
                        "Add missing list items or update the header length marker.",
                    )
                logger.debug(f"Popping context: {self._get_context_description(ctx)}")
                stack.pop()
            if stack:
                top = stack[-1]
                if top.kind == "object" and depth == top.content_depth:
                    self._parse_object_line_into(top, content, depth, stack, line_num, raw)
                    continue
                if top.kind == "array_list" and depth == top.content_depth:
                    self._parse_list_item_into(top, content, depth, stack, line_num, raw)
                    continue
                if top.kind == "array_tabular" and depth == top.content_depth:
                    self._parse_tabular_row_into(top, content, line_num, raw)
                    self._pop_completed_tabular(stack)
                    continue

            raise self._err(
                line_num,
                (
                    f"unexpected content at depth {depth}; "
                    f"current context is {self._get_context_description(stack[-1]) if stack else 'root'}"
                ),
                raw,
                "Adjust indentation or ensure the line belongs to the current structure.",
            )

        # Finalize: ensure any open tabular arrays completed
        self._pop_completed_tabular(stack)

        # Validate remaining array_list contexts have correct length
        for ctx in stack:
            if (
                ctx.kind == "array_list"
                and ctx.arr is not None
                and ctx.expected is not None
                and len(ctx.arr) != ctx.expected
            ):
                raise self._err(
                    line_num,
                    (
                        f"array length mismatch at depth {ctx.depth}; "
                        f"expected {ctx.expected} items but found {len(ctx.arr)} "
                        "by end of input"
                    ),
                    "",
                    "Add missing '- ' items or reduce the declared length marker.",
                )

        return root

    def _get_context_description(self, ctx: _Ctx) -> str:
        """Get human-readable description of context.

        Args:
            ctx: Context object.

        Returns:
            str: Description like "object with 3 keys" or "array_list with 2/5 items".
        """
        if ctx.kind == "object" and ctx.obj is not None:
            keys = list(ctx.obj.keys())[:3]
            key_str = f" ({', '.join(keys)}...)" if len(keys) > 0 else ""
            return f"object with {len(ctx.obj)} keys{key_str}"
        elif ctx.kind == "array_list" and ctx.arr is not None:
            expected_str = f"/{ctx.expected}" if ctx.expected is not None else ""
            return f"array_list with {len(ctx.arr)}{expected_str} items"
        elif ctx.kind == "array_tabular" and ctx.arr is not None:
            expected_str = f"/{ctx.expected}" if ctx.expected is not None else ""
            field_str = f" [{', '.join(ctx.fields)}]" if ctx.fields else ""
            return f"array_tabular with {len(ctx.arr)}{expected_str} rows{field_str}"
        return ctx.kind

    def _err(
        self,
        line_num: int,
        detail: str,
        line: str,
        hint: str | None = None,
    ) -> ValueError:
        """Build a detailed ValueError with context snippet and hint."""

        def _format_snippet(raw: str) -> str:
            trimmed = raw.rstrip("\n")
            snippet = trimmed.strip()
            if not snippet:
                snippet = trimmed
            snippet = snippet.replace("\t", "\\t")
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            return repr(snippet) if snippet else "''"

        message = f"Line {line_num}: {detail}. Snippet: {_format_snippet(line)}"
        if hint:
            message = f"{message} Hint: {hint}"
        else:
            message = f"{message} Hint: Check TOON syntax and indentation near this line."
        return ValueError(message)

    # Helpers
    def _detect_indent_size(self, lines: list[str]) -> int:
        """Detect indentation size from lines.

        Finds minimum non-zero leading space count.

        Args:
            lines: Lines to analyze.

        Returns:
            int: Detected indent size (default: 2 if no indentation found).
        """
        indents: list[int] = []
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            leading = self._count_leading_spaces(line, idx)
            if leading > 0:
                indents.append(leading)
        if not indents:
            return 2
        detected = min(indents)
        logger.debug(f"Detected indent size: {detected} spaces")
        return detected

    def _calc_depth_and_content(self, line: str, indent_size: int, line_num: int) -> tuple[int, str]:
        leading = self._count_leading_spaces(line, line_num)
        if leading % max(indent_size, 1) != 0:
            raise self._err(
                line_num,
                (f"invalid indentation; expected a multiple of {indent_size} spaces but found {leading}"),
                line,
                "Adjust indentation to consistent space multiples (2 or 4 spaces).",
            )
        depth = leading // max(indent_size, 1)
        return depth, line[leading:]

    def _count_leading_spaces(self, line: str, line_num: int | None = None) -> int:
        count = 0
        for ch in line:
            if ch == " ":
                count += 1
                continue
            if ch == "\t":
                raise self._err(
                    line_num if line_num is not None else 0,
                    "tab character found in indentation",
                    line,
                    "Replace tabs with spaces (2 or 4 spaces recommended).",
                )
            break
        return count

    def _split_first_colon(self, s: str) -> tuple[str, str]:
        i = self._find_colon_index(s)
        if i == -1:
            return s, ""
        return s[:i].rstrip(), s[i + 1 :].lstrip()

    def _find_colon_index(self, s: str) -> int:
        in_quotes = False
        esc = False
        b = 0
        c = 0
        for i, ch in enumerate(s):
            if esc:
                esc = False
                continue
            if ch == BACKSLASH:
                esc = True
                continue
            if ch == DOUBLE_QUOTE:
                in_quotes = not in_quotes
                continue
            if in_quotes:
                continue
            if ch == OPEN_BRACKET:
                b += 1
                continue
            if ch == CLOSE_BRACKET and b > 0:
                b -= 1
                continue
            if ch == OPEN_BRACE:
                c += 1
                continue
            if ch == CLOSE_BRACE and c > 0:
                c -= 1
                continue
            if ch == COLON and b == 0 and c == 0:
                return i
        return -1

    def _looks_object_line(self, content: str) -> bool:
        return self._find_colon_index(content) != -1

    def _looks_header_token(self, left: str) -> bool:
        """
        Returns True if left contains '[' outside quotes that pairs with ']' before any '{...}' suffix.
        Scans with quote/escape awareness to avoid misfiring on quoted keys containing '['.
        """
        in_quotes = False
        esc = False
        found_open_bracket = False
        found_close_bracket = False

        for ch in left:
            if esc:
                esc = False
                continue
            if ch == BACKSLASH:
                esc = True
                continue
            if ch == DOUBLE_QUOTE:
                in_quotes = not in_quotes
                continue
            if in_quotes:
                continue
            # Now we're outside quotes
            if ch == OPEN_BRACKET:
                found_open_bracket = True
                continue
            if found_open_bracket and ch == CLOSE_BRACKET:
                found_close_bracket = True
                break
            if ch == OPEN_BRACE:
                # Found '{' before ']', not a valid header token
                break

        return found_open_bracket and found_close_bracket

    def _parse_header(self, header: str, line_num: int, line: str) -> dict:
        """Parse array header to extract metadata.

        Header format: key?[#]N[delimiter]?][{fields}]

        Args:
            header: Header string (without colon).
            line_num: Current input line number for error reporting.
            line: Full line content for snippet reporting.

        Returns:
            dict: Parsed header with keys: key, length, fields, delimiter, has_length_marker.

        Raises:
            ValueError: If header format is invalid.
        """
        # header like: key?[#]N[delimiter]?][{fields}] (no colon)
        s = header.strip()
        key: str | None = None
        idx_open = s.find(OPEN_BRACKET)
        if idx_open == -1:
            raise self._err(
                line_num,
                "invalid array header: missing '[' before length block",
                line,
                "Use format key[N]: or [N]: with brackets around the length.",
            )
        key_part = s[:idx_open].rstrip()
        rest = s[idx_open + 1 :]

        if key_part:
            try:
                key = self._parse_key_token(key_part)
            except ValueError as exc:
                raise self._err(
                    line_num,
                    f"invalid header key: {exc}",
                    line,
                    "Quote or escape the key before the array header.",
                ) from exc

        idx_close = rest.find(CLOSE_BRACKET)
        if idx_close == -1:
            raise self._err(
                line_num,
                "invalid array header: missing closing ']' after length",
                line,
                "Ensure the array header closes with ] before any fields or colon.",
            )
        inside = rest[:idx_close]
        after_bracket = rest[idx_close + 1 :]

        has_len_marker = False
        delim = DEFAULT_DELIMITER
        m = _HEADER_LENGTH_PATTERN.fullmatch(inside)
        if not m:
            raise self._err(
                line_num,
                ("invalid array header length block; expected N or #N with optional delimiter (, |, \\t)"),
                line,
                "Declare the array length as [3], [#3], [3|], or [3\\t].",
            )
        if inside.startswith("#"):
            has_len_marker = True
        length = int(m.group(1))
        if m.group(2):
            delim = TAB if m.group(2) == "\t" else PIPE

        fields: list[str] | None = None
        after_bracket = after_bracket.strip()
        if after_bracket:
            if not after_bracket.startswith(OPEN_BRACE):
                raise self._err(
                    line_num,
                    "invalid array header suffix; expected '{fields}'",
                    line,
                    "Place field names inside braces immediately after ].",
                )
            # Parse fields in {...}
            if not after_bracket.endswith(CLOSE_BRACE):
                raise self._err(
                    line_num,
                    "invalid array header suffix; missing closing '}'",
                    line,
                    "Close the field list with a matching } brace.",
                )
            brace_content = after_bracket[1:-1]
            fields = []
            for tok in self._split_values(brace_content, delim):
                try:
                    fields.append(self._parse_key_token(tok.strip()))
                except ValueError as exc:
                    raise self._err(
                        line_num,
                        f"invalid field name in header: {exc}",
                        line,
                        "Quote field names containing spaces or escapes in { }.",
                    ) from exc

        result = {
            "key": key,
            "length": length,
            "fields": fields,
            "delimiter": delim,
            "has_length_marker": has_len_marker,
        }
        logger.debug(
            f"Parsed header: key={result['key']}, length={result['length']}, fields={result['fields']}, delimiter={repr(result['delimiter'])}"
        )
        return result

    def _parse_inline_array(self, header: dict, values_str: str, line_num: int, line: str) -> JsonArray:
        if not values_str.strip():
            if header["length"] == 0:
                return []
            else:
                raise self._err(
                    line_num,
                    (f"inline array length mismatch; expected {header['length']} values but found 0"),
                    line,
                    "Add the missing comma-separated values after the colon.",
                )
        parts = self._split_values(values_str, header["delimiter"])
        arr: list[JsonValue] = []
        for part in parts:
            arr.append(self._parse_primitive(part, line_num, line))
        if header["length"] != len(arr):
            raise self._err(
                line_num,
                (f"inline array length mismatch; expected {header['length']} values but found {len(arr)}"),
                line,
                "Update the header count or add the missing values.",
            )
        return arr

    def _parse_object_line_into(
        self,
        ctx: _Ctx,
        content: str,
        depth: int,
        stack: list[_Ctx],
        line_num: int,
        raw_line: str,
    ):
        assert ctx.kind == "object" and ctx.obj is not None
        left, right = self._split_first_colon(content)
        if self._looks_header_token(left):
            h = self._parse_header(left, line_num, raw_line)
            if not h["key"]:
                raise self._err(
                    line_num,
                    "array header inside object must include a key prefix",
                    raw_line,
                    "Use key[N]: form with a key name before brackets.",
                )
            key = h["key"]
            if h["fields"] is not None:
                if right:
                    raise self._err(
                        line_num,
                        "tabular array header cannot include inline values",
                        raw_line,
                        "Place tabular rows on indented lines after the header.",
                    )
                ctx.obj[key] = []
                arr_ctx = _Ctx("array_tabular", depth)
                arr_ctx.arr = ctx.obj[key]  # type: ignore
                arr_ctx.expected = h["length"]
                arr_ctx.fields = h["fields"]
                arr_ctx.delimiter = h["delimiter"]
                arr_ctx.content_depth = depth + 1
                stack.append(arr_ctx)
                return
            # list or inline primitive array
            if right:
                ctx.obj[key] = self._parse_inline_array(h, right, line_num, raw_line)
                return
            ctx.obj[key] = []
            arr_ctx = _Ctx("array_list", depth)
            arr_ctx.arr = ctx.obj[key]  # type: ignore
            arr_ctx.expected = h["length"]
            arr_ctx.delimiter = h["delimiter"]
            arr_ctx.content_depth = depth + 1
            stack.append(arr_ctx)
            return

        idx = self._find_colon_index(content)
        if idx == -1:
            raise self._err(
                line_num,
                "invalid object entry; expected 'key: value'",
                raw_line,
                "Add a colon between the key and value, e.g. name: Alice.",
            )
        key_token = content[:idx].strip()
        if not key_token:
            raise self._err(
                line_num,
                "invalid object entry; missing key before ':'",
                raw_line,
                "Provide a key before the colon.",
            )
        try:
            key = self._parse_key_token(key_token)
        except ValueError as exc:
            raise self._err(
                line_num,
                f"invalid object key: {exc}",
                raw_line,
                'Quote keys with spaces or escape sequences, e.g. "name value".',
            ) from exc
        value = content[idx + 1 :].lstrip()

        if value == "":
            obj: JsonObject = {}
            ctx.obj[key] = obj
            child = _Ctx("object", depth)
            child.obj = obj
            # Nested objects on hyphen line (first field of list item) indent by two levels
            # All other nested objects indent by one level
            child.content_depth = (depth + 2) if (ctx.from_list_item and depth == ctx.depth) else (depth + 1)
            child.from_list_item = False  # Don't propagate flag to child contexts
            stack.append(child)
            return
        if value.startswith(OPEN_BRACKET):
            header, after = self._split_first_colon(value)
            h = self._parse_header(header, line_num, raw_line)
            ctx.obj[key] = self._parse_inline_array(h, after, line_num, raw_line)
            return

        if self._find_colon_index(value) != -1 and value[0] != DOUBLE_QUOTE:
            # nested object inline: key: subkey: value
            nested_ctx = _Ctx("object", depth + 1)
            nested_obj: JsonObject = {}
            nested_ctx.obj = nested_obj
            nested_ctx.content_depth = depth + 1
            nested_ctx.from_list_item = False
            ctx.obj[key] = nested_obj
            stack.append(nested_ctx)
            self._parse_object_line_into(nested_ctx, value, depth + 1, stack, line_num, value)
            return
        ctx.obj[key] = self._parse_primitive(value, line_num, value)

    def _parse_list_item_into(
        self,
        ctx: _Ctx,
        content: str,
        depth: int,
        stack: list[_Ctx],
        line_num: int,
        raw_line: str,
    ):
        assert ctx.kind == "array_list" and ctx.arr is not None
        if not content.startswith(LIST_ITEM_PREFIX):
            raise self._err(
                line_num,
                f"list item must start with '- ' at depth {depth}",
                raw_line,
                "Prefix array list entries with '- ' followed by the value.",
            )
        rest = content[len(LIST_ITEM_PREFIX) :].strip()

        # Empty object item
        if rest == "":
            ctx.arr.append({})
            return

        # Inline array item: - [N...]: values
        if rest.startswith(OPEN_BRACKET):
            header, after = self._split_first_colon(rest)
            h = self._parse_header(header, line_num, raw_line)
            arr = self._parse_inline_array(h, after, line_num, raw_line)
            ctx.arr.append(arr)
            return

        # Object item: parse first field on hyphen line
        if self._find_colon_index(rest) != -1:
            obj: JsonObject = {}
            ctx.arr.append(obj)
            obj_ctx = _Ctx("object", depth)
            obj_ctx.obj = obj
            obj_ctx.content_depth = depth + 1
            obj_ctx.from_list_item = True
            stack.append(obj_ctx)
            self._parse_object_line_into(obj_ctx, rest, depth, stack, line_num, rest)
            return

        # Primitive item
        ctx.arr.append(self._parse_primitive(rest, line_num, rest))

    def _parse_tabular_row_into(self, ctx: _Ctx, content: str, line_num: int, raw_line: str):
        assert ctx.kind == "array_tabular" and ctx.arr is not None and ctx.fields is not None
        parts = self._split_values(content, ctx.delimiter)
        if len(parts) != len(ctx.fields):
            raise self._err(
                line_num,
                (f"tabular row field count mismatch; expected {len(ctx.fields)} fields but found {len(parts)}"),
                raw_line,
                "Check delimiter usage and ensure each row has values for all fields.",
            )
        row: dict[str, JsonValue] = {}
        for k, v in zip(ctx.fields, parts, strict=False):
            row[k] = self._parse_primitive(v, line_num, v)
        ctx.arr.append(row)

    def _pop_completed_tabular(self, stack: list[_Ctx]):
        while stack and stack[-1].kind == "array_tabular":
            top = stack[-1]
            if top.arr is None or top.expected is None:
                break
            if len(top.arr) >= top.expected:
                stack.pop()
            else:
                break

    # Primitive parsing
    def _parse_primitive(self, s: str, line_num: int, raw_line: str) -> Any:
        """Parse primitive value from string.

        Handles: null, true, false, numbers (int/float), quoted strings, unquoted strings.

        Args:
            s: String to parse.

        Returns:
            Any: Parsed primitive value.
        """
        t = s.strip()
        try:
            if t == NULL_LITERAL:
                result = None
            elif t == TRUE_LITERAL:
                result = True
            elif t == FALSE_LITERAL:
                result = False
            elif self._is_quoted(t):
                result = self._unquote_string(t)
            elif self._is_number_like(t):
                if self._has_forbidden_leading_zeros(t):
                    result = t
                # try int first, then float
                elif _INTEGER_PATTERN.fullmatch(t):
                    try:
                        result = int(t)
                    except ValueError:
                        result = t
                else:
                    try:
                        result = float(t)
                    except ValueError:
                        result = t
            else:
                result = t
        except ValueError as exc:
            detail = str(exc) or "invalid primitive literal"
            raise self._err(
                line_num,
                detail,
                raw_line,
                "Check escapes and quote strings that contain special characters.",
            ) from exc
        logger.debug(f"Parsing primitive: {s[:50]} -> {result}")
        return result

    def _is_quoted(self, s: str) -> bool:
        return len(s) >= 2 and s[0] == DOUBLE_QUOTE and s[-1] == DOUBLE_QUOTE

    def _unquote_string(self, s: str) -> str:
        assert self._is_quoted(s)
        inner = s[1:-1]
        out = []
        esc = False
        for ch in inner:
            if esc:
                mapped = UNESCAPE_SEQUENCES.get(ch)
                if mapped is None:
                    raise ValueError(
                        f'Invalid escape sequence: \\{ch}. Valid escapes are: \\n, \\r, \\t, \\", \\\\. In string: {s[:50]}'
                    )
                out.append(mapped)
                esc = False
                continue
            if ch == BACKSLASH:
                esc = True
                continue
            out.append(ch)
        if esc:
            raise ValueError(
                f'Unclosed escape sequence at end of string: {s[:50]}. Backslash must be followed by n, r, t, ", or \\'
            )
        return "".join(out)

    def _is_number_like(self, s: str) -> bool:
        return bool(_NUMBER_PATTERN.fullmatch(s))

    def _has_forbidden_leading_zeros(self, s: str) -> bool:
        if not s:
            return False
        negative = s[0] == "-"
        body = s[1:] if negative else s
        if not body or not body[0].isdigit():
            return False
        if "." in body or "e" in body or "E" in body:
            return False
        return len(body) > 1 and body[0] == "0"

    def _parse_key_token(self, token: str) -> str:
        t = token.strip()
        if self._is_quoted(t):
            return self._unquote_string(t)
        return t

    def _split_values(self, s: str, delimiter: Delimiter) -> list[str]:
        """Split delimited values respecting quotes and escapes.

        Args:
            s: String to split.
            delimiter: Delimiter character(s).

        Returns:
            list[str]: Split and trimmed values.
        """
        if s == "":
            return []
        # Fast path when there are no quotes or escapes
        if '"' not in s and "\\" not in s:
            return [part.strip() for part in s.split(delimiter)]
        parts: list[str] = []
        buf: list[str] = []
        in_quotes = False
        esc = False
        i = 0
        delim_len = len(delimiter)
        while i < len(s):
            ch = s[i]
            if esc:
                buf.append(ch)
                esc = False
                i += 1
                continue
            if ch == BACKSLASH:
                buf.append(ch)
                esc = True
                i += 1
                continue
            if ch == DOUBLE_QUOTE:
                buf.append(ch)
                in_quotes = not in_quotes
                i += 1
                continue
            if not in_quotes and self._at_delimiter(s, i, delimiter):
                parts.append("".join(buf).strip())
                buf = []
                i += delim_len
                continue
            buf.append(ch)
            i += 1
        parts.append("".join(buf).strip())
        return parts

    def _at_delimiter(self, s: str, i: int, delimiter: Delimiter) -> bool:
        if len(delimiter) == 1:
            return i < len(s) and s[i] == delimiter
        return s[i : i + len(delimiter)] == delimiter

    def _handle_blank_line(self, stack: list[_Ctx], line_num: int, line: str):
        for ctx in reversed(stack):
            if ctx.kind in ("array_list", "array_tabular"):
                depth = ctx.content_depth
                parts: list[str] = []
                if ctx.arr is not None:
                    if ctx.expected is not None:
                        parts.append(f"array has {len(ctx.arr)}/{ctx.expected} items")
                    else:
                        parts.append(f"array has {len(ctx.arr)} items")
                detail = f"Blank line encountered within array contents at depth {depth}"
                if parts:
                    detail = f"{detail}; {'; '.join(parts)}"
                raise self._err(
                    line_num,
                    detail,
                    line,
                    "Remove blank lines inside arrays; arrays must be contiguous without empty lines.",
                )
