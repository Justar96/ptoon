Core API
========

This page documents the main API functions provided by pytoon. See :doc:`../api/types` for reusable type aliases used throughout the examples.

.. note::

   **API stability:** ``encode()`` and ``decode()`` are considered stable entry points. New utilities (e.g., token analysis helpers) are additive and optional, and changes will not break existing integrations.

Main Functions
--------------

encode()
~~~~~~~~

.. code-block:: python

    pytoon.encode(value: JsonValue, *, options: EncodeOptions | None = None) -> str

Encode a Python value to TOON format.

**Parameters:**

* ``value`` (JsonValue) - Python value to encode. Must be JSON-compatible (dict, list, str, int, float, bool, None).
* ``options`` (EncodeOptions, optional) - Encoding options to customize output format.

**Returns:**

* ``str`` - TOON-formatted string

**Supported Types:**

* Primitives: ``None``, ``bool``, ``int``, ``float``, ``str``
* Collections: ``dict``, ``list``
* Special handling:
  
  * ``datetime`` objects → ISO 8601 strings
  * ``set`` objects → sorted lists
  * Large integers (>2^53-1) → strings (for JavaScript compatibility)
  * Non-finite floats (inf, NaN) → ``null``

**Examples:**

Simple object:

.. code-block:: python

    data = {"name": "Alice", "age": 30}
    toon_str = pytoon.encode(data)
    print(toon_str)
    # Output:
    # name: Alice
    # age: 30

Array of objects (tabular format):

.. code-block:: python

    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }
    toon_str = pytoon.encode(data)
    print(toon_str)
    # Output:
    # users[2]{id, name}:
    #   1, Alice
    #   2, Bob

With options:

.. code-block:: python

    options = {
        "delimiter": "|",
        "indent": 4,
        "length_marker": True
    }
    toon_str = pytoon.encode(data, options=options)

**Errors:**

* ``TypeError`` - If value contains non-serializable types (functions, classes, etc.)
* ``ValueError`` - If value contains circular references

decode()
~~~~~~~~

.. code-block:: python

    pytoon.decode(text: str) -> JsonValue

Decode a TOON-formatted string to Python value.

**Parameters:**

* ``text`` (str) - TOON-formatted string to decode

**Returns:**

* ``JsonValue`` - Decoded Python value (dict, list, or primitive)

**Examples:**

Simple object:

.. code-block:: python

    toon_str = """
    name: Alice
    age: 30
    """
    data = pytoon.decode(toon_str)
    print(data)
    # Output: {'name': 'Alice', 'age': 30}

Tabular array:

.. code-block:: python

    toon_str = """
    users[2]{id, name}:
      1, Alice
      2, Bob
    """
    data = pytoon.decode(toon_str)
    print(data)
    # Output: {'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}

**Errors:**

* ``ValueError`` - If text is invalid TOON format:
  
  * Invalid indentation
  * Tabs in indentation (use spaces only)
  * Array length mismatch
  * Invalid headers
  * Malformed escape sequences

Utility Functions
-----------------

count_tokens()
~~~~~~~~~~~~~~

.. code-block:: python

    pytoon.count_tokens(text: str, encoding: str = "o200k_base") -> int

Count tokens in a string using tiktoken.

**Parameters:**

* ``text`` (str) - Text to count tokens in
* ``encoding`` (str, optional) - Tokenizer encoding to use. Default: ``"o200k_base"`` (GPT-4o)

**Returns:**

* ``int`` - Number of tokens

**Supported Encodings:**

* ``"o200k_base"`` - GPT-4o, GPT-4o-mini (default)
* ``"cl100k_base"`` - GPT-4, GPT-3.5-turbo
* ``"p50k_base"`` - Older models
* ``"r50k_base"`` - Davinci, etc.

**Requirements:**

Requires ``tiktoken`` package:

.. code-block:: bash

    pip install tiktoken

**Examples:**

.. code-block:: python

    import pytoon

    text = "Hello, world!"
    token_count = pytoon.count_tokens(text)
    print(f"Tokens: {token_count}")
    # Output: Tokens: 4

    # With different encoding
    token_count = pytoon.count_tokens(text, encoding="cl100k_base")

estimate_savings()
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    pytoon.estimate_savings(data: Any, encoding: str = "o200k_base") -> dict[str, int | float]

Compare JSON vs TOON token efficiency for a value.

**Parameters:**

* ``data`` (Any) - Python dict or list to analyze
* ``encoding`` (str, optional) - Tokenizer encoding (default: ``"o200k_base"``)

**Returns:**

Dictionary with keys:

* ``json_tokens`` (int) - Token count for JSON
* ``toon_tokens`` (int) - Token count for TOON
* ``savings`` (int) - Token difference
* ``savings_percent`` (float) - Percentage savings

**Examples:**

