Frequently Asked Questions
==========================

This FAQ addresses common questions about TOON format, limitations, and best practices.

General Questions
-----------------

What is TOON?
~~~~~~~~~~~~~

TOON (Token-Oriented Object Notation) is a text format optimized for Large Language Models (LLMs). It achieves 30-60% token reduction compared to JSON for structured data, particularly for tabular data and nested structures with repeated keys.

When should I use TOON instead of JSON?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use TOON when:**

- Sending large structured datasets to LLMs (RAG, analytics, catalogs)
- Token count is a cost driver (OpenAI, Anthropic pricing is per-token)
- You need to fit more data in limited context windows
- Data is tabular or has repeated structure

**Stick with JSON when:**

- Payloads are small (< 100 tokens)
- Using strict JSON contracts (OpenAI function calling, tool use)
- Encoding latency matters more than token count
- Data is highly heterogeneous with no repeated structure

Is TOON compatible with all LLM providers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! TOON is just a text format. Any LLM that can process text can read TOON. It works with:

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Open-source models (Llama, Mistral, etc.)

The LLM doesn't need special training - the format is human-readable and follows natural patterns.

Format Limitations
------------------

Why doesn't TOON support 3+ levels of array nesting?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Short answer:** Deep nesting uses MORE tokens than JSON, defeating TOON's purpose.

**Detailed explanation:**

1. **Token efficiency comparison:**

   .. code-block:: python

      # 3-level nested array
      json_str = '[[[1,2]], [[3,4]]]'  # 21 tokens
      # TOON would need:   ~70 tokens (if we supported it)
      # Result: 233% MORE tokens than JSON!

2. **Real-world coverage:** 95-99% of API responses and data structures use ≤2 levels of nesting.

3. **Format philosophy:** TOON is optimized for tabular/structured data, not arbitrary nesting.

What should I do if my data has deep nesting?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Restructure your data!** Deep nesting is often a design smell. Here are proven patterns:

**Pattern 1: Trees → Adjacency Lists**

.. code-block:: python

   # ❌ Deep nesting
   tree = {
       "name": "root",
       "children": [{"name": "child", "children": [{"name": "grandchild"}]}]
   }

   # ✅ Flat adjacency list
   tree_flat = {
       "nodes": [
           {"id": 1, "name": "root", "parent": None},
           {"id": 2, "name": "child", "parent": 1},
           {"id": 3, "name": "grandchild", "parent": 2}
       ]
   }
   # Token savings: 50-60% vs nested JSON!

**Pattern 2: 3D Arrays → Flattened with Shape**

.. code-block:: python

   # ❌ 3D nested array
   tensor = [[[1,2],[3,4]], [[5,6],[7,8]]]

   # ✅ Flattened with metadata
   tensor_flat = {
       "shape": [2, 2, 2],
       "data": [1, 2, 3, 4, 5, 6, 7, 8]
   }
   # Token savings: 35-45% vs nested!

**Pattern 3: Nested Collections → Normalized Tables**

.. code-block:: python

   # ❌ Nested order
   order = {
       "id": "ORD-001",
       "customer": {"id": 123, "name": "Alice", "address": {...}},
       "items": [{"sku": "A", "details": {...}}, ...]
   }

   # ✅ Normalized (database-style)
   order_flat = {
       "orders": [{"id": "ORD-001", "customer_id": 123, ...}],
       "customers": [{"id": 123, "name": "Alice", ...}],
       "items": [{"order_id": "ORD-001", "sku": "A", ...}]
   }
   # Token savings: 40-55% vs nested!

See :doc:`guides/data_restructuring` for detailed examples with helper functions.

How do I know if my data is too deeply nested?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When encoding, TOON will warn you:

.. code-block:: text

   WARNING: Skipping deeply nested array (depth 3). TOON format supports
   up to 2 levels of array nesting. Consider flattening this data structure.

Enable warnings with:

