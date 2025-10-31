Error Handling
==============

This guide covers error handling patterns and best practices for robust TOON applications.

Common Error Scenarios
----------------------

Encoding Errors
~~~~~~~~~~~~~~~

**Non-serializable types:**

.. code-block:: python

    # Error: functions can't be encoded
    data = {"func": lambda x: x}
    ptoon.encode(data)  # TypeError or normalizes to null

**Solution:** Remove or convert unsupported types

.. code-block:: python

    # Convert to serializable form
    data = {"func_name": "lambda_function"}

Decoding Errors
~~~~~~~~~~~~~~~

**Invalid TOON syntax:**

.. code-block:: python

    invalid_toon = "key value"  # Missing colon
    ptoon.decode(invalid_toon)  # ValueError

**Invalid indentation:**

.. code-block:: python

    invalid_toon = """
    user:
       name: Alice
      age: 30
    """
    ptoon.decode(invalid_toon)  # ValueError: Invalid indentation

**Solution:** Ensure TOON is well-formed or implement fallback

LLM Response Errors
~~~~~~~~~~~~~~~~~~~

**LLM returns invalid TOON:**

.. code-block:: python

    response = llm.generate("List users in TOON format")
    # Response might be malformed
    ptoon.decode(response)  # ValueError

**Solution:** Implement fallback parsing

Error Handling Patterns
-----------------------

1. Try-Except with Fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import ptoon
    import json

    def safe_decode(text):
        """Try TOON, then JSON, then return as text."""
        # Try TOON first
        try:
            return ptoon.decode(text)
        except ValueError:
            pass
        
        # Try JSON
        try:
            return json.loads(text)
        except ValueError:
            pass
        
        # Return as plain text
        return text

    # Usage
    result = safe_decode(llm_response)

2. Graceful Degradation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def encode_safe(data):
        """Encode to TOON, fallback to JSON on error."""
        try:
            return "toon", ptoon.encode(data)
        except (TypeError, ValueError) as e:
            print(f"Warning: TOON encoding failed ({e}), using JSON")
            return "json", json.dumps(data, indent=2)

    # Usage
    format_type, encoded = encode_safe(data)
    prompt = f"Data ({format_type}):\n{encoded}\n\nQuestion: ..."

3. Retry with Clarification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def query_with_retry(data, question, max_retries=3):
        """Query LLM, retry on decode errors."""
        toon_str = ptoon.encode(data)
        prompt = f"Data:\n{toon_str}\n\n{question}"
        
        for attempt in range(max_retries):
            response = llm.generate(prompt)
            
            try:
                return ptoon.decode(response)
            except ValueError as e:
                if attempt < max_retries - 1:
                    # Add clarification for next attempt
                    prompt += "\nPlease respond in valid TOON format."
                else:
                    # Last attempt failed, return as text
                    return response

