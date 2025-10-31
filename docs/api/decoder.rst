Decoder API Reference
=====================

This page documents the ``Decoder`` class used for parsing TOON format strings.

Decoder Class
-------------

.. autoclass:: pytoon.decoder.Decoder
   :members:
   :undoc-members:
   :show-inheritance:

Usage
-----

Direct usage (advanced):

.. code-block:: python

    from pytoon.decoder import Decoder

    # Create decoder
    decoder = Decoder()
    
    # Decode TOON string
    data = decoder.decode(toon_str)

**Note:** Most users should use ``pytoon.decode()`` instead of using the ``Decoder`` class directly.

Parsing Strategy
----------------

The decoder uses a stack-based approach:

* Line-by-line processing
* Depth tracking via indentation
* Context stack (object, array_list, array_tabular)
* Automatic context unwinding on dedent

Error Conditions
----------------

The decoder raises ``ValueError`` for:

* Invalid indentation (inconsistent spacing)
* Tab characters in indentation (use spaces only)
* Array length mismatches
* Invalid headers
* Malformed escape sequences
* Blank lines in arrays

See Also
--------

* :doc:`../user_guide/format_specification` - Format details
* :doc:`../guides/error_handling` - Error handling guide
* :doc:`core` - Main API reference