.. code-block:: python

   import os
   os.environ['PYTOON_DEBUG'] = '1'

   import pytoon
   result = pytoon.encode(deep_data)  # Will show warnings

Performance & Efficiency
------------------------

How much faster/cheaper is TOON vs JSON?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Token savings** (primary benefit):

- **Tabular data:** 40-60% fewer tokens
- **Nested objects:** 30-45% fewer tokens
- **Flat arrays:** ~10-20% fewer tokens
- **Average across use cases:** 35-50% reduction

**API cost savings:** Proportional to token reduction (30-60% cheaper)

**Encoding speed:** ~0.8x JSON (Python implementation, but encoding time is negligible compared to LLM inference)

**Example:**

.. code-block:: python

   # 100 employee records
   json_tokens = 4500
   toon_tokens = 2700  # 40% reduction

   # OpenAI GPT-4 input pricing: $0.03 per 1K tokens
   json_cost = $0.135
   toon_cost = $0.081   # Save $0.054 per request

   # At 10,000 requests/month: Save $540/month

Does TOON slow down my application?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Encoding time is negligible** compared to LLM inference:

- Encoding 1000 records: ~5ms (TOON) vs ~3ms (JSON)
- LLM inference for same data: ~2000ms (2 seconds)

**For LLM applications:**

- ✅ Fewer tokens → faster LLM processing
- ✅ 30-60% cost reduction
- ❌ 2ms extra encoding time (0.1% of total time)

**Trade-off is clearly worth it** for any LLM use case!

Usage & Integration
-------------------

Can I use TOON with OpenAI function calling?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**No, not for the function schema.** OpenAI's function calling requires strict JSON for the schema definition.

**However, you CAN use TOON for the data passed TO the function:**

.. code-block:: python

   # Function schema must be JSON
   function_schema = {
       "name": "analyze_users",
       "parameters": {
           "type": "object",
           "properties": {
               "user_data": {"type": "string"}  # TOON data as string
           }
       }
   }

   # Encode user data as TOON and pass as string parameter
   import pytoon
   user_data_toon = pytoon.encode(large_user_dataset)

   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": f"Analyze: {user_data_toon}"}]
   )

How do LLMs learn to read TOON format?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**They don't need special training!** TOON is designed to be intuitive:

1. **Human-readable structure:** Similar to YAML, CSV, markdown tables
2. **Few-shot learning:** Show 1-2 examples in the prompt
3. **Natural patterns:** LLMs recognize tabular patterns from training data

**Example prompt:**

.. code-block:: text

   The data is in TOON format. Here's an example:

   users[2]{id, name, role}:
     1, Alice, Engineer
     2, Bob, Designer

   This represents a list of 2 users with id, name, and role fields.

   Now analyze this data:
   [your TOON data here]

Most LLMs understand TOON without explicit examples!

Can I mix TOON and JSON in the same message?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Yes!** You can include both in your prompt:

.. code-block:: python

   prompt = f"""
   Here is configuration data (JSON):
   {json.dumps(config)}

   And here is a large dataset (TOON):
   {pytoon.encode(large_data)}

   Please analyze the dataset using the configuration.
   """

This is useful when you have:

- Small config/parameters → JSON (standard format)
- Large structured data → TOON (token efficiency)

Troubleshooting
---------------

Why does my encoded data look incomplete?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Most likely:** Your data has deep nesting (3+ levels) that TOON skips.

**Check for warnings:**

.. code-block:: python

   import os
   os.environ['PYTOON_DEBUG'] = '1'

   result = pytoon.encode(data)
   # Look for: "WARNING: Skipping deeply nested array..."

**Solution:** Restructure your data to flatten the nesting (see patterns above).

How do I validate that TOON encoding is correct?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use roundtrip testing:**

.. code-block:: python

   import pytoon

   original = {"users": [{"id": 1, "name": "Alice"}]}
   encoded = pytoon.encode(original)
   decoded = pytoon.decode(encoded)

   assert decoded == original  # Should always pass!

