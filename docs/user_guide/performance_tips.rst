Performance Tips
================

This guide covers optimization strategies for maximizing TOON's benefits.

Token Efficiency
----------------

Optimal Data Structures
~~~~~~~~~~~~~~~~~~~~~~~~

**Best:** Arrays of uniform objects (tabular format)

.. code-block:: python

    # Excellent for TOON (63.9% savings)
    employees = [
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Designer"},
        # ... 98 more
    ]

**Good:** Repeated structures

.. code-block:: python

    # Good for TOON (40-50% savings)
    time_series = [
        {"date": "2025-01-01", "views": 1000, "sales": 50},
        {"date": "2025-01-02", "views": 1200, "sales": 60},
        # ...
    ]

**Moderate:** Nested structures

.. code-block:: python

    # Moderate savings (30-40%)
    orders = [
        {
            "id": 1,
            "customer": {"name": "Alice", "email": "..."},
            "items": [{"sku": "A", "qty": 2}]
        }
    ]

When TOON Shines
~~~~~~~~~~~~~~~~

**High Savings (>50%):**

* Uniform tabular data
* Large datasets (>100 tokens)
* Repeated field names
* Time-series data
* Catalog/inventory data

**Example:** 100 employee records

* JSON: 5,992 tokens
* TOON: 2,162 tokens
* **Savings: 63.9%**

When to Use JSON Instead
~~~~~~~~~~~~~~~~~~~~~~~~

**Use JSON when:**

* Tiny payloads (<100 tokens) - overhead not worth it
* Function calling / tool use - requires strict JSON schema
* Streaming partial responses - need incremental parsing
* Highly heterogeneous data - no repeated structure

Encoding Performance
--------------------

Speed Characteristics
~~~~~~~~~~~~~~~~~~~~~

* TOON encoding: ~0.12x speed of JSON (slower)
* TOON decoding: ~0.10x speed of JSON (slower)
* Reason: Python implementation vs C-optimized json module

Why It's Worth It
~~~~~~~~~~~~~~~~~

**Token count is the primary cost driver:**

.. code-block:: python

    # Example cost analysis
    json_tokens = 6000
    toon_tokens = 2200  # 63% savings
    
    # At $0.60 per 1M tokens (gpt-4o-mini input)
    json_cost = 6000 * 0.60 / 1_000_000  # $0.0036
    toon_cost = 2200 * 0.60 / 1_000_000  # $0.0013
    
    # Savings per request: $0.0023
    # At 1,000 requests/day: $2.30/day = $69/month = $839/year

**Encoding overhead is negligible:**

* Encoding: ~1-10ms
* LLM inference: ~100-1000ms+
* **Net result: TOON is faster end-to-end**

Optimization Strategies
~~~~~~~~~~~~~~~~~~~~~~~

**1. Reuse encoder instances (automatic):**

.. code-block:: python

    # Encoders are cached internally
    toon_str = pytoon.encode(data)  # Creates encoder
    toon_str = pytoon.encode(data2)  # Reuses encoder

**2. Pre-encode static data:**

.. code-block:: python

    # Encode once, reuse many times
    static_data_toon = pytoon.encode(static_data)
    
    for query in queries:
        prompt = f"Data:\n{static_data_toon}\n\nQuestion: {query}"
        # Use prompt...

**3. Choose appropriate delimiter:**

.. code-block:: python

    # Tab is most compact (2-3% savings)
    options = {"delimiter": "\t"}
    toon_str = pytoon.encode(data, options=options)

Token Counting
--------------

.. note::

    **Tokenizer Variance:** Token counts shown use OpenAI's ``o200k_base`` encoding (GPT-4o, GPT-4o-mini). For Anthropic Claude or Google Gemini, use their respective tokenizers for accuracy. pytoon's built-in counting provides approximations for non-OpenAI models, but relative savings (30-60%) remain consistent across providers.

Use Built-in Utilities
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon

    # Quick comparison
    result = pytoon.estimate_savings(data)
    if result['savings_percent'] > 30:
        use_toon = True

    # Detailed comparison
    print(pytoon.compare_formats(data))

Cache Token Counts
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # For repeated data, cache the count
    token_cache = {}
    
    def get_token_count(data_id, data):
        if data_id not in token_cache:
            toon_str = pytoon.encode(data)
            token_cache[data_id] = pytoon.count_tokens(toon_str)
        return token_cache[data_id]

Real-World Cost Analysis
------------------------

Example: Employee Database
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario:**
* 100 employee records per query
* 1,000 queries per day
* OpenAI GPT-4o-mini ($0.60 per 1M input tokens)

**JSON:**
* Tokens per query: 5,992
* Daily tokens: 5,992,000
* Daily cost: $3.60
* Monthly cost: $108
* Annual cost: $1,314

**TOON:**
* Tokens per query: 2,162
* Daily tokens: 2,162,000
* Daily cost: $1.30
* Monthly cost: $39
* Annual cost: $468

**Savings: $846/year** (64% reduction)

Break-Even Analysis
~~~~~~~~~~~~~~~~~~~

**When does encoding overhead pay off?**

Typically after first use:

* Encoding overhead: 1-10ms one-time
* Token savings: applies to every LLM call
* Inference time reduction: proportional to token savings

**Threshold:** Any dataset >100 tokens usually benefits

Benchmarking Your Data
----------------------

Measure Before Optimizing
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon
    import json

    # Your actual data
    data = {...}

    # Get detailed comparison
    print(pytoon.compare_formats(data))

    # Programmatic decision
    result = pytoon.estimate_savings(data)
    
    if result['savings_percent'] > 30:
        print("✓ TOON recommended")
        use_format = "toon"
    else:
        print("✗ Consider JSON")
        use_format = "json"

Test with Different Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Try different delimiters
    for delim in [",", "|", "\t"]:
        opts = {"delimiter": delim}
        toon_str = pytoon.encode(data, options=opts)
        toon_tokens = pytoon.count_tokens(toon_str)
        print(f"{delim}: {toon_tokens} tokens")

Best Practices Summary
----------------------

**Do:**

✓ Measure token savings with your actual data
✓ Use tabular format when possible (structure data uniformly)
✓ Pre-encode and cache static data
✓ Choose delimiter based on data content
✓ Monitor costs over time

**Don't:**

✗ Assume all data benefits equally
✗ Over-optimize readability for tiny gains
✗ Ignore encoding overhead for tiny payloads
✗ Use TOON for function calling (use JSON)

Checklist
~~~~~~~~~

Before using TOON in production:

1. [ ] Measured token savings on representative data
2. [ ] Verified savings >30%
3. [ ] Tested with actual LLM API
4. [ ] Implemented error handling
5. [ ] Monitored costs
6. [ ] Documented decision

See Also
--------

* :doc:`/benchmarks` - Detailed benchmark results
* :doc:`/guides/token_optimization` - Token optimization strategies
* :doc:`core_api` - API documentation
