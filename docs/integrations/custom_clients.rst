Custom Clients and Local Models
================================

This guide shows how to use TOON with custom LLM clients and local models.

Introduction
------------

TOON works with **any LLM that accepts text input**. No special API support is required. This includes:

* Local models (Ollama, llama.cpp)
* Custom API endpoints
* Self-hosted models
* Hugging Face Transformers

General Pattern
---------------

The pattern is the same for all providers:

1. Encode data: ``toon_str = pytoon.encode(data)``
2. Construct prompt: ``prompt = f"Data:\n{toon_str}\n\nQuestion: ..."``
3. Send to model using provider's API
4. Parse response

Local Models
------------

Ollama
~~~~~~

`Ollama <https://ollama.ai/>`_ provides easy local model hosting.

.. code-block:: python

    import pytoon
    import requests

    # Encode data
    data = {"products": [...]}
    toon_str = pytoon.encode(data)

    # Send to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": f"Given this data:\n{toon_str}\n\nWhat is the most expensive product?",
            "stream": False
        }
    )

    answer = response.json()["response"]
    print(answer)

llama.cpp
~~~~~~~~~

Use with Python bindings:

.. code-block:: python

    import pytoon
    from llama_cpp import Llama

    # Load model
    llm = Llama(model_path="./models/llama-2-7b.gguf")

    # Encode data
    data = {...}
    toon_str = pytoon.encode(data)

    # Generate
    prompt = f"Data:\n{toon_str}\n\nQuestion: ..."
    output = llm(prompt, max_tokens=100)
    answer = output["choices"][0]["text"]
    print(answer)

Hugging Face Transformers
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytoon
    from transformers import AutoTokenizer, AutoModelForCausalLM

    # Load model
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Encode data
    data = {...}
    toon_str = pytoon.encode(data)

    # Generate
    prompt = f"Data:\n{toon_str}\n\nQuestion: ..."
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(answer)

Custom API Endpoints
--------------------

REST API
~~~~~~~~

.. code-block:: python

    import pytoon
    import requests

    # Encode data
    data = {...}
    toon_str = pytoon.encode(data)

    # Send to custom API
    response = requests.post(
        "https://your-llm-api.com/generate",
        json={
            "prompt": f"Data:\n{toon_str}\n\nQuestion: ...",
            "max_tokens": 100,
            "temperature": 0.7
        },
        headers={"Authorization": "Bearer your-token"}
    )

    answer = response.json()["text"]

gRPC API
~~~~~~~~

.. code-block:: python

    import pytoon
    import grpc
    # Assuming you have generated pb2 files from proto definitions
    import your_llm_service_pb2 as pb2
    import your_llm_service_pb2_grpc as pb2_grpc

    # Encode data
    data = {...}
    toon_str = pytoon.encode(data)

    # Send to gRPC service
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.LLMServiceStub(channel)

    request = pb2.GenerateRequest(
        prompt=f"Data:\n{toon_str}\n\nQuestion: ...",
        max_tokens=100
    )

    response = stub.Generate(request)
    answer = response.text

Token Counting
--------------

For Model-Specific Tokenizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the model's own tokenizer for accurate counts:

.. code-block:: python

    # Hugging Face
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("model-name")
    tokens = tokenizer(toon_str)["input_ids"]
    token_count = len(tokens)

    # llama.cpp
    from llama_cpp import Llama
    llm = Llama(model_path="model.gguf")
    token_count = len(llm.tokenize(toon_str.encode()))

For Approximations
~~~~~~~~~~~~~~~~~~

Use pytoon's built-in counting (OpenAI-compatible):

.. code-block:: python

    # Approximate count
    token_count = pytoon.count_tokens(toon_str)

Prompt Engineering
------------------

Some models may need format explanation:

.. code-block:: python

    system_prompt = """
    You will receive data in TOON format, a compact notation similar to JSON.
    Format rules:
    - key: value for simple fields
    - key[N]{fields}: for tabular data
    - - item for lists
    """

    prompt = f"{system_prompt}\n\nData:\n{toon_str}\n\nQuestion: ..."

Most modern models understand TOON without explanation.

Testing Token Efficiency
------------------------

Measure with model's tokenizer:

.. code-block:: python

    import pytoon
    import json

    data = {...}

    # Compare formats
    json_str = json.dumps(data)
    toon_str = pytoon.encode(data)

    # Count with model's tokenizer
    json_tokens = len(tokenizer(json_str)["input_ids"])
    toon_tokens = len(tokenizer(toon_str)["input_ids"])

    savings = json_tokens - toon_tokens
    print(f"Savings: {savings} tokens ({savings/json_tokens*100:.1f}%)")

Best Practices
--------------

1. Test with Small Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Verify model understands TOON
    test_data = {"items": [{"a": 1}, {"a": 2}]}
    toon_str = pytoon.encode(test_data)
    
    # Send to model and check response
    response = model.generate(f"Parse this:\n{toon_str}")

2. Implement Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def encode_safe(data):
        try:
            return pytoon.encode(data)
        except Exception:
            return json.dumps(data)

3. Monitor Performance
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import time

    # Measure encoding overhead
    start = time.time()
    toon_str = pytoon.encode(data)
    encoding_time = time.time() - start

    # Measure inference time
    start = time.time()
    response = model.generate(prompt)
    inference_time = time.time() - start

    print(f"Encoding: {encoding_time*1000:.2f}ms")
    print(f"Inference: {inference_time*1000:.2f}ms")

Example: Complete Local Setup
------------------------------

Full script for local model:

.. code-block:: python

    #!/usr/bin/env python3
    """Complete local model + TOON example."""

    import pytoon
    import json
    from transformers import AutoTokenizer, AutoModelForCausalLM

    def main():
        # Load model
        model_name = "microsoft/phi-2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # Sample data
        data = {
            "products": [
                {"id": 1, "name": "Widget", "price": 19.99},
                {"id": 2, "name": "Gadget", "price": 29.99}
            ]
        }

        # Compare formats
        json_str = json.dumps(data)
        toon_str = pytoon.encode(data)

        json_tokens = len(tokenizer(json_str)["input_ids"])
        toon_tokens = len(tokenizer(toon_str)["input_ids"])

        print(f"JSON: {json_tokens} tokens")
        print(f"TOON: {toon_tokens} tokens")
        print(f"Savings: {json_tokens - toon_tokens} tokens\n")

        # Query with TOON
        prompt = f"Given:\n{toon_str}\n\nWhat is the most expensive product?"
        
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=200)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"Answer: {answer}")

    if __name__ == "__main__":
        main()

Troubleshooting
---------------

**Model doesn't understand TOON**

* Add format explanation to system prompt
* Provide an example in the prompt
* Test with simpler structures first

**Token counting is inaccurate**

* Use model's own tokenizer
* ``pytoon.count_tokens()`` is OpenAI-specific

**Performance issues**

* Profile encoding vs inference time
* Consider caching encoded data
* For tiny payloads, JSON might be faster

See Also
--------

* :doc:`overview` - General integration patterns
* :doc:`/guides/error_handling` - Error handling
* :doc:`/guides/performance_tips` - Performance optimization
