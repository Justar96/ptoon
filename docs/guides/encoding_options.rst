Encoding Options
================

This guide covers all encoding options in detail with visual examples.

Overview
--------

``pytoon.encode()`` accepts an optional ``options`` parameter to customize output:

.. code-block:: python

    options = {
        "delimiter": ",",      # or "|" or "\t"
        "indent": 2,           # spaces per level (int >= 0)
        "length_marker": False # include #N in headers (bool)
    }

    toon_str = pytoon.encode(data, options=options)

Option: indent
--------------

**Type:** ``int`` (>= 0)

**Default:** ``2``

**Purpose:** Control indentation spacing (spaces per level)

Examples
~~~~~~~~

**indent=2 (default):**

.. code-block:: text

    user:
      name: Alice
      contact:
        email: alice@example.com

**indent=4:**

.. code-block:: text

    user:
        name: Alice
        contact:
            email: alice@example.com

**indent=1 (compact):**

.. code-block:: text

    user:
     name: Alice
     contact:
      email: alice@example.com

Token Impact
~~~~~~~~~~~~

.. code-block:: python

    data = {"user": {"name": "Alice", "age": 30}}

    # indent=2 (default): 22 tokens
    # indent=4: 24 tokens (+9%)
    # indent=1: 21 tokens (-5%)

**Recommendation:**

* **indent=2**: Best balance (default)
* **indent=4**: Better readability
* **indent=1**: More compact while maintaining structure

.. note::

   **Caution:** ``indent=0`` uses a single space per depth internally to preserve structure, keeping nested data decodable while minimizing whitespace. The output is significantly harder to read, so prefer ``indent >= 1`` for nested data unless byte- or token-level compaction is critical.

Option: delimiter
-----------------

**Type:** ``","`` | ``"|"`` | ``"\t"``

**Default:** ``","``

**Purpose:** Control value separator in arrays

Comma (default)
~~~~~~~~~~~~~~~

.. code-block:: text

    values[3]: 1, 2, 3
    users[2]{id, name}:
      1, Alice
      2, Bob

**Use when:** General purpose (most readable)

Pipe
~~~~

.. code-block:: text

    values[3|]: 1| 2| 3
    users[2|]{id| name}:
      1| Alice
      2| Bob

**Use when:** Data contains commas

Example:

.. code-block:: python

    data = {
        "products": [
            {"name": "Widget, Large", "price": 19.99},
            {"name": "Gadget, Small", "price": 9.99}
        ]
    }

    # With comma delimiter (requires quoting)
    pytoon.encode(data, options={"delimiter": ","})
    # products[2]{name, price}:
    #   "Widget, Large", 19.99
    #   "Gadget, Small", 9.99

    # With pipe delimiter (no quoting needed)
    pytoon.encode(data, options={"delimiter": "|"})
    # products[2|]{name| price}:
    #   Widget, Large| 19.99
    #   Gadget, Small| 9.99

Tab
~~~

.. code-block:: text

    values[3\t]: 1	2	3
    users[2\t]{id	name}:
      1	Alice
      2	Bob

**Use when:** Maximum compactness

Token Impact
~~~~~~~~~~~~

.. code-block:: python

    data = {"values": list(range(10))}

    # Comma: 28 tokens
    # Pipe: 28 tokens (similar)
    # Tab: 26 tokens (-7%)

**Recommendation:**

* **Comma**: Default, most readable
* **Pipe**: When data contains commas
* **Tab**: Maximum efficiency (less readable)

Option: length_marker
---------------------

**Type:** ``bool``

**Default:** ``False``

**Purpose:** Include ``#`` prefix in array length declarations

