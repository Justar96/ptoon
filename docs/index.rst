ptoon: Token-Oriented Object Notation for LLMs
================================================

**ptoon** is a Python library for encoding structured data in TOON format, achieving 30-60% token savings compared to JSON for LLM applications.

Key Benefits
------------

* **30-60% token reduction** for structured data
* **Human-readable format** that's easy to understand
* **Preserves semantic information** - data structure is clear
* **Pure Python** with no runtime dependencies

Quick Example
-------------

.. code-block:: python

    import ptoon

    data = {
        "employees": [
            {"id": 1, "name": "Alice", "role": "Engineer"},
            {"id": 2, "name": "Bob", "role": "Designer"}
        ]
    }

    # Encode to TOON format
    toon_str = ptoon.encode(data)
    print(toon_str)
    # Output:
    # employees[2]{id, name, role}:
    #   1, Alice, Engineer
    #   2, Bob, Designer

    # Decode back to Python
    decoded = ptoon.decode(toon_str)
    assert decoded == data

    # Compare token efficiency
    result = ptoon.estimate_savings(data)
    print(f"Token savings: {result['savings_percent']:.1f}%")

Installation
------------

.. code-block:: bash

    # Basic installation
    pip install ptoon

    # With examples (includes OpenAI integration)
    pip install ptoon[examples]

    # With benchmarks
    pip install ptoon[benchmark]

    # Development installation
    pip install -e ".[dev]"

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/installation
   user_guide/quickstart
   user_guide/core_api
   user_guide/format_specification
   user_guide/performance_tips

.. toctree::
   :maxdepth: 2
   :caption: Integration Examples

   integrations/overview
   integrations/openai
   integrations/anthropic
   integrations/google_ai
   integrations/custom_clients

.. toctree::
   :maxdepth: 2
   :caption: Practical Guides

   guides/token_optimization
   guides/data_restructuring
   guides/error_handling
   guides/streaming_responses
   guides/encoding_options

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/encoder
   api/decoder
   api/utils
   api/types

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   faq
   troubleshooting
   benchmarks
   contributing
   changelog

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
-----

* `GitHub Repository <https://github.com/Justar96/toon-py>`_
* `PyPI Package <https://pypi.org/project/ptoon/>`_
* `Issue Tracker <https://github.com/Justar96/toon-py/issues>`_
