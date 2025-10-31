Utilities API Reference
=======================

This page documents utility functions for token counting and analysis.

Utility Functions
-----------------

.. automodule:: ptoon.utils
   :members:
   :undoc-members:
   :noindex:

Requirements
------------

Token counting utilities require ``tiktoken``:

.. code-block:: bash

    pip install tiktoken

Or install with benchmark dependencies:

.. code-block:: bash

    pip install ptoon[benchmark]

If ``tiktoken`` is unavailable, ``ptoon.count_tokens`` raises ``RuntimeError("tiktoken is required for token counting. Install with: pip install tiktoken or pip install ptoon[benchmark]")``.

.. note::

    **Tokenizer Dependence:** The ``count_tokens()`` function uses OpenAI's ``tiktoken`` library with the ``o200k_base`` encoding (used by GPT-4o and newer models). Token counts will vary when using different tokenizers from other LLM providers (Anthropic, Google, etc.).

    For precise token counting with other providers:

    * **Anthropic Claude:** Use their ``anthropic`` SDK's tokenization
    * **Google Gemini:** Use ``google-generativeai`` SDK's token counting
    * **Llama models:** Use the Hugging Face tokenizers

    The token savings percentages (30-60%) are generally consistent across providers, but absolute token counts will differ.

Examples
--------

Count Tokens
~~~~~~~~~~~~

.. code-block:: python

    import ptoon

    text = "Hello, world!"
    token_count = ptoon.count_tokens(text)
    print(f"Tokens: {token_count}")

    # With specific encoding
    token_count = ptoon.count_tokens(text, encoding="cl100k_base")

Estimate Savings
~~~~~~~~~~~~~~~~

.. code-block:: python

    data = {"users": [{"id": 1, "name": "Alice"}]}
    result = ptoon.estimate_savings(data)

    print(f"JSON tokens: {result['json_tokens']}")
    print(f"TOON tokens: {result['toon_tokens']}")
    print(f"Savings: {result['savings_percent']:.1f}%")

Compare Formats
~~~~~~~~~~~~~~~

.. code-block:: python

    print(ptoon.compare_formats(data))

    # Output:
    # Format Comparison
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Format  Tokens  Size (bytes)  Savings
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # JSON    28      89            -
    # TOON    18      53            35.7% tokens
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

See Also
--------

* :doc:`../user_guide/core_api` - Core API guide
* :doc:`../guides/token_optimization` - Token optimization
* :doc:`core` - Main API reference
