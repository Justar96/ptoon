Anthropic Claude Integration
============================

.. note::

   **Preview:** Full Anthropic examples are coming soon. For current direct-encode patterns, see :doc:`overview` and :download:`examples/openai_integration.py <../../examples/openai_integration.py>`.

*Full example implementation coming soon*

Introduction
------------

Anthropic Claude models support TOON format with similar integration patterns to OpenAI. Token savings of 30-60% apply equally to Claude.

Prerequisites
-------------

.. code-block:: bash

    pip install pytoon anthropic

Set your API key:

.. code-block:: bash

    export ANTHROPIC_API_KEY="your-api-key-here"

Basic Example
-------------

.. code-block:: python

    import pytoon
    import anthropic

    # Encode data
    data = {"employees": [...]}
    toon_str = pytoon.encode(data)

    # Send to Claude
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Given this data:\n{toon_str}\n\nQuestion: ..."
        }]
    )

    answer = message.content[0].text
    print(answer)

Key Differences from OpenAI
---------------------------

Message Format
~~~~~~~~~~~~~~

Claude uses a different message structure:

.. code-block:: python

    # System message (optional)
    system = "You are a helpful assistant."

    # User message
    messages = [{"role": "user", "content": prompt}]

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system,
        messages=messages
    )

Token Counting
~~~~~~~~~~~~~~

Use Anthropic's token counting API:

.. code-block:: python

    # Accurate token count for Claude
    token_count = client.count_tokens(toon_str)

**Note:** ``pytoon.count_tokens()`` uses OpenAI's tokenizer and provides approximations for Claude.

Supported Models
----------------

* **Claude 3 Opus** - Most capable, highest cost
* **Claude 3 Sonnet** - Balanced performance and cost
* **Claude 3 Haiku** - Fast and cost-effective

Best Practices
--------------

Follow general integration patterns from :doc:`overview`:

* Encode data with ``pytoon.encode()``
* Include in prompt
* Handle errors gracefully
* Measure token savings

Future Updates
--------------

Complete integration guide with full examples will be added in a future release. The example script ``examples/anthropic_integration.py`` is planned.

For now, refer to:

* :doc:`overview` - General integration patterns
* :doc:`openai` - Similar patterns apply to Claude
* `Anthropic API Documentation <https://docs.anthropic.com/>`_

See Also
--------

* :doc:`overview` - General integration guide
* :doc:`/guides/error_handling` - Error handling patterns
* `Anthropic Documentation <https://docs.anthropic.com/>`_
