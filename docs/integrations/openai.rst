OpenAI Integration
==================

This guide shows how to use TOON with OpenAI's GPT models for token-efficient LLM applications.

Introduction
------------

OpenAI is the most popular LLM provider. TOON works seamlessly with the OpenAI API and typically achieves **30-60% token savings** compared to JSON, resulting in proportional cost savings.

Prerequisites
-------------

Install dependencies:

.. code-block:: bash

    pip install pytoon[examples]

This installs:
* ``pytoon`` - TOON encoder/decoder
* ``openai`` - OpenAI Python SDK
* ``tiktoken`` - Token counting library

Set your API key:

.. code-block:: bash

    export OPENAI_API_KEY="your-api-key-here"

Basic Example
-------------

Simple query with TOON-encoded data:

.. code-block:: python

    import pytoon
    import openai

    # Your data
    employee = {
        "name": "Alice",
        "role": "Engineer",
        "salary": 120000,
        "years": 3
    }

    # Encode to TOON
    toon_str = pytoon.encode(employee)
    print("TOON format:")
    print(toon_str)
    # Output:
    # name: Alice
    # role: Engineer
    # salary: 120000
    # years: 3

    # Send to OpenAI
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Given this employee data:\n{toon_str}\n\nWhat is their role?"
        }]
    )

    answer = response.choices[0].message.content
    print(f"Answer: {answer}")
    # Output: Answer: Engineer

Token Comparison
----------------

Compare JSON vs TOON token counts:

.. code-block:: python

    import pytoon
    import tiktoken
    import json

    # Sample data: 100 employees
    employees = [
        {"id": i, "name": f"Employee {i}", "role": "Engineer", "salary": 100000 + i*1000}
        for i in range(1, 101)
    ]
    data = {"employees": employees}

    # JSON format
    json_str = json.dumps(data, indent=2)
    
    # TOON format
    toon_str = pytoon.encode(data)

    # Count tokens (GPT-4o uses o200k_base)
    enc = tiktoken.get_encoding("o200k_base")
    json_tokens = len(enc.encode(json_str))
    toon_tokens = len(enc.encode(toon_str))

    print(f"JSON: {json_tokens} tokens")
    print(f"TOON: {toon_tokens} tokens")
    print(f"Savings: {json_tokens - toon_tokens} tokens ({(1-toon_tokens/json_tokens)*100:.1f}%)")

**Expected output:**

.. code-block:: text

    JSON: 5,992 tokens
    TOON: 2,162 tokens
    Savings: 3,830 tokens (63.9%)

**TOON format (excerpt):**

.. code-block:: text

    employees[100]{id, name, role, salary}:
      1, Employee 1, Engineer, 101000
      2, Employee 2, Engineer, 102000
      ...

**JSON format (excerpt):**

.. code-block:: json

    {
      "employees": [
        {"id": 1, "name": "Employee 1", "role": "Engineer", "salary": 101000},
        {"id": 2, "name": "Employee 2", "role": "Engineer", "salary": 102000},
        ...
      ]
    }

Notice how field names (``id``, ``name``, ``role``, ``salary``) appear once in TOON vs repeated 100 times in JSON.

RAG Example
-----------

Real-world use case: question answering over a dataset.

.. code-block:: python

    import pytoon
    import openai

    # Simulate retrieved documents
    employees = [
        {"id": 1, "name": "Alice", "role": "Engineer", "salary": 120000},
        {"id": 2, "name": "Bob", "role": "Designer", "salary": 100000},
        {"id": 3, "name": "Carol", "role": "Manager", "salary": 150000},
    ]

    # Encode to TOON
    toon_str = pytoon.encode({"employees": employees})

    # Ask multiple questions
    client = openai.OpenAI()
    questions = [
        "Who has the highest salary?",
        "How many employees are there?",
        "What is Alice's role?"
    ]

    for question in questions:
        prompt = f"Given this data:\n{toon_str}\n\n{question}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.choices[0].message.content
        print(f"Q: {question}")
        print(f"A: {answer}\n")

**Cost Analysis:**

.. code-block:: python

    # Tokens per query (data + question)
    json_tokens = 108 + 10  # 118 total
    toon_tokens = 39 + 10   # 49 total
    
    # At 3 questions
    json_total = 118 * 3   # 354 tokens
    toon_total = 49 * 3    # 147 tokens
    
    # Savings: 207 tokens (58.5%)

Error Handling
--------------

Handle malformed responses gracefully:

.. code-block:: python

    import pytoon
    import openai
    import json

    def query_with_fallback(data, question):
        """Query LLM with TOON, handle errors gracefully."""
        client = openai.OpenAI()
        
        # Encode data
        try:
            toon_str = pytoon.encode(data)
        except (TypeError, ValueError) as e:
            print(f"Encoding error: {e}, falling back to JSON")
            toon_str = json.dumps(data, indent=2)
        
        # Send to LLM
        prompt = f"Data:\n{toon_str}\n\n{question}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.choices[0].message.content
        
        # Try parsing as structured data
        try:
            return pytoon.decode(answer)
        except ValueError:
            pass
        
        try:
            return json.loads(answer)
        except ValueError:
            pass
        
        # Return as text
        return answer

    # Usage
    data = {"users": [{"id": 1, "name": "Alice"}]}
    result = query_with_fallback(data, "What is the user's name?")
    print(result)

Best Practices
--------------

Prompt Engineering
~~~~~~~~~~~~~~~~~~

