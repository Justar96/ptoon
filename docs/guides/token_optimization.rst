Token Optimization
==================

This guide provides strategies for maximizing token savings with TOON.

Understanding Token Efficiency
------------------------------

**Tokens** are the units LLMs use to process text. Each token costs money and consumes context window space. TOON reduces tokens by:

* Eliminating repeated keys in arrays (tabular format)
* Using compact syntax
* Minimizing structural overhead

Optimization Strategies
-----------------------

1. Use Tabular Format
~~~~~~~~~~~~~~~~~~~~~

**Most effective optimization:** Structure data as arrays of uniform objects.

.. code-block:: python

    # Suboptimal: nested individual objects
    data = {
        "employee1": {"id": 1, "name": "Alice", "role": "Engineer"},
        "employee2": {"id": 2, "name": "Bob", "role": "Designer"}
    }

    # Optimal: array of uniform objects
    data = {
        "employees": [
            {"id": 1, "name": "Alice", "role": "Engineer"},
            {"id": 2, "name": "Bob", "role": "Designer"}
        ]
    }

**TOON output (optimal):**

.. code-block:: text

    employees[2]{id, name, role}:
      1, Alice, Engineer
      2, Bob, Designer

**Token savings: 60%+**

2. Choose Optimal Delimiter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    data = {"values": list(range(100))}

    # Comma (default) - good balance
    pytoon.encode(data, options={"delimiter": ","})
    # values[100]: 0, 1, 2, ...

    # Tab - most compact (2-3% savings)
    pytoon.encode(data, options={"delimiter": "\t"})
    # values[100\t]: 0	1	2	...

    # Pipe - when data contains commas
    pytoon.encode(data, options={"delimiter": "|"})
    # values[100|]: 0| 1| 2| ...

3. Shorten Field Names
~~~~~~~~~~~~~~~~~~~~~~

Balance readability with efficiency:

.. code-block:: python

    # Verbose
    data = {"employee_identification_number": 1, "employee_full_name": "Alice"}
    # TOON: employee_identification_number: 1 ...

    # Concise
    data = {"id": 1, "name": "Alice"}
    # TOON: id: 1 ...

**Impact:** Can save 5-10% tokens

4. Remove Unnecessary Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Before
    data = {
        "users": [
            {"id": 1, "name": "Alice", "created_at": "2025-01-01", "updated_at": "2025-01-15", "version": 2},
            # ... more users
        ]
    }

    # After (keep only needed fields)
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            # ... more users
        ]
    }

5. Batch Multiple Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine queries to reuse encoded data:

.. code-block:: python

    # Inefficient: encode for each query
    for question in questions:
        toon_str = pytoon.encode(data)
        prompt = f"Data:\n{toon_str}\n\n{question}"
        # Send to LLM

    # Efficient: encode once
    toon_str = pytoon.encode(data)
    for question in questions:
        prompt = f"Data:\n{toon_str}\n\n{question}"
        # Send to LLM

Measuring Token Savings
------------------------

.. note::

    **Model/Tokenizer Mapping:** Token counting in pytoon uses OpenAI's ``tiktoken`` library with the ``o200k_base`` encoding (GPT-4o and newer models). Counts shown are for OpenAI models. For Anthropic Claude or Google Gemini, use their tokenizers for accuracy; pytoon counts will be approximate.

    While absolute token counts differ across providers, the **relative savings (30-60%) remain consistent**. For provider-specific precision:

    * **OpenAI (GPT-4o, GPT-4o-mini):** Use ``pytoon.count_tokens()`` (default ``o200k_base``)
    * **OpenAI (GPT-4, GPT-3.5):** Use ``pytoon.count_tokens(text, encoding="cl100k_base")``
    * **Anthropic Claude:** Use the ``anthropic`` SDK's token counting
    * **Google Gemini:** Use ``google-generativeai`` SDK's token counting
    * **Llama models:** Use Hugging Face tokenizers

    See :doc:`../api/utils` for more details on tokenizer dependencies.

Use estimate_savings()
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon

    data = {"employees": [...]}  # Your data
    result = pytoon.estimate_savings(data)

    print(f"JSON tokens: {result['json_tokens']}")
    print(f"TOON tokens: {result['toon_tokens']}")
    print(f"Savings: {result['savings']} tokens ({result['savings_percent']:.1f}%)")

