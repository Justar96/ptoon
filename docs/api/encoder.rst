Encoder API Reference
=====================

This page documents the ``Encoder`` class used for converting Python values to TOON format.

Encoder Class
-------------

.. autoclass:: pytoon.encoder.Encoder
   :members:
   :undoc-members:
   :show-inheritance:

Usage
-----

Direct usage (advanced):

.. code-block:: python

    from pytoon.encoder import Encoder

    # Create encoder with options
    encoder = Encoder(indent=4, delimiter="|", length_marker=True)
    
    # Encode data
    toon_str = encoder.encode({"users": [...]})

**Note:** Most users should use ``pytoon.encode()`` instead of using the ``Encoder`` class directly.

Encoding Strategies
-------------------

The encoder uses three strategies for arrays:

1. **Inline Arrays**
   
   For primitive arrays:
   
   .. code-block:: text
   
       numbers[5]: 1, 2, 3, 4, 5

2. **Tabular Arrays**
   
   For uniform object arrays (≥2 items):
   
   .. code-block:: text
   
       users[2]{id, name}:
         1, Alice
         2, Bob

3. **List Arrays**
   
   For mixed content:
   
   .. code-block:: text
   
       items[3]:
         - first
         - second
         - third

See Also
--------

* :doc:`../user_guide/format_specification` - Format details
* :doc:`core` - Main API reference
