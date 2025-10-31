Format Specification
====================

This guide explains the TOON format structure and rules. For the normative specification, see `SPEC.md on GitHub <https://github.com/Justar96/ptoon/blob/main/SPEC.md>`_.

Introduction
------------

TOON (Token-Oriented Object Notation) is a text format optimized for LLM token efficiency while maintaining human readability. It achieves 30-60% token savings compared to JSON by:

* Eliminating repeated keys in arrays
* Using compact syntax
* Minimizing structural characters

Data Model
----------

TOON supports the same data types as JSON:

* **Primitives**: ``null``, ``true``, ``false``, numbers, strings
* **Objects**: Key-value mappings
* **Arrays**: Ordered lists

Format Overview
---------------

Objects
~~~~~~~

Objects use ``key: value`` syntax:

.. code-block:: text

    name: Alice
    age: 30
    city: San Francisco

Nested objects:

.. code-block:: text

    user:
      name: Alice
      contact:
        email: alice@example.com
        phone: 555-1234

Arrays
~~~~~~

TOON supports three array formats depending on content:

1. **Inline Arrays** - For primitive arrays
2. **Tabular Arrays** - For uniform objects (most efficient)
3. **List Arrays** - For mixed/nested content

Inline Arrays
~~~~~~~~~~~~~

For arrays of primitives:

.. code-block:: text

    numbers[5]: 1, 2, 3, 4, 5
    names[3]: Alice, Bob, Carol

Empty arrays:

.. code-block:: text

    empty[0]:

Tabular Arrays
~~~~~~~~~~~~~~

For arrays of uniform objects (≥2 items). This is the most token-efficient format.

**Syntax:** ``key[N]{field1, field2}:``

**Example:**

.. code-block:: text

    employees[3]{id, name, role}:
      1, Alice, Engineer
      2, Bob, Designer
      3, Carol, Manager

**Requirements:**

* All objects must have identical keys
* All values must be primitives
* Minimum 2 objects required
* Field order follows the first object's key ordering; subsequent rows are reordered to match for deterministic headers

**Comparison with JSON:**

TOON:

.. code-block:: text

    employees[3]{id, name, role}:
      1, Alice, Engineer
      2, Bob, Designer

JSON (equivalent):

.. code-block:: json

    {
      "employees": [
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Designer"}
      ]
    }

**Token savings:** Notice how "id", "name", and "role" appear once in TOON vs repeated in each JSON object.

List Arrays
~~~~~~~~~~~

For mixed content, nested structures, or objects that don't qualify for tabular format:

.. code-block:: text

    items[3]:
      - first item
      - second item
      - third item

Nested structures:

.. code-block:: text

    users[2]:
      - name: Alice
        age: 30
      - name: Bob
        age: 25

Primitives
----------

Null, Booleans
~~~~~~~~~~~~~~

.. code-block:: text

    value: null
    active: true
    disabled: false

Numbers
~~~~~~~

Integers and floats:

.. code-block:: text

    count: 42
    price: 19.99
    negative: -100

Large integers (>2^53-1) are encoded as strings for JavaScript compatibility:

.. code-block:: python

    # Python
    ptoon.encode({"big": 9007199254740992})
    # Output: big: "9007199254740992"

Strings
~~~~~~~

Unquoted strings (safe):

.. code-block:: text

    name: Alice
    city: San_Francisco

Quoted strings (when containing special characters):

.. code-block:: text

    message: "Hello, world!"
    path: "C:\\Users\\Alice"
    json: "{\"key\": \"value\"}"

**Quoting rules:**

Strings must be quoted if they:

* Are empty
* Have leading/trailing whitespace
* Match ``true``, ``false``, ``null`` (case-insensitive)
* Look like numbers
* Contain: ``:`` ``"`` ``\\`` ``[`` ``]`` ``{`` ``}`` ``,`` or the active delimiter

**Escape sequences:**

* ``\\n`` - newline
* ``\\r`` - carriage return
* ``\\t`` - tab
* ``\\`` - backslash
* ``\\"`` - double quote

Delimiters
----------

TOON supports three delimiters for array values:

Comma (default)
~~~~~~~~~~~~~~~