4. Validation Before Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def validate_and_encode(data):
        """Validate data before encoding."""
        # Check type
        if not isinstance(data, (dict, list)):
            raise TypeError(f"Expected dict or list, got {type(data)}")
        
        # Check for non-serializable types
        def check_serializable(obj):
            if callable(obj):
                raise TypeError(f"Cannot encode callable: {obj}")
            if isinstance(obj, dict):
                for v in obj.values():
                    check_serializable(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_serializable(v)
        
        check_serializable(data)
        
        # Encode
        return ptoon.encode(data)

Debug Mode
----------

Enable debug logging:

.. code-block:: bash

    export PTOON_DEBUG=1

.. code-block:: python

    import os
    os.environ['PTOON_DEBUG'] = '1'

    # Now encoding decisions are logged
    toon_str = ptoon.encode(data)

Understanding Error Messages
-----------------------------

ValueError: Invalid indentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ValueError: Invalid indentation at line 3

**Cause:** Inconsistent spacing or tabs

**Solution:**

.. code-block:: python

    # Bad: inconsistent
    """
    user:
       name: Alice
      age: 30
    """

    # Good: consistent 2-space indent
    """
    user:
      name: Alice
      age: 30
    """

ValueError: Array length mismatch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ValueError: Array length mismatch: expected 3, got 2

**Cause:** Declared length doesn't match actual items

**Solution:** Fix the array or use correct length marker

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

ValueError: Tabs not allowed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause:** Tabs used for indentation

**Solution:** Convert tabs to spaces

.. code-block:: python

    # Convert tabs to spaces
    toon_str = toon_str.replace('\t', '  ')
    ptoon.decode(toon_str)

Complete Example
----------------

Robust LLM integration with comprehensive error handling:

.. code-block:: python

    import ptoon
    import json
    import logging

    logger = logging.getLogger(__name__)

    def robust_llm_query(data, question, max_retries=3):
        """
        Query LLM with TOON data, comprehensive error handling.
        
        Returns: Parsed result or None on failure
        """
        # Encode data
        try:
            toon_str = ptoon.encode(data)
            format_type = "TOON"
        except (TypeError, ValueError) as e:
            logger.warning(f"TOON encoding failed: {e}, falling back to JSON")
            toon_str = json.dumps(data, indent=2)
            format_type = "JSON"
        
        # Construct prompt
        prompt = f"Data ({format_type}):\n{toon_str}\n\nQuestion: {question}"
        
        # Try with retries
        for attempt in range(max_retries):
            try:
                # Send to LLM
                response = llm.generate(prompt)
                
                # Try parsing response
                # 1. Try TOON
                try:
                    return ptoon.decode(response)
                except ValueError:
                    pass
                
                # 2. Try JSON
                try:
                    return json.loads(response)
                except ValueError:
                    pass
                
                # 3. Return as text if it's the last attempt
                if attempt == max_retries - 1:
                    return response
                
                # Add clarification for next attempt
                prompt += "\n\nPlease respond in valid TOON or JSON format."
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None

    # Usage
    result = robust_llm_query(
        data={"employees": [...]},
        question="Who has the highest salary?"
    )

    if result:
        print(f"Success: {result}")
    else:
        print("Query failed after retries")

Best Practices
--------------

1. Always Use Try-Except
~~~~~~~~~~~~~~~~~~~~~~~~~

Never assume decode will succeed:

.. code-block:: python

    # Bad
    result = ptoon.decode(response)

    # Good
    try:
        result = ptoon.decode(response)
    except ValueError as e:
        logger.error(f"Decode failed: {e}")
        result = response  # Use raw text

2. Log Errors
~~~~~~~~~~~~~

.. code-block:: python

    import logging

    try:
        data = ptoon.decode(toon_str)
    except ValueError as e:
        logging.error(f"Decode error: {e}", extra={
            "toon_string": toon_str[:100],  # First 100 chars
            "error_type": type(e).__name__
        })

3. Implement Fallbacks
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def parse_response(text):
        """Multi-level fallback parsing."""
        parsers = [
            ("TOON", ptoon.decode),
            ("JSON", json.loads),
            ("TEXT", lambda x: x)
        ]
        
        for name, parser in parsers:
            try:
                return name, parser(text)
            except Exception:
                continue
        
        return "UNKNOWN", text

4. Validate Input
~~~~~~~~~~~~~~~~~

.. code-block:: python

    def validate_data(data):
        """Validate before encoding."""
        if not isinstance(data, (dict, list)):
            raise TypeError("Data must be dict or list")
        
        # Add more validation as needed
        return True

    if validate_data(data):
        toon_str = ptoon.encode(data)

5. Test Error Paths
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Unit test for error handling
    def test_decode_error_handling():
        invalid_toon = "invalid: {syntax"
        
        try:
            ptoon.decode(invalid_toon)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

See Also
--------

* :doc:`/troubleshooting` - Troubleshooting guide
* :doc:`/user_guide/core_api` - Core API error documentation
* :doc:`/integrations/overview` - Integration patterns
