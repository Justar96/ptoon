Streaming Responses
===================

This guide explains how to use TOON with streaming LLM APIs.

Introduction
------------

Streaming allows displaying LLM responses in real-time. TOON works seamlessly with streaming:

* Encode data upfront (one-time operation)
* Stream the response as usual
* Parse complete response after streaming finishes

Basic Pattern
-------------

1. **Encode data before streaming**
2. **Stream response chunks**
3. **Parse complete response**

OpenAI Streaming Example
------------------------

.. code-block:: python

    import pytoon
    import openai

    # 1. Encode data upfront
    data = {"employees": [...]}
    toon_str = pytoon.encode(data)

    # 2. Create prompt
    prompt = f"Given this data:\n{toon_str}\n\nWho has the highest salary?"

    # 3. Stream response
    client = openai.OpenAI()
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    # 4. Collect and display chunks
    chunks = []
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            chunks.append(content)

    print()  # Newline after stream

    # 5. Parse complete response
    full_response = "".join(chunks)
    try:
        result = pytoon.decode(full_response)
        print(f"\nParsed result: {result}")
    except ValueError:
        print(f"\nText result: {full_response}")

Anthropic Streaming Example
---------------------------

.. code-block:: python

    import pytoon
    import anthropic

    # Encode data
    data = {...}
    toon_str = pytoon.encode(data)

    # Stream with Claude
    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-3-opus-20240229",
        messages=[{
            "role": "user",
            "content": f"Data:\n{toon_str}\n\nQuestion: ..."
        }],
        max_tokens=1024
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        
        # Get complete response
        full_response = stream.get_final_text()

    # Parse if needed
    try:
        result = pytoon.decode(full_response)
    except ValueError:
        result = full_response

Handling Partial Responses
---------------------------

Incomplete TOON
~~~~~~~~~~~~~~~

Don't try to parse incomplete TOON:

.. code-block:: python

    # Bad: parsing during stream
    for chunk in stream:
        try:
            pytoon.decode(accumulated_text)  # Will fail on partial TOON
        except ValueError:
            pass

    # Good: parse after stream completes
    full_response = "".join(chunks)
    result = pytoon.decode(full_response)

Buffering Strategy
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def stream_and_parse(prompt):
        """Stream response, parse after completion."""
        buffer = []
        
        # Stream and display
        for chunk in llm.stream(prompt):
            text = chunk.content
            print(text, end="", flush=True)
            buffer.append(text)
        
        print()  # Newline
        
        # Parse complete response
        complete = "".join(buffer)
        try:
            return pytoon.decode(complete)
        except ValueError:
            return complete

Error Handling
--------------

Handle Stream Interruptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def stream_with_retry(prompt, max_retries=3):
        """Stream with retry on interruption."""
        for attempt in range(max_retries):
            try:
                chunks = []
                for chunk in llm.stream(prompt):
                    chunks.append(chunk.content)
                    print(chunk.content, end="", flush=True)
                
                # Success
                return "".join(chunks)
            
            except Exception as e:
                print(f"\nStream interrupted: {e}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                else:
                    raise
        
        return None

Handle Invalid Response
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def safe_stream_parse(prompt):
        """Stream and safely parse response."""
        chunks = []
        
        try:
            for chunk in llm.stream(prompt):
                text = chunk.content
                print(text, end="", flush=True)
                chunks.append(text)
        except Exception as e:
            print(f"\nStreaming error: {e}")
            return None
        
        print()
        complete = "".join(chunks)
        
        # Try multiple parsers
        for parser in [pytoon.decode, json.loads, lambda x: x]:
            try:
                return parser(complete)
            except Exception:
                continue
        
        return complete

Best Practices
--------------

1. Encode Before Streaming
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Good: encode once upfront
    toon_str = pytoon.encode(data)
    for query in queries:
        prompt = f"Data:\n{toon_str}\n\n{query}"
        stream_response(prompt)

    # Bad: encoding during stream (unnecessary overhead)
    for query in queries:
        toon_str = pytoon.encode(data)  # Redundant
        stream_response(f"Data:\n{toon_str}\n\n{query}")

2. Buffer Responses
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Collect all chunks
    chunks = []
    for chunk in stream:
        text = chunk.content
        print(text, end="", flush=True)
        chunks.append(text)

    # Parse complete response
    complete = "".join(chunks)

3. Display Raw Text
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Show streaming text to user
    for chunk in stream:
        display_to_user(chunk.content)

    # Parse in background
    result = parse_complete_response(complete_text)

4. Handle Timeouts
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import signal

    def stream_with_timeout(prompt, timeout=30):
        """Stream with timeout."""
        def timeout_handler(signum, frame):
            raise TimeoutError("Stream timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            return stream_response(prompt)
        finally:
            signal.alarm(0)  # Cancel alarm

Performance Considerations
--------------------------

* Streaming doesn't affect TOON encoding (done upfront)
* Token savings still apply
* No additional latency during stream
* Encoding overhead is one-time

Complete Example
----------------

Full streaming application:

.. code-block:: python

    #!/usr/bin/env python3
    """Complete streaming + TOON example."""

    import pytoon
    import openai
    import sys

    def stream_query(data, question):
        """Stream LLM response with TOON data."""
        client = openai.OpenAI()
        
        # Encode data upfront
        try:
            toon_str = pytoon.encode(data)
        except Exception as e:
            print(f"Encoding error: {e}", file=sys.stderr)
            return None
        
        # Construct prompt
        prompt = f"Data:\n{toon_str}\n\nQuestion: {question}"
        
        # Stream response
        print("Response: ", end="", flush=True)
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            chunks = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    chunks.append(content)
            
            print("\n")  # Newline after stream
            
            # Parse complete response
            full_response = "".join(chunks)
            try:
                return pytoon.decode(full_response)
            except ValueError:
                return full_response
        
        except Exception as e:
            print(f"\nStreaming error: {e}", file=sys.stderr)
            return None

    def main():
        # Sample data
        data = {
            "products": [
                {"id": 1, "name": "Widget", "price": 19.99},
                {"id": 2, "name": "Gadget", "price": 29.99},
                {"id": 3, "name": "Doohickey", "price": 39.99}
            ]
        }

        # Query with streaming
        result = stream_query(data, "What is the most expensive product?")
        
        if result:
            print(f"Parsed result: {result}")
        else:
            print("Query failed")

    if __name__ == "__main__":
        main()

See Also
--------

* :doc:`/integrations/openai` - OpenAI integration
* :doc:`/guides/error_handling` - Error handling patterns
* :doc:`/integrations/overview` - General integration guide
