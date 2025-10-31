Core API Reference
==================

This page documents the main ``ptoon`` module API.

Module Overview
---------------

The ``ptoon`` module provides the main entry points for encoding and decoding TOON format.

Main Functions
--------------

.. automodule:: ptoon
   :members: encode, decode
   :undoc-members:
   :noindex:

Utility Functions
-----------------

.. autofunction:: ptoon.count_tokens
   :noindex:

.. autofunction:: ptoon.estimate_savings
   :noindex:

.. autofunction:: ptoon.compare_formats
   :noindex:

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import ptoon

    # Encode
    data = {"name": "Alice", "age": 30}
    toon_str = ptoon.encode(data)

    # Decode
    decoded = ptoon.decode(toon_str)
    assert decoded == data

With Options
~~~~~~~~~~~~

.. code-block:: python

    options = {
        "delimiter": "|",
        "indent": 4,
        "length_marker": True
    }
    toon_str = ptoon.encode(data, options=options)

Token Counting
~~~~~~~~~~~~~~

.. code-block:: python

    # Count tokens
    tokens = ptoon.count_tokens(toon_str)

    # Estimate savings
    result = ptoon.estimate_savings(data)
    print(f"Savings: {result['savings_percent']:.1f}%")

    # Visual comparison
    print(ptoon.compare_formats(data))

See Also
--------

* :doc:`../user_guide/core_api` - Core API user guide
* :doc:`encoder` - Encoder class reference
* :doc:`decoder` - Decoder class reference
* :doc:`utils` - Utilities reference
* :doc:`types` - Type definitions
