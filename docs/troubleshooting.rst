Troubleshooting
===============

This guide helps you resolve common issues when using pytoon.

Installation Issues
-------------------

pip install fails
~~~~~~~~~~~~~~~~~

**Problem:** ``pip install pytoon`` fails

**Solutions:**

1. Check Python version (≥3.10 required):

.. code-block:: bash

    python --version

2. Update pip:

.. code-block:: bash

    pip install --upgrade pip

3. Try with ``--no-cache-dir``:

.. code-block:: bash

    pip install --no-cache-dir pytoon

Import error
~~~~~~~~~~~~

**Problem:** ``ImportError: No module named 'pytoon'``

**Solutions:**

1. Verify installation:

.. code-block:: bash

    pip show pytoon

2. Check you're in the correct virtual environment

3. Reinstall:

.. code-block:: bash

    pip uninstall pytoon
    pip install pytoon

Encoding Issues
---------------

TypeError: Cannot encode
~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``TypeError: Object of type X is not JSON serializable``

**Cause:** Non-serializable type (function, class instance, etc.)

**Solution:** Remove or convert unsupported types:

.. code-block:: python

    # Bad
    data = {"func": lambda x: x}

    # Good
    data = {"func_name": "lambda"}

Large integers become strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Large integers are encoded as strings

**Cause:** Intentional behavior for JavaScript compatibility (integers >2^53-1)

**Solution:** This is expected. If you need native integers, keep values ≤2^53-1.

Datetime encoding
~~~~~~~~~~~~~~~~~

**Problem:** Datetime objects encoded as strings

**Cause:** Intentional normalization to ISO 8601 format

**Solution:** This is expected behavior. Decode will return strings, not datetime objects.

Decoding Issues
---------------

Invalid indentation
~~~~~~~~~~~~~~~~~~~

**Problem:** ``ValueError: Invalid indentation at line N``

**Cause:** Inconsistent spacing or tabs

**Solution:**

.. code-block:: python

    # Bad: inconsistent
    """
    user:
       name: Alice    # 3 spaces
      age: 30         # 2 spaces
    """

    # Good: consistent
    """
    user:
      name: Alice     # 2 spaces
      age: 30         # 2 spaces
    """

Tabs not allowed
~~~~~~~~~~~~~~~~

**Problem:** ``ValueError: Tabs not allowed for indentation``

**Cause:** Tab characters used for indentation

**Solution:** Replace tabs with spaces:

.. code-block:: python

    toon_str = toon_str.replace('\t', '  ')
    data = pytoon.decode(toon_str)

Array length mismatch
~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``ValueError: Array length mismatch: expected N, got M``

**Cause:** Declared length doesn't match actual items

**Solution:** Fix the array header or item count:

.. code-block:: python

    # Bad
    """
    items[3]:
      - a
      - b
    """

    # Good
    """
    items[2]:
      - a
      - b
    """

Invalid escape sequence
~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``ValueError: Invalid escape sequence``

**Cause:** Unknown escape like ``\x``