.. code-block:: python

    import pytoon

    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }

    result = pytoon.estimate_savings(data)
    print(f"JSON tokens: {result['json_tokens']}")
    print(f"TOON tokens: {result['toon_tokens']}")
    print(f"Savings: {result['savings']} tokens ({result['savings_percent']:.1f}%)")

**Note:**

To compare specific encoding options, encode manually with ``pytoon.encode(..., options=...)`` and count tokens using ``pytoon.count_tokens()``.

compare_formats()
~~~~~~~~~~~~~~~~~

.. code-block:: python

    pytoon.compare_formats(data: Any, encoding: str = "o200k_base") -> str

Generate visual comparison table of JSON vs TOON formats.

**Parameters:**

* ``data`` (Any) - Python dict or list to compare
* ``encoding`` (str, optional) - Tokenizer encoding (default: ``"o200k_base"``)

**Returns:**

* ``str`` - Formatted comparison table

**Example:**

.. code-block:: python

    import pytoon

    data = {"users": [{"id": 1, "name": "Alice"}]}
    print(pytoon.compare_formats(data))

Output:

.. code-block:: text

    Format Comparison
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Format  Tokens  Size (bytes)  Savings
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    JSON    28      89            -
    TOON    18      53            35.7% tokens, 40.4% size
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Encoding Options
----------------

The ``options`` parameter accepts a dictionary with the following keys:

indent
~~~~~~

**Type:** ``int``

**Default:** ``2``

Number of spaces per indentation level.

**Example:**

.. code-block:: python

    # indent=2 (default)
    pytoon.encode({"user": {"name": "Alice"}}, options={"indent": 2})
    # user:
    #   name: Alice

    # indent=4
    pytoon.encode({"user": {"name": "Alice"}}, options={"indent": 4})
    # user:
    #     name: Alice

delimiter
~~~~~~~~~

**Type:** ``","`` | ``"|"`` | ``"\t"``

**Default:** ``","``

Delimiter for array values in inline and tabular formats.

**Example:**

.. code-block:: python

    data = {"values": [1, 2, 3]}

    # Comma (default)
    pytoon.encode(data, options={"delimiter": ","})
    # values[3]: 1, 2, 3

    # Pipe
    pytoon.encode(data, options={"delimiter": "|"})
    # values[3|]: 1| 2| 3

    # Tab
    pytoon.encode(data, options={"delimiter": "\t"})
    # values[3\t]: 1	2	3

length_marker
~~~~~~~~~~~~~

**Type:** ``bool``

**Default:** ``False``

Include ``#`` prefix in array length markers for strict validation.

**Example:**

.. code-block:: python

    data = {"items": [1, 2, 3]}

    # length_marker=False (default)
    pytoon.encode(data, options={"length_marker": False})
    # items[3]: 1, 2, 3

    # length_marker=True
    pytoon.encode(data, options={"length_marker": True})
    # items[#3]: 1, 2, 3

With length markers, the decoder strictly validates array lengths and raises ``ValueError`` if mismatch occurs.

Type System
-----------

pytoon provides type hints for better IDE support:

.. code-block:: python

    from pytoon.types import (
        JsonValue,      # Any JSON-compatible value
        JsonObject,     # dict[str, JsonValue]
        JsonArray,      # list[JsonValue]
        JsonPrimitive,  # None | bool | int | float | str
        Delimiter,      # Literal[",", "|", "\t"]
        EncodeOptions,  # TypedDict with encoding options
    )

**Example usage:**

.. code-block:: python

    from pytoon.types import JsonObject, EncodeOptions
    import pytoon

    def process_data(data: JsonObject, opts: EncodeOptions) -> str:
        return pytoon.encode(data, options=opts)

Best Practices
--------------

When to Use TOON vs JSON
~~~~~~~~~~~~~~~~~~~~~~~~~

**Use TOON when:**

* Sending data in LLM prompts
* Token efficiency matters
* Data has repeated structure (tabular data)
* Human readability is desired

**Use JSON when:**

* LLM function calling / tool use (strict schema required)
* Very small payloads (<100 tokens)
* Interop with systems expecting JSON
* Highly heterogeneous data

Error Handling
~~~~~~~~~~~~~~

Always wrap decode in try-except:

.. code-block:: python

    try:
        data = pytoon.decode(toon_str)
    except ValueError as e:
        print(f"Decode error: {e}")
        # Handle error or fallback to JSON

Performance Tips
~~~~~~~~~~~~~~~~

* Encoding is slower than JSON (~0.12x speed) but token savings offset this
* Use ``estimate_savings()`` to decide if TOON is worthwhile
* Cache encoded strings when reusing same data
* For more, see :doc:`performance_tips`

See Also
--------

* :doc:`/guides/encoding_options` - Detailed encoding options guide
* :doc:`/guides/error_handling` - Error handling patterns
* :doc:`/guides/token_optimization` - Token optimization strategies
* :doc:`/api/encoder` - Encoder class documentation
* :doc:`/api/decoder` - Decoder class documentation
