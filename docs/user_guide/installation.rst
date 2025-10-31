Installation
============

Basic Installation
------------------

The core ptoon library has no dependencies and can be installed with pip:

.. code-block:: bash

    pip install ptoon

Python version requirement: **Python 3.10 or higher**

Optional Dependencies
---------------------

ptoon provides several optional dependency groups for different use cases:

Examples
~~~~~~~~

Install with OpenAI integration support:

.. code-block:: bash

    pip install ptoon[examples]

Includes:
    * ``openai`` - OpenAI Python SDK
    * ``tiktoken`` - Token counting library

Use case: Running integration examples with OpenAI

Benchmark
~~~~~~~~~

Install with benchmarking tools:

.. code-block:: bash

    pip install ptoon[benchmark]

Includes:
    * ``tiktoken`` - Token counting
    * ``faker`` - Test data generation
    * ``tqdm`` - Progress bars

Use case: Running performance benchmarks

LLM Benchmark
~~~~~~~~~~~~~

Install with LLM accuracy benchmark support:

.. code-block:: bash

    pip install ptoon[llm-benchmark]

Includes:
    * ``openai`` - OpenAI Python SDK
    * ``tiktoken`` - Token counting
    * ``tqdm`` - Progress bars
    * ``python-dotenv`` - Environment variable management

Use case: Running LLM accuracy benchmarks

Development
~~~~~~~~~~~

Install for development with testing and linting tools:

.. code-block:: bash

    pip install ptoon[dev]

Includes:
    * ``pytest`` - Testing framework
    * ``pytest-cov`` - Coverage reporting
    * ``black`` - Code formatting
    * ``ruff`` - Linting
    * ``mypy`` - Type checking

All Dependencies
~~~~~~~~~~~~~~~~

Install all optional dependencies:

.. code-block:: bash

    pip install ptoon[all]

Development Installation
------------------------

For contributors and developers:

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/Justar96/toon-py.git
    cd ptoon

2. Install in editable mode with development dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

Or using uv:

.. code-block:: bash

    uv sync --extra dev

3. Verify installation:

.. code-block:: bash

    pytest

Verification
------------

Test your installation:

.. code-block:: bash

    python -c "import ptoon; print(ptoon.__version__)"

Quick functionality test:

.. code-block:: python

    import ptoon
    
    data = {"test": "value"}
    encoded = ptoon.encode(data)
    print(encoded)
    # Output: test: value
    
    decoded = ptoon.decode(encoded)
    assert decoded == data
    print("Installation verified!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Python version error**

If you see ``Requires-Python >=3.10`` error:

* Check your Python version: ``python --version``
* Install Python 3.10 or higher
* Use a virtual environment with the correct version

**Import error after installation**

Verify installation:

.. code-block:: bash

    pip show ptoon

If not found, try:

.. code-block:: bash

    pip uninstall ptoon
    pip install ptoon

**Permission errors**

Use ``--user`` flag:

.. code-block:: bash

    pip install --user ptoon

Or use a virtual environment (recommended):

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install ptoon

Virtual Environment
~~~~~~~~~~~~~~~~~~~

We strongly recommend using a virtual environment:

.. code-block:: bash

    # Create virtual environment
    python -m venv venv
    
    # Activate (Linux/macOS)
    source venv/bin/activate
    
    # Activate (Windows)
    venv\Scripts\activate
    
    # Install ptoon
    pip install ptoon

Next Steps
----------

* :doc:`quickstart` - Get started with basic usage
* :doc:`core_api` - Learn the core API
* :doc:`/integrations/overview` - Integrate with LLM providers