Without length_marker (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    items[3]:
      - apple
      - banana
      - cherry

With length_marker
~~~~~~~~~~~~~~~~~~

.. code-block:: text

    items[#3]:
      - apple
      - banana
      - cherry

Validation Behavior
~~~~~~~~~~~~~~~~~~~

**With length markers:**

.. code-block:: python

    # Decoder strictly validates length
    toon_str = """
    items[#3]:
      - apple
      - banana
    """
    pytoon.decode(toon_str)  # ValueError: expected 3, got 2

**Without length markers:**

.. code-block:: python

    # Decoder is more lenient
    toon_str = """
    items[3]:
      - apple
      - banana
    """
    pytoon.decode(toon_str)  # Still validates but less strict

Token Impact
~~~~~~~~~~~~

.. code-block:: python

    data = {"items": ["a", "b", "c"]}

    # Without: 12 tokens
    # With: 13 tokens (+8%)

**Recommendation:**

* **False**: Default, most cases
* **True**: When strict validation is critical

Combining Options
-----------------

Example 1: Maximum Compactness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Use indent=1 for nested structures (indent=0 only valid for flat data)
    options = {
        "indent": 1,
        "delimiter": "\t",
        "length_marker": False
    }

    toon_str = pytoon.encode(data, options=options)

**Token savings:** ~5-10% compared to default

**Trade-off:** Less readable

Example 2: Maximum Readability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    options = {
        "indent": 4,
        "delimiter": ",",
        "length_marker": True
    }

    toon_str = pytoon.encode(data, options=options)

**Token cost:** ~3-5% more than default

**Benefit:** Clearer structure, strict validation

Example 3: Balanced (Default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Explicit default options
    options = {
        "indent": 2,
        "delimiter": ",",
        "length_marker": False
    }

    # Or simply omit options
    toon_str = pytoon.encode(data)

**Good balance:** Readability and efficiency

Visual Comparison
-----------------

Same data with different options:

.. code-block:: python

    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }

Default Options
~~~~~~~~~~~~~~~

.. code-block:: text

    users[2]{id, name}:
      1, Alice
      2, Bob

**Tokens:** 18

Compact Options
~~~~~~~~~~~~~~~

.. code-block:: python

    options = {"indent": 1, "delimiter": "\t"}

.. code-block:: text

    users[2\t]{id	name}:
     1	Alice
     2	Bob

**Tokens:** 17 (-6%)

Readable Options
~~~~~~~~~~~~~~~~

.. code-block:: python

    options = {"indent": 4, "delimiter": ",", "length_marker": True}

.. code-block:: text

    users[#2]{id, name}:
        1, Alice
        2, Bob

**Tokens:** 20 (+11%)

Decision Guide
--------------

Choose indent
~~~~~~~~~~~~~

* **2**: Default, recommended
* **4**: Prefer readability  
* **1**: Compact (but still valid for nested structures)
* **0**: Only for flat objects/arrays without nesting

Choose delimiter
~~~~~~~~~~~~~~~~

* **","**: Default, no commas in data
* **"|"**: Data contains commas
* **"\t"**: Maximum compactness

Choose length_marker
~~~~~~~~~~~~~~~~~~~~

* **False**: Default, most cases
* **True**: Need strict validation

Performance Impact
------------------

Options affect token count by 0-10%:

.. code-block:: python

    data = {"employees": [...]}  # 100 employees

    # Default
    result = pytoon.estimate_savings(data)
    # TOON: 2,162 tokens

    # Compact options (indent=1 for nested data)
    options = {"indent": 1, "delimiter": "\t"}
    toon_str = pytoon.encode(data, options=options)
    toon_tokens = pytoon.count_tokens(toon_str)
    # TOON: 2,100 tokens (-2.9%)

    # Readable options
    options = {"indent": 4, "length_marker": True}
    toon_str = pytoon.encode(data, options=options)
    toon_tokens = pytoon.count_tokens(toon_str)
    # TOON: 2,240 tokens (+3.6%)

**Encoding speed:** Unaffected by options

Best Practices
--------------

1. Start with Defaults
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Simple and effective
    toon_str = pytoon.encode(data)

2. Measure Impact
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Test different options
    for delim in [",", "|", "\t"]:
        opts = {"delimiter": delim}
        toon_str = pytoon.encode(data, options=opts)
        toon_tokens = pytoon.count_tokens(toon_str)
        print(f"{delim}: {toon_tokens} tokens")

3. Be Consistent
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Choose options once, use throughout app
    APP_OPTIONS = {"delimiter": "|", "indent": 2}

    def encode_for_llm(data):
        return pytoon.encode(data, options=APP_OPTIONS)

4. Document Choices
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Explain why
    OPTIONS = {
        "delimiter": "|",  # Data contains commas
        "indent": 2        # Default readability
    }

See Also
--------

* :doc:`/user_guide/core_api` - Core API documentation
* :doc:`/guides/token_optimization` - Token optimization guide
* :doc:`/user_guide/format_specification` - Format details