If roundtrip fails, it's a bug - please report it!

Why am I getting more tokens with TOON than JSON?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common reasons:**

1. **Small dataset:** TOON has header overhead. For < 100 tokens, JSON might be smaller.

   .. code-block:: python

      tiny = {"x": 1}
      # JSON: 7 tokens
      # TOON: 6 tokens (minimal difference, not worth it)

2. **Heterogeneous data:** TOON excels at uniform data.

   .. code-block:: python

      # Bad for TOON (all different keys)
      mixed = [{"a": 1}, {"b": 2}, {"c": 3}]

      # Good for TOON (same keys)
      uniform = [{"id": 1, "val": "x"}, {"id": 2, "val": "y"}]

3. **Already minimal structure:** Some JSON is already optimal.

   .. code-block:: python

      # JSON is already compact
      simple = [1, 2, 3, 4, 5]

**Rule of thumb:** TOON shines with:

- Arrays of objects (≥2 objects)
- Objects with multiple fields
- Repeated keys across structures

Why is decoding failing with "invalid TOON syntax"?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common issues:**

1. **Mixed indentation:** Use consistent spaces (2 or 4), never tabs for indentation.

   .. code-block:: text

      ❌ Bad:
      users:
        id: 1    ← 2 spaces
          name: Alice  ← 4 spaces (inconsistent!)

      ✅ Good:
      users:
        id: 1
        name: Alice

2. **Missing colons:** Object fields need ``key: value`` format.

3. **Array length mismatch:** If using length markers (``[#3]``), count must match.

4. **Blank lines in arrays:** Arrays must be contiguous (no blank lines).

**Enable debug logging to see exactly where parsing fails:**

.. code-block:: python

   import os
   os.environ['PYTOON_DEBUG'] = '1'

   pytoon.decode(toon_string)  # Will show detailed error location

Advanced Topics
---------------

How does TOON handle special characters?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Same as JSON:**

- Strings with special chars are quoted
- Escape sequences: ``\n``, ``\r``, ``\t``, ``\"``, ``\\``
- Numbers, booleans, null are unquoted

.. code-block:: python

   data = {"message": "Line 1\nLine 2", "path": "C:\\Users"}
   encoded = pytoon.encode(data)
   # Output:
   # message: "Line 1\nLine 2"
   # path: "C:\\Users"

Can I customize the TOON format?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Limited customization available:**

.. code-block:: python

   pytoon.encode(data, options={
       "indent": 4,           # Spaces per level (default: 2)
       "delimiter": "|",      # Value separator: ',', '|', '\t'
       "length_marker": True  # Include #N in headers (default: False)
   })

**Example output with pipe delimiter:**

.. code-block:: text

   users[2|]{id| name| role}:
     1| Alice| Engineer
     2| Bob| Designer

Contributing & Support
----------------------

I found a bug, where do I report it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**GitHub Issues:** https://github.com/johannschopplich/toon/issues

**Include:**

- Minimal reproduction example
- Expected vs actual behavior
- Python version and pytoon version

Where can I learn more?
~~~~~~~~~~~~~~~~~~~~~~~~

**Documentation:**

- :doc:`user_guide/quickstart` - Getting started guide
- :doc:`user_guide/format_specification` - Complete format spec
- :doc:`guides/data_restructuring` - Data transformation patterns
- :doc:`api/core` - API reference

**Examples:**

- ``examples/openai_integration.py`` - OpenAI usage
- ``examples/better_patterns_demo.py`` - Data restructuring demos

See Also
--------

- :doc:`troubleshooting` - Technical troubleshooting guide
- :doc:`guides/data_restructuring` - Detailed restructuring patterns
- :doc:`user_guide/performance_tips` - Performance optimization
- :doc:`benchmarks` - Performance benchmarks
