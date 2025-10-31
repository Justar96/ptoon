Core API Reference
==================

This page documents the main ``pytoon`` module API.

Module Overview
---------------

The ``pytoon`` module provides the main entry points for encoding and decoding TOON format.

Main Functions
--------------

.. automodule:: pytoon
   :members: encode, decode
   :undoc-members:

Utility Functions
-----------------

.. autofunction:: pytoon.count_tokens

.. autofunction:: pytoon.estimate_savings

.. autofunction:: pytoon.compare_formats

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import pytoon

    # Encode
    data = {"name": "Alice", "age": 30}
    toon_str = pytoon.encode(data)

    # Decode
    decoded = pytoon.decode(toon_str)
    assert decoded == data

With Options
~~~~~~~~~~~~

.. code-block:: python

    options = {
        "delimiter": "|",
        "indent": 4,
        "length_marker": True
    }
    toon_str = pytoon.encode(data, options=options)

Token Counting
~~~~~~~~~~~~~~

.. code-block:: python

    # Count tokens
    tokens = pytoon.count_tokens(toon_str)

    # Estimate savings
    result = pytoon.estimate_savings(data)
    print(f"Savings: {result['savings_percent']:.1f}%")

    # Visual comparison
    print(pytoon.compare_formats(data))

See Also
--------

* :doc:`../user_guide/core_api` - Core API user guide
* :doc:`encoder` - Encoder class reference
* :doc:`decoder` - Decoder class reference
* :doc:`utils` - Utilities reference
* :doc:`types` - Type definitions
