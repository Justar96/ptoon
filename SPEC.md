# pytoon Specification

Version: **v0.1.0**  
Status: Draft (normative where indicated)  
Audience: Python developers implementing TOON encoders/decoders, tool builders,
prompt engineers, and QA teams validating interoperability with the canonical
TypeScript implementation.

`pytoon` is the Python reference port of Token-Oriented Object Notation (TOON),
optimized for Large Language Model (LLM) token efficiency while remaining human
readable. It preserves the core TOON semantics defined in
[johannschopplich/toon](https://github.com/johannschopplich/toon) and documents
Python-specific normalization and runtime behavior.

## Changelog

- **v0.1.0 — October 30, 2025**
  - Aligned encoder output and decoder strict-mode rules with upstream TOON
    v1.2, including delimiter scoping, float formatting (no exponent notation),
    blank-line enforcement, and hyphen formatting.
  - Added normative guidance for Python normalization (datetime, set ordering,
    large integers, unsupported types).
  - Documented strict-mode error cases now enforced by the decoder (tab
    indentation, invalid escapes, forbidden leading zeros, incomplete arrays).
  - Clarified option handling (`indent`, `delimiter`, `length_marker`) and cache
    behavior in `pytoon.__init__`.
- **v0.0.0 — Initial acknowledgement**
  - Adopted the canonical TOON specification maintained by Johann Schopplich as
    the foundational reference. Immense thanks to the upstream authors and
    contributors whose work made this port possible.

---

## 1. Terminology and Conventions

- **TOON document**: UTF-8 text composed of LF-terminated lines serialized by the
  encoder.
- **Line**: a sequence of non-newline characters ending with LF (`\n`); CRLF is
  normalized to LF on decode.
- **Indentation level (depth)**: number of indentation units preceding content.
- **Indentation unit (indentSize)**: configured number of spaces per depth
  (default 2). Tabs MUST NOT be used for indentation.
- **Header**: bracketed array declaration possibly followed by a field list,
  terminating in a colon (e.g., `items[3]:`, `rows[2|]{a|b}:`).
- **Field list**: brace-enclosed list of tabular headers separated by the active
  delimiter.
- **List item**: line beginning with `- ` at depth+1 relative to the owning
  header.
- **Document delimiter**: default delimiter chosen by encoder options (comma by
  default) used outside any array scope.
- **Active delimiter**: delimiter declared in the nearest array header; governs
  splitting and quoting within that scope.
- **Length marker**: optional `#` prefix in array headers (e.g., `[#3]`); tracked
  via encoder option `length_marker`.
- **Strict mode**: decoder’s default validation mode. All error requirements in
  this document apply to strict mode.

Keywords **MUST**, **MUST NOT**, **SHOULD**, **MAY** follow RFC 2119 semantics.

## 2. Data Model

- `JsonPrimitive`: `str | int | float | bool | None`
- `JsonArray`: ordered list of `JsonValue`
- `JsonObject`: ordered mapping `dict[str, JsonValue]`
- `JsonValue`: `JsonPrimitive | JsonArray | JsonObject`
- Object key order and array element order MUST be preserved roundtrip.
- Numbers are assumed to be finite; encoders normalize non-finites to `null`.

## 3. Normalization (Encoder)

### 3.1 Primitive Numbers

- `-0.0` MUST encode as `0`.
- Finite floats MUST render without exponent notation. `pytoon` formats them via
  `Decimal(str(value))`, then strips trailing zeros and decimal points.
- Integers with `abs(value) > 2**53 - 1` MUST encode as quoted decimal strings
  (to preserve precision across JS ecosystems).
- NaN and ±Infinity MUST normalize to `null`.

### 3.2 Other Types

- `datetime.datetime` values encode via `.isoformat()`. Timezone-awareness is
  preserved in the output string.
- `set` instances encode as arrays:
  - If elements are comparable, sorted order is used.
  - Otherwise, elements are sorted by `repr(x)` to ensure determinism.
- `Mapping` types encode as objects using stringified keys in iteration order.
- Unsupported or opaque types (functions, complex numbers, bytes, symbols,
  generators, etc.) MUST normalize to `null`.
- `list` and `tuple` normalize recursively to JSON arrays.

### 3.3 Strings and Keys

- Strings and keys pass through unchanged unless quoting/escaping is required by
  Section 6.
- Encoder escapes only the sequences `\\`, `\"`, `\n`, `\r`, `\t`. Tab (`\t`) is
  escaped unless the active delimiter is HTAB and the string is not a key.

## 4. Encoder Behavior

### 4.1 Objects

- `key: value` lines with exactly one space after the colon for primitives.
- Nested objects emit `key:` on one line, followed by child lines indented by
  `indent` spaces.
- Empty objects encode as `key:` with no additional content.

### 4.2 Arrays

1. **Inline primitive arrays**  
   `key[N<delim?>]: v1<delim>v2...` with one space after the colon when non-empty.
   Empty arrays emit `key[0<delim?>]:` with no trailing space.

2. **Tabular arrays**  
   Eligible when:
   - All elements are objects with identical key sets (≥1 key).
   - Every field value is a JSON primitive.
   - Array length ≥ 2.  
   Format: `key[N<delim?>]{f1<delim>f2}:` with each row emitted at depth+1 as a
   delimiter-separated primitive list.

3. **List arrays**  
   Used for mixed arrays, nested arrays/objects, or tabular-ineligible objects.
   Format:
   ```
   key[N<delim?>]:
     - item
     - key: value
   ```
   - Primitive items render as `- value`.
   - Nested arrays of primitives inline under `- [M...]: ...`.
   - Nested objects place their first field on the hyphen line; remaining fields
     appear at depth+1.

4. **Arrays of arrays**  
   If the top-level array contains only primitive arrays, the encoder emits list
   form where each nested array uses inline syntax (`- [M]: ...`).

### 4.3 Output Invariants

- Indentation uses spaces exclusively; tabs are prohibited.
- Each line is trimmed (no trailing spaces).
- Final document omits a trailing newline.

## 5. Decoder Behavior (Strict Mode)

### 5.1 Pre-processing

- Trailing newline characters are stripped before processing.
- Blank lines outside arrays/tabular scopes are ignored. Blank lines occurring
  between the first and last row/item inside an array/tabular scope MUST raise
  `ValueError`.
- Indent size is auto-detected as the smallest non-zero leading-space count. The
  decoder enforces that every indented line has a leading-space count that is an
  exact multiple of `indentSize`. Tabs encountered in indentation MUST raise
  `ValueError`.

### 5.2 Context Management

- Decoder maintains a stack of contexts (`object`, `array_list`, `array_tabular`)
  tracking depth, expected length, fields, and active delimiter.
- Dedenting closes contexts; arrays validate length equality before closing.
- Array headers without inline values push new contexts; inline arrays decode
  immediately.

### 5.3 Primitive Parsing

- Unquoted tokens `true`, `false`, `null` map to booleans/null.
- Numeric detection accepts standard decimal and exponent forms, but tokens with
  forbidden leading zeros (e.g., `05`, `-01`) MUST remain strings.
- Quoted tokens are unescaped using only the sanctioned sequences; encountering
  an unknown escape or unfinished escape MUST raise `ValueError`.

### 5.4 List Items

- Items MUST start with `- ` (hyphen + space). Lines starting with `-value` or
  other malformed prefixes are rejected.
- Primitive items decode via `_parse_primitive`.
- Inline arrays on hyphen lines parse using their nested headers.
- Object items parse the first field on the hyphen line and indent subsequent
  fields by +1 level. Nested objects inside list items indent by +2 relative to
  the hyphen line, matching the TypeScript reference.

### 5.5 Tabular Rows

- Tabular contexts track expected field count and length. Each row splits using
  the active delimiter. Length or field mismatches MUST raise `ValueError`.
- Completed tabular contexts automatically pop from the stack once the expected
  number of rows is consumed.

## 6. Quoting Rules

Strings or keys MUST be quoted when any of the following apply:

- Empty string.
- Leading or trailing whitespace.
- Case-insensitive matches for `true`, `false`, `null`.
- Numeric-looking tokens, including exponent forms or forbidden leading zeros.
- Contains colon (`:`), double-quote, backslash, square/curly brackets, comma,
  or the active delimiter.
- Begins with `-` (to avoid list-item ambiguity).
- Contains control characters (newline, carriage return, tab outside HTAB scope).
- Active delimiter is present anywhere in the token; non-active delimiters do
  not trigger quoting.

Keys additionally allow unquoted form only if they match `^[A-Z_][\w.]*$`
case-insensitively.

## 7. Delimiters

- Supported delimiters: comma (default), HTAB, pipe (`|`).
- Absence of a delimiter symbol in a header always implies comma, regardless of
  parent scope.
- Tabular headers must repeat the same delimiter inside `{}` as declared in the
  bracket segment.
- Nested headers establish new active delimiters; the decoder MUST scope splits
  accordingly.

## 8. Root Form Detection

1. If the first non-empty depth-0 line matches a header (`[N...]`), decode a root
   array (inline, list, or tabular).
2. If the document contains exactly one non-empty line that is neither a header
   nor a `key: ...` pattern, decode a primitive.
3. Otherwise, decode as an object whose keys live at depth zero.

Empty documents (after trimming ignorable blank lines) decode as `{}`.

## 9. Options and Defaults

`pytoon.encode(value, options=None)` accepts:

- `indent` (int, default 2) — spaces per indentation level.
- `delimiter` (str, default `,`) — document delimiter. Tabular and inline arrays
  inherit this unless a header overrides it.
- `length_marker` (bool, default False) — when true, encoders emit `[#N]`.

`pytoon.decode(source, options=None)` reserves the `options` parameter for
future use; strict mode is enabled by default. The module caches a default
encoder/decoder for common options to minimize allocations.

## 10. Conformance Requirements

An implementation claiming compatibility with this specification MUST:

1. Normalize inputs according to Section 3.
2. Produce syntax respecting Sections 4–7 (including formatting invariants).
3. Decode all conforming documents losslessly, validating errors described in
   Section 5 (strict mode).
4. Support the option surface described in Section 9.
5. Preserve key/element order roundtrip.

## 11. Recommended Test Coverage

Projects embedding `pytoon` SHOULD cover:

- Primitive quoting heuristics, including delimiter-aware cases.
- Object key quoting and order preservation.
- Inline primitive arrays, empty arrays, nested arrays of primitives.
- Tabular detection heuristics, field quoting, and delimiter propagation.
- Mixed arrays producing list items with nested objects and arrays.
- Length marker emission and enforcement.
- Whitespace invariants (no trailing spaces/newline).
- Decoder negative cases: invalid escapes, forbidden leading zeros, tab
  indentation, blank lines inside arrays, hyphen formatting, length mismatches.

The repository’s `tests/` directory mirrors these recommendations and SHOULD be
treated as part of the normative suite for regression.

## 12. Compatibility Notes

- Output produced by `pytoon` is designed to roundtrip with the upstream
  TypeScript decoder in strict mode.
- Differences are limited to language-specific normalization (e.g.,
  Python datetime string formats with timezone offsets).
- Consumers interacting with non-Python TOON implementations SHOULD ensure
  shared agreement on set ordering and custom-type normalization.

---

By adhering to this document, maintainers can evolve `pytoon` with confidence
that its behavior remains aligned with the broader TOON ecosystem while honoring
Python-specific guarantees. Contributions building on this specification SHOULD
update the changelog with explicit normative changes and expand the test matrix
accordingly.
