from __future__ import annotations

import re
from typing import Any, Optional, List, Dict

from .types import JsonValue, JsonObject, JsonArray
from .constants import (
    LIST_ITEM_PREFIX,
    LIST_ITEM_MARKER,
    COMMA,
    COLON,
    SPACE,
    PIPE,
    OPEN_BRACKET,
    CLOSE_BRACKET,
    OPEN_BRACE,
    CLOSE_BRACE,
    NULL_LITERAL,
    TRUE_LITERAL,
    FALSE_LITERAL,
    BACKSLASH,
    DOUBLE_QUOTE,
    TAB,
    DEFAULT_DELIMITER,
)


class _Ctx:
    def __init__(self, kind: str, depth: int):
        self.kind = kind  # 'object' | 'array_list' | 'array_tabular'
        self.depth = depth  # header depth for this context
        self.content_depth = depth + 1  # where child lines are expected
        self.obj: Optional[JsonObject] = None
        self.arr: Optional[JsonArray] = None
        self.expected: Optional[int] = None
        self.fields: Optional[list[str]] = None
        self.delimiter: str = DEFAULT_DELIMITER
        self.from_list_item: bool = False


class Decoder:
    def __init__(self):
        pass

    def decode(self, toon_string: str) -> JsonValue:
        text = toon_string.rstrip("\n")
        if not text.strip():
            return {}

        lines = text.splitlines()
        indent_size = self._detect_indent_size(lines)

        stack: list[_Ctx] = []
        root: Optional[JsonValue] = None

        for raw in lines:
            if not raw.strip():
                continue

            depth, content = self._calc_depth_and_content(raw, indent_size)

            # Close tabular arrays that completed before handling new line
            self._pop_completed_tabular(stack)

            # Unwind contexts on dedent
            while stack and depth < stack[-1].content_depth:
                ctx = stack[-1]
                if ctx.kind == 'array_list' and ctx.arr is not None and ctx.expected is not None:
                    if len(ctx.arr) != ctx.expected:
                        raise ValueError(f"Array length mismatch: expected {ctx.expected}, got {len(ctx.arr)}")
                stack.pop()
                self._pop_completed_tabular(stack)

            # Close completed list arrays when next token is not a list item
            while stack and stack[-1].kind == 'array_list':
                top = stack[-1]
                if top.arr is not None and top.expected is not None:
                    if len(top.arr) < top.expected:
                        # Array not complete yet, but next token is not a list item
                        if not (content.startswith(LIST_ITEM_PREFIX) or content.startswith(LIST_ITEM_MARKER)):
                            raise ValueError(f"Array length mismatch: expected {top.expected}, got {len(top.arr)}")
                    if len(top.arr) == top.expected:
                        if not (content.startswith(LIST_ITEM_PREFIX) or content.startswith(LIST_ITEM_MARKER)):
                            stack.pop()
                            continue
                break

            if not stack:
                # Root line
                if content.startswith(OPEN_BRACKET):
                    # Root array header or inline
                    header, after = self._split_first_colon(content)
                    h = self._parse_header(header)
                    if h['fields'] is not None:
                        # tabular root
                        ctx = _Ctx('array_tabular', depth)
                        ctx.arr = []
                        ctx.expected = h['length']
                        ctx.fields = h['fields']
                        ctx.delimiter = h['delimiter']
                        root = ctx.arr
                        stack.append(ctx)
                        continue
                    if after:
                        arr = self._parse_inline_array(h, after)
                        root = arr
                    else:
                        ctx = _Ctx('array_list', depth)
                        ctx.arr = []
                        ctx.expected = h['length']
                        ctx.delimiter = h['delimiter']
                        root = ctx.arr
                        stack.append(ctx)
                    continue

                if self._looks_object_line(content):
                    root = {}
                    ctx = _Ctx('object', depth)
                    ctx.obj = root  # type: ignore
                    ctx.content_depth = depth  # root object keys are at the same depth
                    stack.append(ctx)
                    self._parse_object_line_into(ctx, content, depth, stack)
                    continue

                # Primitive root
                root = self._parse_primitive(content)
                continue

            # Non-root line, route by current context
            top = stack[-1]
            if top.kind == 'object' and depth == top.content_depth:
                self._parse_object_line_into(top, content, depth, stack)
                continue

            if top.kind == 'array_list' and depth == top.content_depth:
                self._parse_list_item_into(top, content, depth, stack)
                # If list reached expected and next constructs are not items, we'll close on dedent later
                continue

            if top.kind == 'array_tabular' and depth == top.content_depth:
                self._parse_tabular_row_into(top, content)
                self._pop_completed_tabular(stack)
                continue

            # If line depth equals a parent after popping completed tabular, try again
            while stack and depth < stack[-1].content_depth:
                ctx = stack[-1]
                if ctx.kind == 'array_list' and ctx.arr is not None and ctx.expected is not None:
                    if len(ctx.arr) != ctx.expected:
                        raise ValueError(f"Array length mismatch: expected {ctx.expected}, got {len(ctx.arr)}")
                stack.pop()
            if stack:
                top = stack[-1]
                if top.kind == 'object' and depth == top.content_depth:
                    self._parse_object_line_into(top, content, depth, stack)
                    continue
                if top.kind == 'array_list' and depth == top.content_depth:
                    self._parse_list_item_into(top, content, depth, stack)
                    continue
                if top.kind == 'array_tabular' and depth == top.content_depth:
                    self._parse_tabular_row_into(top, content)
                    self._pop_completed_tabular(stack)
                    continue

            raise ValueError(f"Unexpected line at depth {depth}: {content}")

        # Finalize: ensure any open tabular arrays completed
        self._pop_completed_tabular(stack)

        # Validate remaining array_list contexts have correct length
        for ctx in stack:
            if ctx.kind == 'array_list' and ctx.arr is not None and ctx.expected is not None:
                if len(ctx.arr) != ctx.expected:
                    raise ValueError(f"Array length mismatch: expected {ctx.expected}, got {len(ctx.arr)}")

        return root

    # Helpers
    def _detect_indent_size(self, lines: list[str]) -> int:
        indents = [len(l) - len(l.lstrip(' ')) for l in lines if l and l[0] == ' ']
        indents = [i for i in indents if i > 0]
        if not indents:
            return 2
        return min(indents)

    def _calc_depth_and_content(self, line: str, indent_size: int) -> tuple[int, str]:
        leading = len(line) - len(line.lstrip(' '))
        if leading % max(indent_size, 1) != 0:
            raise ValueError("Invalid indentation")
        depth = leading // max(indent_size, 1)
        return depth, line[leading:]

    def _split_first_colon(self, s: str) -> tuple[str, str]:
        i = self._find_colon_index(s)
        if i == -1:
            return s, ''
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

    def _parse_header(self, header: str) -> dict:
        # header like: key?[#]N[delimiter]?][{fields}] (no colon)
        s = header.strip()
        key: Optional[str] = None
        idx_open = s.find(OPEN_BRACKET)
        if idx_open == -1:
            raise ValueError("Invalid array header: missing [")
        key_part = s[:idx_open].rstrip()
        rest = s[idx_open + 1 :]

        if key_part:
            key = self._parse_key_token(key_part)

        idx_close = rest.find(CLOSE_BRACKET)
        if idx_close == -1:
            raise ValueError("Invalid array header: missing ]")
        inside = rest[:idx_close]
        after_bracket = rest[idx_close + 1 :]

        has_len_marker = False
        delim = DEFAULT_DELIMITER
        m = re.fullmatch(r"#?(\d+)([\|\t])?", inside)
        if not m:
            raise ValueError("Invalid array header length block")
        if inside.startswith('#'):
            has_len_marker = True
        length = int(m.group(1))
        if m.group(2):
            delim = TAB if m.group(2) == '\t' else PIPE

        fields: Optional[list[str]] = None
        after_bracket = after_bracket.strip()
        if after_bracket:
            if not after_bracket.startswith(OPEN_BRACE):
                raise ValueError("Invalid array header: unexpected suffix")
            # Parse fields in {...}
            if not after_bracket.endswith(CLOSE_BRACE):
                raise ValueError("Invalid array header: missing }")
            brace_content = after_bracket[1:-1]
            fields = [self._parse_key_token(tok.strip()) for tok in self._split_values(brace_content, delim)]

        return {
            'key': key,
            'length': length,
            'fields': fields,
            'delimiter': delim,
            'has_length_marker': has_len_marker,
        }

    def _parse_inline_array(self, header: dict, values_str: str) -> JsonArray:
        if not values_str.strip():
            if header['length'] == 0:
                return []
            else:
                raise ValueError("Array length mismatch")
        parts = self._split_values(values_str, header['delimiter'])
        arr = [self._parse_primitive(p) for p in parts]
        if header['length'] != len(arr):
            raise ValueError("Array length mismatch")
        return arr

    def _parse_object_line_into(self, ctx: _Ctx, content: str, depth: int, stack: list[_Ctx]):
        assert ctx.kind == 'object' and ctx.obj is not None
        left, right = self._split_first_colon(content)
        if self._looks_header_token(left):
            h = self._parse_header(left)
            if not h['key']:
                raise ValueError("Array header in object must include a key")
            key = h['key']
            if h['fields'] is not None:
                if right:
                    raise ValueError("Tabular header should not have inline values")
                ctx.obj[key] = []
                arr_ctx = _Ctx('array_tabular', depth)
                arr_ctx.arr = ctx.obj[key]  # type: ignore
                arr_ctx.expected = h['length']
                arr_ctx.fields = h['fields']
                arr_ctx.delimiter = h['delimiter']
                arr_ctx.content_depth = depth + 1
                stack.append(arr_ctx)
                return
            # list or inline primitive array
            if right:
                ctx.obj[key] = self._parse_inline_array(h, right)
                return
            ctx.obj[key] = []
            arr_ctx = _Ctx('array_list', depth)
            arr_ctx.arr = ctx.obj[key]  # type: ignore
            arr_ctx.expected = h['length']
            arr_ctx.delimiter = h['delimiter']
            arr_ctx.content_depth = depth + 1
            stack.append(arr_ctx)
            return

        key = self._parse_key_token(left)
        if right == '':
            obj: JsonObject = {}
            ctx.obj[key] = obj
            child = _Ctx('object', depth)
            child.obj = obj
            child.content_depth = (depth + 2) if ctx.from_list_item else (depth + 1)
            child.from_list_item = ctx.from_list_item
            stack.append(child)
            return
        ctx.obj[key] = self._parse_primitive(right)

    def _parse_list_item_into(self, ctx: _Ctx, content: str, depth: int, stack: list[_Ctx]):
        assert ctx.kind == 'array_list' and ctx.arr is not None
        if not content.startswith(LIST_ITEM_PREFIX) and not content.startswith(LIST_ITEM_MARKER):
            raise ValueError("Expected list item")
        rest = content[1:].lstrip() if content.startswith(LIST_ITEM_MARKER) else content[len(LIST_ITEM_PREFIX):]
        rest = rest.strip()

        # Empty object item
        if rest == '':
            ctx.arr.append({})
            return

        # Inline array item: - [N...]: values
        if rest.startswith(OPEN_BRACKET):
            header, after = self._split_first_colon(rest)
            h = self._parse_header(header)
            arr = self._parse_inline_array(h, after)
            ctx.arr.append(arr)
            return

        # Object item: parse first field on hyphen line
        if self._find_colon_index(rest) != -1:
            obj: JsonObject = {}
            ctx.arr.append(obj)
            obj_ctx = _Ctx('object', depth)
            obj_ctx.obj = obj
            obj_ctx.content_depth = depth + 1
            obj_ctx.from_list_item = True
            stack.append(obj_ctx)
            self._parse_object_line_into(obj_ctx, rest, depth, stack)
            return

        # Primitive item
        ctx.arr.append(self._parse_primitive(rest))

    def _parse_tabular_row_into(self, ctx: _Ctx, content: str):
        assert ctx.kind == 'array_tabular' and ctx.arr is not None and ctx.fields is not None
        parts = self._split_values(content, ctx.delimiter)
        if len(parts) != len(ctx.fields):
            raise ValueError("Tabular row field count mismatch")
        row: Dict[str, JsonValue] = {}
        for k, v in zip(ctx.fields, parts):
            row[k] = self._parse_primitive(v)
        ctx.arr.append(row)

    def _pop_completed_tabular(self, stack: list[_Ctx]):
        while stack and stack[-1].kind == 'array_tabular':
            top = stack[-1]
            if top.arr is None or top.expected is None:
                break
            if len(top.arr) >= top.expected:
                stack.pop()
            else:
                break

    # Primitive parsing
    def _parse_primitive(self, s: str) -> Any:
        t = s.strip()
        if t == NULL_LITERAL:
            return None
        if t == TRUE_LITERAL:
            return True
        if t == FALSE_LITERAL:
            return False
        if self._is_quoted(t):
            return self._unquote_string(t)
        if self._is_number_like(t):
            # try int first, then float
            if re.fullmatch(r'-?\d+', t):
                try:
                    return int(t)
                except ValueError:
                    pass
            try:
                return float(t)
            except ValueError:
                pass
        return t

    def _is_quoted(self, s: str) -> bool:
        return len(s) >= 2 and s[0] == DOUBLE_QUOTE and s[-1] == DOUBLE_QUOTE

    def _unquote_string(self, s: str) -> str:
        assert self._is_quoted(s)
        inner = s[1:-1]
        out = []
        esc = False
        for ch in inner:
            if esc:
                if ch == 'n':
                    out.append('\n')
                elif ch == 'r':
                    out.append('\r')
                elif ch == 't':
                    out.append('\t')
                else:
                    out.append(ch)
                esc = False
                continue
            if ch == BACKSLASH:
                esc = True
                continue
            out.append(ch)
        if esc:
            raise ValueError("Unclosed escape sequence")
        return ''.join(out)

    def _is_number_like(self, s: str) -> bool:
        return bool(re.fullmatch(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', s, re.IGNORECASE))

    def _parse_key_token(self, token: str) -> str:
        t = token.strip()
        if self._is_quoted(t):
            return self._unquote_string(t)
        return t

    def _split_values(self, s: str, delimiter: str) -> list[str]:
        if s == '':
            return []
        parts: list[str] = []
        buf: list[str] = []
        in_quotes = False
        esc = False
        i = 0
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
                parts.append(''.join(buf).strip())
                buf = []
                i += len(delimiter)
                continue
            buf.append(ch)
            i += 1
        parts.append(''.join(buf).strip())
        return parts

    def _at_delimiter(self, s: str, i: int, delimiter: str) -> bool:
        if delimiter == COMMA or delimiter == PIPE:
            return s[i] == delimiter
        if delimiter == TAB:
            return s[i] == '\t'
        return s[i : i + len(delimiter)] == delimiter