.. code-block:: text

    values[3]: 1, 2, 3
    users[2]{id, name}:
      1, Alice
      2, Bob

Pipe
~~~~

Useful when data contains commas:

.. code-block:: text

    values[3|]: 1| 2| 3
    products[2|]{name| price}:
      Widget, Large| 19.99
      Gadget, Small| 9.99

Tab
~~~

Most compact, harder to read:

.. code-block:: text

    values[3\t]: 1	2	3
    users[2\t]{id	name}:
      1	Alice
      2	Bob

**Delimiter scoping:** The delimiter specified in an array header applies to that array and its nested structures.

Indentation
-----------

* Use spaces only (tabs are not allowed)
* Consistent indentation required
* Default: 2 spaces per level
* Auto-detected on decode

Example with indent=4:

.. code-block:: text

    user:
        name: Alice
        contact:
            email: alice@example.com

Special Cases
-------------

Empty Structures
~~~~~~~~~~~~~~~~

Empty objects and arrays:

.. code-block:: text

    empty_object:
    empty_array[0]:

Root Arrays
~~~~~~~~~~~

Root-level arrays are supported:

.. code-block:: text

    [3]:
      - Alice
      - Bob
      - Carol

Or tabular:

.. code-block:: text

    [2]{id, name}:
      1, Alice
      2, Bob

Datetime Objects
~~~~~~~~~~~~~~~~

Python datetime objects are encoded as ISO 8601 strings:

.. code-block:: python

    from datetime import datetime
    import ptoon

    data = {"timestamp": datetime(2025, 10, 31, 12, 30)}
    toon_str = ptoon.encode(data)
    # timestamp: 2025-10-31T12:30:00

Sets
~~~~

Python sets are encoded as sorted arrays:

.. code-block:: python

    data = {"tags": {3, 1, 2}}
    toon_str = ptoon.encode(data)
    # tags[3]: 1, 2, 3

Length Markers
--------------

Optional ``#`` prefix for strict length validation:

Without length marker (default):

.. code-block:: text

    items[3]: a, b, c

With length marker:

.. code-block:: text

    items[#3]: a, b, c

When decoding with length markers, the decoder validates that exactly the specified number of items are present and raises ``ValueError`` on mismatch.

Visual Examples
---------------

Example 1: Employee Records
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**TOON (tabular):**

.. code-block:: text

    employees[3]{id, name, role, salary}:
      1, Alice, Engineer, 120000
      2, Bob, Designer, 100000
      3, Carol, Manager, 150000

**JSON (equivalent):**

.. code-block:: json

    {
      "employees": [
        {"id": 1, "name": "Alice", "role": "Engineer", "salary": 120000},
        {"id": 2, "name": "Bob", "role": "Designer", "salary": 100000},
        {"id": 3, "name": "Carol", "role": "Manager", "salary": 150000}
      ]
    }

**Token savings:** ~64% (TOON: 39 tokens vs JSON: 108 tokens)

Example 2: Nested Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**TOON:**

.. code-block:: text

    company:
      name: Acme Corp
      employees[2]:
        - name: Alice
          role: Engineer
        - name: Bob
          role: Designer

**JSON:**

.. code-block:: json

    {
      "company": {
        "name": "Acme Corp",
        "employees": [
          {"name": "Alice", "role": "Engineer"},
          {"name": "Bob", "role": "Designer"}
        ]
      }
    }

Validation Rules
----------------

Valid TOON documents must:

* Use spaces for indentation (no tabs)
* Have consistent indentation
* Match array lengths (when length markers used)
* Use valid escape sequences in strings
* Have properly formatted headers

Common parsing errors:

* **Invalid indentation** - Inconsistent spacing
* **Tab characters** - Use spaces only
* **Array length mismatch** - Declared length doesn't match items
* **Invalid escape** - Unknown escape sequence like ``\\x``
* **Blank lines in arrays** - Not allowed between array items

See Also
--------

* `SPEC.md <https://github.com/Justar96/ptoon/blob/main/SPEC.md>`_ - Normative specification
* :doc:`core_api` - Encoding/decoding API
* :doc:`/guides/encoding_options` - Encoding options guide
* :doc:`/troubleshooting` - Common issues and solutions
