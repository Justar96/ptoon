Quickstart Guide
================

This guide will get you started with pytoon in minutes.

Basic Encoding
--------------

Simple Dictionary
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon

    data = {
        "name": "Alice",
        "age": 30,
        "city": "San Francisco"
    }

    toon_str = pytoon.encode(data)
    print(toon_str)

Output:

.. code-block:: text

    name: Alice
    age: 30
    city: San Francisco

Simple List
~~~~~~~~~~~

.. code-block:: python

    data = {"numbers": [1, 2, 3, 4, 5]}
    toon_str = pytoon.encode(data)
    print(toon_str)

Output:

.. code-block:: text

    numbers[5]: 1, 2, 3, 4, 5

Nested Structure
~~~~~~~~~~~~~~~~

.. code-block:: python

    data = {
        "user": {
            "name": "Alice",
            "contact": {
                "email": "alice@example.com",
                "phone": "555-1234"
            }
        }
    }

    toon_str = pytoon.encode(data)
    print(toon_str)

Output:

.. code-block:: text

    user:
      name: Alice
      contact:
        email: alice@example.com
        phone: 555-1234

Basic Decoding
--------------

Decode TOON string back to Python:

.. code-block:: python

    toon_str = """
    name: Alice
    age: 30
    city: San Francisco
    """

    data = pytoon.decode(toon_str)
    print(data)
    # Output: {'name': 'Alice', 'age': 30, 'city': 'San Francisco'}

Roundtrip Example
~~~~~~~~~~~~~~~~~

Verify data integrity:

.. code-block:: python

    import pytoon

    original = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }

    # Encode
    toon_str = pytoon.encode(original)
    
    # Decode
    decoded = pytoon.decode(toon_str)
    
    # Verify
    assert decoded == original
    print("Roundtrip successful!")

Common Use Cases
----------------

1. Sending Data to LLMs
~~~~~~~~~~~~~~~~~~~~~~~~

Reduce token usage when sending data to language models:

.. code-block:: python

    import pytoon
    import openai

    # Your data
    employees = [
        {"id": 1, "name": "Alice", "role": "Engineer", "salary": 120000},
        {"id": 2, "name": "Bob", "role": "Designer", "salary": 100000},
        {"id": 3, "name": "Carol", "role": "Manager", "salary": 150000},
    ]

    # Encode to TOON
    toon_str = pytoon.encode({"employees": employees})

    # Use in LLM prompt
    prompt = f"""
    Given this employee data:
    {toon_str}

    Who has the highest salary?
    """

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(response.choices[0].message.content)

The TOON format saves tokens compared to JSON:

.. code-block:: text

    employees[3]{id, name, role, salary}:
      1, Alice, Engineer, 120000
      2, Bob, Designer, 100000
      3, Carol, Manager, 150000

vs JSON:

.. code-block:: json

    {
      "employees": [
        {"id": 1, "name": "Alice", "role": "Engineer", "salary": 120000},
        {"id": 2, "name": "Bob", "role": "Designer", "salary": 100000},
        {"id": 3, "name": "Carol", "role": "Manager", "salary": 150000}
      ]
    }

2. Token Counting
~~~~~~~~~~~~~~~~~

Count tokens in your data:

.. code-block:: python

    import pytoon

    data = {"employees": [...]}  # Your data

    # Count JSON tokens
    import json
    json_str = json.dumps(data)
    json_tokens = pytoon.count_tokens(json_str)

    # Count TOON tokens
    toon_str = pytoon.encode(data)
    toon_tokens = pytoon.count_tokens(toon_str)

    print(f"JSON: {json_tokens} tokens")
    print(f"TOON: {toon_tokens} tokens")
    print(f"Savings: {json_tokens - toon_tokens} tokens ({(1 - toon_tokens/json_tokens)*100:.1f}%)")

3. Format Comparison
~~~~~~~~~~~~~~~~~~~~

Easily compare JSON vs TOON:

.. code-block:: python

    import pytoon

    data = {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
        ]
    }

    # Visual comparison
    print(pytoon.compare_formats(data))

Output:

.. code-block:: text

    Format Comparison
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Format  Tokens  Size (bytes)  Savings
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    JSON    45      147           -
    TOON    28      98            37.8% tokens, 33.3% size
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can also use ``estimate_savings()`` for programmatic access:

.. code-block:: python

    result = pytoon.estimate_savings(data)
    print(f"JSON tokens: {result['json_tokens']}")
    print(f"TOON tokens: {result['toon_tokens']}")
    print(f"Savings: {result['savings_percent']:.1f}%")

Encoding Options
----------------

Brief Introduction
~~~~~~~~~~~~~~~~~~

TOON supports several encoding options to customize output:

.. code-block:: python

    options = {
        "delimiter": ",",      # or "|" or "\t"
        "indent": 2,           # spaces per level
        "length_marker": False # include #N in headers
    }

    toon_str = pytoon.encode(data, options=options)

Delimiter Options
~~~~~~~~~~~~~~~~~

Choose delimiter based on your data:

.. code-block:: python

    data = {"values": [1, 2, 3]}

    # Comma (default)
    pytoon.encode(data, options={"delimiter": ","})
    # values[3]: 1, 2, 3

    # Pipe
    pytoon.encode(data, options={"delimiter": "|"})
    # values[3|]: 1| 2| 3

    # Tab
    pytoon.encode(data, options={"delimiter": "\t"})
    # values[3\t]: 1	2	3

For detailed encoding options, see :doc:`/guides/encoding_options`.

Next Steps
----------

Now that you understand the basics:

* :doc:`core_api` - Learn all available functions
* :doc:`/integrations/openai` - Integrate with OpenAI
* :doc:`/guides/token_optimization` - Maximize token savings
* :doc:`format_specification` - Understand TOON format in depth