Use compare_formats()
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    print(pytoon.compare_formats(data))

Output:

.. code-block:: text

    Format Comparison
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Format  Tokens  Size (bytes)  Savings
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    JSON    108     347           -
    TOON    39      118           63.9% tokens, 66.0% size
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Real-World Examples
-------------------

Example 1: Employee Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    employees = [
        {"id": i, "name": f"Employee {i}", "role": "Engineer", "salary": 100000 + i*1000}
        for i in range(1, 101)
    ]

**Results:**
* JSON: 5,992 tokens
* TOON: 2,162 tokens
* **Savings: 3,830 tokens (63.9%)**

Example 2: Time Series Analytics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    analytics = [
        {"date": f"2025-01-{i:02d}", "views": 1000+i*10, "sales": 50+i}
        for i in range(1, 181)
    ]

**Results:**
* JSON: 10,969 tokens
* TOON: 4,499 tokens
* **Savings: 6,470 tokens (59.0%)**

Example 3: Product Catalog
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    products = [
        {"sku": f"SKU{i:04d}", "name": f"Product {i}", "price": 9.99 + i, "stock": 100}
        for i in range(1, 201)
    ]

**Results:**
* JSON: 12,450 tokens
* TOON: 4,820 tokens
* **Savings: 7,630 tokens (61.3%)**

Cost Analysis
-------------

Per-Request Savings
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Calculate cost savings per request
    result = pytoon.estimate_savings(data)
    
    # GPT-4o-mini pricing: $0.60 per 1M input tokens
    cost_per_million = 0.60
    
    json_cost = result['json_tokens'] * cost_per_million / 1_000_000
    toon_cost = result['toon_tokens'] * cost_per_million / 1_000_000
    savings_per_request = json_cost - toon_cost
    
    print(f"Savings per request: ${savings_per_request:.6f}")

Scale Analysis
~~~~~~~~~~~~~~

.. code-block:: python

    # Project savings at scale
    requests_per_day = 1000
    savings_per_request = 0.0023  # from above

    daily_savings = savings_per_request * requests_per_day
    monthly_savings = daily_savings * 30
    annual_savings = daily_savings * 365

    print(f"Daily savings: ${daily_savings:.2f}")
    print(f"Monthly savings: ${monthly_savings:.2f}")
    print(f"Annual savings: ${annual_savings:.2f}")

**Example output:**
* Daily: $2.30
* Monthly: $69
* Annual: $839

Advanced Techniques
-------------------

Dynamic Format Selection
~~~~~~~~~~~~~~~~~~~~~~~~

Choose format based on data characteristics:

.. code-block:: python

    def choose_format(data):
        result = pytoon.estimate_savings(data)
        
        if result['savings_percent'] > 30:
            return "toon", pytoon.encode(data)
        else:
            return "json", json.dumps(data)

    format_type, encoded = choose_format(data)
    print(f"Using {format_type} format")

Hybrid Approach
~~~~~~~~~~~~~~~

Mix TOON and JSON based on use case:

.. code-block:: python

    # TOON for large data in prompts
    data_toon = pytoon.encode(large_dataset)

    # JSON for function calling schemas
    functions = [{
        "name": "get_data",
        "parameters": {"type": "object", ...}  # JSON
    }]

    prompt = f"Data:\n{data_toon}\n\nQuestion: ..."

Best Practices Checklist
-------------------------

Before deploying TOON:

☑ **Measured:** Run ``estimate_savings()`` on representative data
☑ **Verified:** Savings >30% for your use case
☑ **Tested:** Confirmed LLM understands TOON format
☑ **Optimized:** Restructured data for tabular format where possible
☑ **Monitored:** Set up cost tracking
☑ **Documented:** Noted why TOON was chosen

See Also
--------

* :doc:`/user_guide/performance_tips` - Performance optimization
* :doc:`/guides/encoding_options` - Encoding options guide
* :doc:`/user_guide/core_api` - Core API documentation
* :doc:`/benchmarks` - Benchmark results