The LLM understands TOON without explanation:

.. code-block:: python

    # Simple (usually sufficient)
    prompt = f"Given this data:\n{toon_str}\n\nQuestion: ..."

    # Explicit (if needed)
    prompt = f"Given this data in TOON format:\n{toon_str}\n\nQuestion: ..."

To request TOON output:

.. code-block:: python

    prompt = "List employees. Format: TOON"
    # or
    prompt = "List employees in TOON format: id, name, role"

Token Optimization
~~~~~~~~~~~~~~~~~~

Use tabular format for maximum savings:

.. code-block:: python

    # Good: uniform objects → tabular format
    data = {
        "products": [
            {"id": 1, "name": "Widget", "price": 19.99},
            {"id": 2, "name": "Gadget", "price": 29.99}
        ]
    }
    # Output: products[2]{id, name, price}:
    #           1, Widget, 19.99
    #           2, Gadget, 29.99

Choose appropriate delimiter:

.. code-block:: python

    # If data contains commas, use pipe
    options = {"delimiter": "|"}
    toon_str = pytoon.encode(data, options=options)

Cost Management
~~~~~~~~~~~~~~~

Monitor token usage:

.. code-block:: python

    response = client.chat.completions.create(...)
    
    usage = response.usage
    print(f"Input tokens: {usage.prompt_tokens}")
    print(f"Output tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")

Calculate savings:

.. code-block:: python

    result = pytoon.estimate_savings(data)
    
    # At $0.60 per 1M input tokens (gpt-4o-mini)
    json_cost = result['json_tokens'] * 0.60 / 1_000_000
    toon_cost = result['toon_tokens'] * 0.60 / 1_000_000
    savings = json_cost - toon_cost
    
    print(f"Savings per request: ${savings:.4f}")

Streaming Responses
-------------------

TOON works with streaming:

.. code-block:: python

    import pytoon
    import openai

    client = openai.OpenAI()
    data = {"employees": [...]}
    toon_str = pytoon.encode(data)

    # Stream response
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Data:\n{toon_str}\n\nQuestion: ..."}],
        stream=True
    )

    chunks = []
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            chunks.append(content)

    # Parse complete response
    full_response = "".join(chunks)
    try:
        result = pytoon.decode(full_response)
    except ValueError:
        result = full_response

Function Calling
----------------

**Important:** Use JSON for function calling, not TOON.

OpenAI's function calling requires strict JSON schemas. Use TOON for data in prompts, JSON for function definitions:

.. code-block:: python

    # TOON for data
    data_toon = pytoon.encode({"employees": [...]})

    # JSON for function schema
    functions = [{
        "name": "get_employee",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer"}
            }
        }
    }]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Data:\n{data_toon}\n\nGet employee 1"}],
        functions=functions,
        function_call="auto"
    )

Model-Specific Notes
--------------------

GPT-4o
~~~~~~

* Tokenizer: ``o200k_base``
* Excellent with TOON format
* Best for large datasets

.. code-block:: python

    tokens = pytoon.count_tokens(toon_str, encoding="o200k_base")

GPT-4
~~~~~

* Tokenizer: ``o200k_base``
* Works well with TOON

GPT-3.5-turbo
~~~~~~~~~~~~~

* Tokenizer: ``cl100k_base``
* Also supports TOON

.. code-block:: python

    tokens = pytoon.count_tokens(toon_str, encoding="cl100k_base")

Performance Metrics
-------------------

Based on benchmark results:

**Employee Records (100 items):**
* JSON: 5,992 tokens
* TOON: 2,162 tokens  
* Savings: 63.9%

**Time Series (180 days):**
* JSON: 10,969 tokens
* TOON: 4,499 tokens
* Savings: 59.0%

**E-Commerce Orders (50 orders):**
* JSON: 10,654 tokens
* TOON: 7,046 tokens
* Savings: 33.9%

Complete Example
----------------

Full working script:

.. code-block:: python

    #!/usr/bin/env python3
    """Complete OpenAI + TOON integration example."""

    import pytoon
    import openai
    import json

    def main():
        # Sample data
        employees = [
            {"id": 1, "name": "Alice", "role": "Engineer", "salary": 120000},
            {"id": 2, "name": "Bob", "role": "Designer", "salary": 100000},
            {"id": 3, "name": "Carol", "role": "Manager", "salary": 150000}
        ]
        data = {"employees": employees}

        # Compare formats
        json_str = json.dumps(data, indent=2)
        toon_str = pytoon.encode(data)

        print("JSON format:")
        print(json_str)
        print(f"\nJSON tokens: {pytoon.count_tokens(json_str)}")

        print("\nTOON format:")
        print(toon_str)
        print(f"\nTOON tokens: {pytoon.count_tokens(toon_str)}")

        # Query with TOON
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Given:\n{toon_str}\n\nWho has the highest salary?"
            }]
        )

        print(f"\nAnswer: {response.choices[0].message.content}")
        print(f"Tokens used: {response.usage.total_tokens}")

    if __name__ == "__main__":
        main()

See Also
--------

* `examples/openai_integration.py <https://github.com/Justar96/pytoon/blob/main/examples/openai_integration.py>`_ - Full example script
* :doc:`/guides/token_optimization` - Token optimization guide
* :doc:`/guides/error_handling` - Error handling patterns
* :doc:`/guides/streaming_responses` - Streaming guide
* `OpenAI API Documentation <https://platform.openai.com/docs>`_
