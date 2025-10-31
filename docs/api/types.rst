Type Definitions
================

This page documents type definitions used in pytoon for better IDE support and type checking.

Type Definitions
----------------

.. automodule:: pytoon.types
   :members:
   :undoc-members:

Core Types
----------

``JsonPrimitive``
~~~~~~~~~~~~~~~~~

.. code-block:: python

    JsonPrimitive = None | bool | int | float | str

Represents JSON primitive values.

``JsonArray``
~~~~~~~~~~~~~

.. code-block:: python

    JsonArray = list[JsonValue]

Represents JSON arrays.

``JsonObject``
~~~~~~~~~~~~~~

.. code-block:: python

    JsonObject = dict[str, JsonValue]

Represents JSON objects.

``JsonValue``
~~~~~~~~~~~~~

.. code-block:: python

    JsonValue = JsonPrimitive | JsonArray | JsonObject

Represents any JSON-compatible value.

Option Types
------------

``Delimiter``
~~~~~~~~~~~~~

.. code-block:: python

    Delimiter = Literal[",", "|", "\t"]

Delimiter options for array values.

``EncodeOptions``
~~~~~~~~~~~~~~~~~

.. code-block:: python

    class EncodeOptions(TypedDict, total=False):
        delimiter: Delimiter
        indent: int
        length_marker: bool

Encoding options dictionary.

Usage Examples
--------------

Importing Types
~~~~~~~~~~~~~~~

.. code-block:: python

    from pytoon.types import JsonValue, JsonObject, JsonArray, EncodeOptions

Function Type Hints
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pytoon.types import JsonValue, JsonObject, EncodeOptions
    import pytoon

    def process_data(data: JsonObject) -> str:
        """Encode object to TOON."""
        return pytoon.encode(data)

    def custom_encode(value: JsonValue, opts: EncodeOptions) -> str:
        """Encode with custom options."""
        return pytoon.encode(value, options=opts)

    def batch_encode(items: list[JsonObject]) -> list[str]:
        """Encode multiple objects."""
        return [pytoon.encode(item) for item in items]

Using EncodeOptions
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pytoon.types import EncodeOptions
    import pytoon

    # Define reusable options
    compact_opts: EncodeOptions = {
        "delimiter": "\t",
        "indent": 1,
        "length_marker": False
    }

    readable_opts: EncodeOptions = {
        "delimiter": ",",
        "indent": 4,
        "length_marker": True
    }

    data = {"users": [{"id": 1, "name": "Alice"}]}
    
    # Use with encode
    compact = pytoon.encode(data, options=compact_opts)
    readable = pytoon.encode(data, options=readable_opts)

Working with JsonValue
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pytoon.types import JsonValue, JsonObject
    import pytoon

    def safe_encode(value: JsonValue) -> str:
        """Safely encode any JSON-compatible value."""
        try:
            return pytoon.encode(value)
        except (TypeError, ValueError) as e:
            print(f"Encoding error: {e}")
            return ""

    # Works with all JSON-compatible types
    safe_encode({"name": "Alice"})  # dict
    safe_encode([1, 2, 3])           # list
    safe_encode("hello")              # str
    safe_encode(42)                   # int
    safe_encode(None)                 # None

Type Checking
~~~~~~~~~~~~~

Use with mypy or pyright:

.. code-block:: bash

    # mypy
    mypy your_script.py

    # pyright
    pyright your_script.py

Example type-checked module:

.. code-block:: python

    from pytoon.types import JsonObject, EncodeOptions
    import pytoon

    def create_user_data(name: str, age: int) -> JsonObject:
        """Create a user data object."""
        return {"name": name, "age": age}

    def encode_users(users: list[JsonObject]) -> str:
        """Encode user list to TOON."""
        opts: EncodeOptions = {"indent": 2}
        return pytoon.encode({"users": users}, options=opts)

    # Type checker ensures correctness
    user = create_user_data("Alice", 30)
    toon_str = encode_users([user])

See Also
--------

* :doc:`core` - Main API reference
* :doc:`../user_guide/core_api` - Core API guide
* `Python typing documentation <https://docs.python.org/3/library/typing.html>`_
