Benchmarks
==========

This page summarizes ptoon's performance characteristics based on comprehensive benchmarks.

Token Efficiency Results
------------------------

Overall token savings: **47.5%** (TOON 22,451 vs JSON 42,759 tokens)

By Dataset
~~~~~~~~~~

1. **GitHub Repositories (100 records)**
   
   * JSON: 15,144 tokens
   * TOON: 8,744 tokens
   * **Savings: 42.3%**
   * Structure: Uniform tabular data with 11 fields

2. **Daily Analytics (180 days)**
   
   * JSON: 10,969 tokens
   * TOON: 4,499 tokens
   * **Savings: 59.0%**
   * Structure: Time-series metrics

3. **E-Commerce Orders (50 orders)**
   
   * JSON: 10,654 tokens
   * TOON: 7,046 tokens
   * **Savings: 33.9%**
   * Structure: Nested customer and item data

4. **Employee Records (100 employees)**
   
   * JSON: 5,992 tokens
   * TOON: 2,162 tokens
   * **Savings: 63.9%**
   * Structure: Uniform employee records (highest savings)

Key Findings
~~~~~~~~~~~~

* **Best case:** Uniform tabular data (60-64% savings)
* **Good case:** Repeated structures (40-59% savings)
* **Moderate case:** Nested heterogeneous data (30-40% savings)

Latest Reports
~~~~~~~~~~~~~~

* :download:`Token Efficiency Results <../benchmarks/results/token-efficiency.md>` — dataset-level token counts and savings tables.
* :download:`Speed Benchmark <../benchmarks/results/speed-benchmark.md>` — per-dataset encoding/decoding timings.
* :download:`Memory Benchmark <../benchmarks/results/memory-benchmark.md>` — peak memory usage comparisons.
* :download:`LLM Accuracy Report <../benchmarks/results/llm_accuracy/report.md>` — accuracy deltas between TOON and JSON along with qualitative evaluation notes.

Example: Employee Records
~~~~~~~~~~~~~~~~~~~~~~~~~

**TOON format:**

.. code-block:: text

    employees[100]{id, name, role, department, salary, hire_date}:
      1, Employee 1, Engineer, Engineering, 101000, 2020-01-01
      2, Employee 2, Designer, Design, 102000, 2020-01-02
      3, Employee 3, Manager, Management, 103000, 2020-01-03
      ...

**JSON format:**

.. code-block:: json

    {
      "employees": [
        {
          "id": 1,
          "name": "Employee 1",
          "role": "Engineer",
          "department": "Engineering",
          "salary": 101000,
          "hire_date": "2020-01-01"
        },
        {
          "id": 2,
          "name": "Employee 2",
          "role": "Designer",
          "department": "Design",
          "salary": 102000,
          "hire_date": "2020-01-02"
        },
        ...
      ]
    }

Notice how field names appear once in TOON vs repeated 100 times in JSON.

Speed Benchmark Results
-----------------------

Encoding Speed
~~~~~~~~~~~~~~

* TOON encoding: **~0.12x speed of JSON** (slower)
* Range: 0.08x to 0.17x depending on data structure
* Reason: Python implementation vs C-optimized json module

Decoding Speed
~~~~~~~~~~~~~~

* TOON decoding: **~0.10x speed of JSON** (slower)
* Range: 0.05x to 0.16x
* Reason: Complex parsing logic vs optimized JSON parser

Why Speed Doesn't Matter
~~~~~~~~~~~~~~~~~~~~~~~~~

**Encoding overhead vs inference time:**

* Encoding overhead: 1-10ms
* LLM inference: 100-1000ms+
* **Token savings reduce inference time**
* Net result: TOON is faster end-to-end

**Example:**

* JSON: 6,000 tokens → 600ms inference
* TOON: 2,200 tokens → 220ms inference
* Encoding overhead: +5ms
* **Net savings: 375ms**

Memory Benchmark Results
------------------------

* Memory usage comparable to JSON
* No significant overhead
* Output size: TOON typically 30-60% smaller than JSON

Running Benchmarks
------------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install ptoon[benchmark]

Run All Benchmarks
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    toon-benchmark
    # or
    python -m benchmarks

Run Specific Benchmarks
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Token efficiency only
    toon-benchmark --token-efficiency

    # Speed benchmark
    toon-benchmark --speed

    # Memory benchmark
    toon-benchmark --memory

    # All with JSON output
    toon-benchmark --all --json

Benchmark Your Data
-------------------

Quick Comparison
~~~~~~~~~~~~~~~~

.. code-block:: python

    import ptoon

    data = {...}  # Your data
    
    # Visual comparison
    print(ptoon.compare_formats(data))

    # Output:
    # Format Comparison
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Format  Tokens  Size (bytes)  Savings
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # JSON    5992    19234         -
    # TOON    2162    6891          63.9% tokens
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Programmatic Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    result = ptoon.estimate_savings(data)
    
    print(f"JSON tokens: {result['json_tokens']}")
    print(f"TOON tokens: {result['toon_tokens']}")
    print(f"Savings: {result['savings']} tokens ({result['savings_percent']:.1f}%)")
    
    if result['savings_percent'] > 30:
        print("✓ TOON recommended")
    else:
        print("✗ Consider JSON")

Interpreting Results
--------------------

Token Savings
~~~~~~~~~~~~~

* **>50%**: Excellent - uniform tabular data
* **30-50%**: Good - structured data with repetition
* **<30%**: Moderate - consider JSON for simple cases
* **<10%**: Poor - use JSON instead

When to Use TOON
~~~~~~~~~~~~~~~~

✓ **Use TOON when:**

* Token savings >30%
* Large datasets (>100 tokens)
* Uniform structured data
* Cost optimization matters

✗ **Use JSON when:**

* Token savings <30%
* Tiny payloads (<100 tokens)
* Function calling / tool use
* Highly heterogeneous data

Benchmark Methodology
---------------------

Datasets
~~~~~~~~

* Generated with Faker library (seeded for reproducibility)
* Represent common LLM use cases
* Range from simple to complex structures

Token Counting
~~~~~~~~~~~~~~

* Uses tiktoken with ``o200k_base`` encoding (GPT-4o)
* Accurate for OpenAI models
* Approximation for other providers

Speed Measurement
~~~~~~~~~~~~~~~~~

* Multiple iterations for accuracy
* Median values reported
* Excludes outliers

Reproducibility
~~~~~~~~~~~~~~~

* Seeded random generation
* Consistent test data
* Results should be reproducible:

.. code-block:: bash

    git clone https://github.com/Justar96/toon-py.git
    cd ptoon
    pip install -e ".[benchmark]"
    toon-benchmark

Results Location
----------------

Detailed benchmark results are in the repository:

* `benchmarks/results/token-efficiency.md <https://github.com/Justar96/pytoon/blob/main/benchmarks/results/token-efficiency.md>`_
* `benchmarks/results/speed-benchmark.md <https://github.com/Justar96/pytoon/blob/main/benchmarks/results/speed-benchmark.md>`_
* `benchmarks/results/memory-benchmark.md <https://github.com/Justar96/pytoon/blob/main/benchmarks/results/memory-benchmark.md>`_

See Also
--------

* :doc:`user_guide/performance_tips` - Performance optimization
* :doc:`guides/token_optimization` - Token optimization strategies
* `Benchmark Results <https://github.com/Justar96/toon-py/tree/master/benchmarks/results>`_
