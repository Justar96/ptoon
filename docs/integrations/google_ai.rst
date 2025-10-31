Google AI (Gemini) Integration
===============================

.. note::

   **Preview:** Full Gemini examples are coming soon. For current guidance, start with :doc:`overview` and :download:`examples/openai_integration.py <../../examples/openai_integration.py>` for the direct-encode workflow.

*Full example implementation coming soon*

Introduction
------------

Google's Gemini models support TOON format with the same token efficiency benefits as other LLM providers.

Prerequisites
-------------

.. code-block:: bash

    pip install pytoon google-generativeai

Set your API key:

.. code-block:: bash

    export GOOGLE_API_KEY="your-api-key-here"

Basic Example
-------------

.. code-block:: python

    import pytoon
    import google.generativeai as genai

    # Configure API
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    # Encode data
    data = {"employees": [...]}
    toon_str = pytoon.encode(data)

    # Send to Gemini
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f"Given this data:\n{toon_str}\n\nQuestion: ..."
    )

    answer = response.text
    print(answer)

Token Counting
--------------

Use Gemini's token counting method:

.. code-block:: python

    model = genai.GenerativeModel('gemini-pro')
    token_count = model.count_tokens(toon_str).total_tokens

**Note:** ``pytoon.count_tokens()`` uses OpenAI's tokenizer and provides approximations for Gemini.

Supported Models
----------------

* **Gemini Pro** - Balanced performance
* **Gemini Ultra** - Most capable (when available)

Best Practices
--------------

Follow general integration patterns from :doc:`overview`:

* Encode data with ``pytoon.encode()``
* Include in prompt
* Handle errors gracefully
* Measure token savings

Multimodal Applications
-----------------------

Gemini supports multimodal inputs. TOON can be used for structured text data alongside images:

.. code-block:: python

    # Combine TOON data with images
    data_toon = pytoon.encode({"products": [...]})
    
    response = model.generate_content([
        "Analyze this product data and image:",
        data_toon,
        image_data
    ])

Future Updates
--------------

Complete integration guide with full examples will be added in a future release. The example script ``examples/google_ai_integration.py`` is planned.

For now, refer to:

* :doc:`overview` - General integration patterns
* :doc:`openai` - Similar patterns apply to Gemini
* `Google AI Documentation <https://ai.google.dev/>`_

See Also
--------

* :doc:`overview` - General integration guide
* :doc:`/guides/error_handling` - Error handling patterns
* `Google AI Documentation <https://ai.google.dev/>`_