**Solution:** Use only valid escapes (``\n``, ``\r``, ``\t``, ``\"``, ``\\``):

.. code-block:: python

    # Bad
    """
    path: "C:\new\folder"
    """

    # Good
    """
    path: "C:\\new\\folder"
    """

LLM Integration Issues
----------------------

LLM doesn't understand TOON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** LLM gives poor results with TOON data

**Solutions:**

1. Add format explanation to prompt:

.. code-block:: python

    prompt = """
    The data is in TOON format (Token-Oriented Object Notation).
    
    {toon_str}
    
    Question: ...
    """

2. Provide an example in the prompt

3. Usually not needed - format is intuitive

Token savings lower than expected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Token savings are minimal

**Causes and solutions:**

1. **Heterogeneous data:** Restructure to uniform objects

.. code-block:: python

    # Bad: different structures
    [{"a": 1}, {"b": 2}, {"c": 3}]

    # Good: uniform structure
    [{"id": "a", "val": 1}, {"id": "b", "val": 2}]

2. **Small dataset:** TOON overhead not worth it for tiny data

3. **Already compact:** Some data doesn't benefit

**Verify:**

.. code-block:: python

    result = pytoon.estimate_savings(data)
    print(f"Savings: {result['savings_percent']:.1f}%")

Decoding LLM response fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** LLM response can't be decoded

**Solution:** Implement fallback parsing:

.. code-block:: python

    def safe_parse(response):
        # Try TOON
        try:
            return pytoon.decode(response)
        except ValueError:
            pass
        
        # Try JSON
        try:
            return json.loads(response)
        except ValueError:
            pass
        
        # Return as text
        return response

Performance Issues
------------------

Encoding is slow
~~~~~~~~~~~~~~~~

**Problem:** Encoding takes too long

**Analysis:**

.. code-block:: python

    import time
    
    start = time.time()
    toon_str = pytoon.encode(large_data)
    encoding_time = time.time() - start
    
    print(f"Encoding: {encoding_time*1000:.2f}ms")

**Note:** TOON encoding is ~0.12x speed of JSON. This is expected for Python implementation.

**Solutions:**

1. **Pre-encode static data:**

.. code-block:: python

    # Encode once, reuse many times
    static_toon = pytoon.encode(static_data)

2. **Cache encoded strings:**

.. code-block:: python

    cache = {}
    def get_encoded(key, data):
        if key not in cache:
            cache[key] = pytoon.encode(data)
        return cache[key]

3. **Consider JSON for tiny payloads**

High memory usage
~~~~~~~~~~~~~~~~~

**Problem:** High memory consumption

**Solution:** Process data in chunks:

.. code-block:: python

    # Instead of one large dataset
    large_data = {"items": [...]}  # 10,000 items

    # Split into chunks
    chunk_size = 1000
    for i in range(0, len(items), chunk_size):
        chunk = {"items": items[i:i+chunk_size]}
        toon_str = pytoon.encode(chunk)
        # Process chunk

Token counting is slow
~~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``count_tokens()`` is slow

**Cause:** tiktoken initialization overhead

**Solution:** Cache tokenizer (automatic in pytoon)

.. code-block:: python

    # Tokenizer is cached internally
    # Subsequent calls are fast
    pytoon.count_tokens(text1)  # First call (slower)
    pytoon.count_tokens(text2)  # Cached (fast)

Debug Mode Issues
-----------------

Debug logging not appearing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Debug logs not showing

**Solution:** Set environment variable:

.. code-block:: bash

    export PYTOON_DEBUG=1

Or in Python:

.. code-block:: python

    import os
    os.environ['PYTOON_DEBUG'] = '1'

Too much debug output
~~~~~~~~~~~~~~~~~~~~~

**Problem:** Too verbose

**Solution:** Disable debug mode:

.. code-block:: bash

    unset PYTOON_DEBUG

Or:

.. code-block:: bash

    export PYTOON_DEBUG=0

Type Checking Issues
--------------------

mypy errors
~~~~~~~~~~~

**Problem:** mypy reports type errors with pytoon

**Solutions:**

1. Update to latest pytoon version

2. Use type: ignore comments:

.. code-block:: python

    result = pytoon.decode(text)  # type: ignore

3. Import types explicitly:

.. code-block:: python

    from pytoon.types import JsonValue
    
    def process(data: JsonValue) -> str:
        return pytoon.encode(data)

IDE autocomplete not working
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** No autocomplete for pytoon functions

**Solutions:**

1. Ensure pytoon is installed in same environment as IDE

2. Restart IDE/language server

3. Check IDE Python interpreter settings

Diagnostic Steps
----------------

1. Verify Installation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -c "import pytoon; print(pytoon.__version__)"

2. Test Basic Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon
    
    # Test encode
    data = {"test": "value"}
    encoded = pytoon.encode(data)
    print(f"Encoded: {encoded}")
    
    # Test decode
    decoded = pytoon.decode(encoded)
    assert decoded == data
    print("✓ Basic functionality works")

3. Enable Debug Mode
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export PYTOON_DEBUG=1
    python your_script.py

4. Check Dependencies
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip list | grep -E "pytoon|tiktoken|openai"

Getting Help
------------

Before Filing an Issue
~~~~~~~~~~~~~~~~~~~~~~

1. Check this troubleshooting guide
2. Search `existing issues <https://github.com/Justar96/toon-py/issues>`_
3. Try with latest version:

.. code-block:: bash

    pip install --upgrade pytoon

4. Create minimal reproducible example

When Filing an Issue
~~~~~~~~~~~~~~~~~~~~

Include:

* Python version (``python --version``)
* pytoon version (``pip show pytoon``)
* Minimal code to reproduce
* Full error message with traceback
* Debug output if relevant (``PYTOON_DEBUG=1``)

Example:

.. code-block:: markdown

    **Python version:** 3.11.5
    **pytoon version:** 0.0.1
    
    **Code:**
    ```python
    import pytoon
    data = {...}
    pytoon.encode(data)
    ```
    
    **Error:**
    ```
    Traceback (most recent call last):
      ...
    ```

Community Resources
~~~~~~~~~~~~~~~~~~~

* `GitHub Issues <https://github.com/Justar96/toon-py/issues>`_
* `GitHub Discussions <https://github.com/Justar96/toon-py/discussions>`_
* Stack Overflow (tag: ``pytoon``)

See Also
--------

* :doc:`guides/error_handling` - Error handling patterns
* :doc:`user_guide/core_api` - Core API documentation
* `GitHub Issues <https://github.com/Justar96/toon-py/issues>`_
