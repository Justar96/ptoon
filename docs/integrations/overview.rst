Integration Overview
====================

TOON works with any LLM provider that accepts text input. This guide explains the general integration pattern.

General Integration Pattern
---------------------------

Basic Flow
~~~~~~~~~~

1. **Encode data:** ``toon_str = pytoon.encode(data)``
2. **Include in prompt:** ``f"Given this data:\n{toon_str}\n\nQuestion: ..."``
3. **Send to LLM API:** Use provider's SDK/API
4. **Parse response:** Decode if response is TOON, otherwise handle as text

Example
~~~~~~~

.. code-block:: python

    import pytoon

    # 1. Encode your data
    data = {"employees": [...]}
    toon_str = pytoon.encode(data)

    # 2. Construct prompt
    prompt = f"""
    Given this employee data:
    {toon_str}

    Who has the highest salary?
    """

    # 3. Send to LLM (example with OpenAI)
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # 4. Parse response
    answer = response.choices[0].message.content
    print(answer)

Key Principles
~~~~~~~~~~~~~~

* **TOON is just a string format** - no special LLM support needed
* **Works with any text-based API** - OpenAI, Anthropic, Google, local models
* **LLMs understand TOON without training** - the format is intuitive
* **No modifications to API calls** - just change the prompt content

Integration Steps
-----------------

1. Prepare Your Data
~~~~~~~~~~~~~~~~~~~~

Structure data as dict or list:

.. code-block:: python

    data = {
        "products": [
            {"id": 1, "name": "Widget", "price": 19.99},
            {"id": 2, "name": "Gadget", "price": 29.99}
        ]
    }

**Optimization tips:**

* Use uniform objects for tabular format
* Remove unnecessary fields
* Consider shorter field names

2. Encode to TOON
~~~~~~~~~~~~~~~~~

.. code-block:: python

    toon_str = pytoon.encode(data)

With options:

.. code-block:: python

    options = {"delimiter": "|"}  # If data contains commas
    toon_str = pytoon.encode(data, options=options)

3. Construct Prompt
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    prompt = f"""
    Here is product data:
    {toon_str}

    Please find the most expensive product.
    """

**Optional:** Mention format explicitly (though usually unnecessary):

.. code-block:: python

    prompt = f"""
    Here is product data in TOON format:
    {toon_str}

    Please find the most expensive product.
    """

4. Send to LLM
~~~~~~~~~~~~~~

Use your provider's SDK:

.. code-block:: python

    # OpenAI example
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Anthropic example
    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": prompt}]
    )

5. Handle Response
~~~~~~~~~~~~~~~~~~

Try parsing as TOON first, fallback to text:

.. code-block:: python

    def safe_parse_response(text):
        # Try TOON
        try:
            return pytoon.decode(text)
        except ValueError:
            pass
        
        # Try JSON
        try:
            return json.loads(text)
        except ValueError:
            pass
        
        # Return as text
        return text

    result = safe_parse_response(response.choices[0].message.content)

Supported Providers
-------------------

TOON works with all major LLM providers:

* **OpenAI** - GPT-4, GPT-4o, GPT-3.5
* **Anthropic** - Claude 3 (Opus, Sonnet, Haiku)
* **Google AI** - Gemini Pro, Ultra
* **Custom/Local** - Any model accepting text

Provider-Specific Guides:

* :doc:`openai` - Complete OpenAI integration guide
* :doc:`anthropic` - Anthropic Claude integration
* :doc:`google_ai` - Google AI (Gemini) integration
* :doc:`custom_clients` - Local models and custom APIs

Token Counting
--------------

Each provider uses different tokenizers:

OpenAI
~~~~~~

.. code-block:: python

    import pytoon

    # Use o200k_base for GPT-4o/GPT-4
    tokens = pytoon.count_tokens(toon_str, encoding="o200k_base")

Anthropic
~~~~~~~~~

.. code-block:: python

    # Use Anthropic's tokenizer for accurate counts
    import anthropic
    client = anthropic.Anthropic()
    tokens = client.count_tokens(toon_str)

Google AI
~~~~~~~~~

.. code-block:: python

    # Use model's count_tokens method
    import google.generativeai as genai
    model = genai.GenerativeModel('gemini-pro')
    tokens = model.count_tokens(toon_str).total_tokens

**Note:** ``pytoon.count_tokens()`` uses OpenAI's tokenizer by default, providing approximations for other providers.

Best Practices
--------------

1. Always Measure Token Savings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    result = pytoon.estimate_savings(data)
    if result['savings_percent'] < 20:
        # Consider using JSON instead
        use_json = True

2. Test with Small Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Test with simple data first
    test_data = {"test": [{"a": 1}, {"a": 2}]}
    toon_str = pytoon.encode(test_data)
    # Verify LLM understands it

3. Implement Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    try:
        toon_str = pytoon.encode(data)
    except (TypeError, ValueError) as e:
        # Fallback to JSON
        toon_str = json.dumps(data)

4. Monitor API Costs
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Track token usage
    json_tokens = pytoon.count_tokens(json.dumps(data))
    toon_tokens = pytoon.count_tokens(pytoon.encode(data))
    
    savings_per_request = json_tokens - toon_tokens
    monthly_savings = savings_per_request * requests_per_month

Common Patterns
---------------

RAG (Retrieval-Augmented Generation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Encode retrieved documents
    documents = [{"title": "...", "content": "..."}, ...]
    toon_str = pytoon.encode({"documents": documents})

    prompt = f"Given these documents:\n{toon_str}\n\nAnswer: {question}"

Data Analysis
~~~~~~~~~~~~~

.. code-block:: python

    # Encode analytics data
    analytics = [{"date": "...", "views": 100}, ...]
    toon_str = pytoon.encode({"analytics": analytics})

    prompt = f"Analyze trends in:\n{toon_str}"

Structured Output
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Request TOON response
    prompt = "List top 3 products. Respond in TOON format."
    
    # Parse response
    try:
        result = pytoon.decode(response)
    except ValueError:
        # Handle non-TOON response
        pass

Troubleshooting
---------------

**LLM doesn't understand TOON**

* Add format explanation to prompt
* Provide an example
* Usually not needed - format is intuitive

**Token savings lower than expected**

* Check data structure (uniform objects work best)
* Use ``pytoon.estimate_savings()`` to verify
* Consider restructuring data

**Decoding fails**

* Implement fallback parsing (TOON → JSON → text)
* See :doc:`/guides/error_handling`

See Also
--------

* :doc:`openai` - OpenAI integration examples
* :doc:`/guides/error_handling` - Error handling patterns
* :doc:`/guides/token_optimization` - Optimization strategies
* :doc:`/troubleshooting` - Common issues and solutions
