Installation
============

Basic Installation
------------------

The core pytoon library has no dependencies and can be installed with pip:

.. code-block:: bash

    pip install pytoon

Python version requirement: **Python 3.10 or higher**

Optional Dependencies
---------------------

pytoon provides several optional dependency groups for different use cases:

Examples
~~~~~~~~

Install with OpenAI integration support:

.. code-block:: bash

    pip install pytoon[examples]

Includes:
    * ``openai`` - OpenAI Python SDK
    * ``tiktoken`` - Token counting library

Use case: Running integration examples with OpenAI

Benchmark
~~~~~~~~~

Install with benchmarking tools:

.. code-block:: bash

    pip install pytoon[benchmark]

Includes:
    * ``tiktoken`` - Token counting
    * ``faker`` - Test data generation
    * ``tqdm`` - Progress bars

Use case: Running performance benchmarks

LLM Benchmark
~~~~~~~~~~~~~

Install with LLM accuracy benchmark support:

.. code-block:: bash

    pip install pytoon[llm-benchmark]

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

    pip install pytoon[dev]

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

    pip install pytoon[all]

Development Installation
------------------------

For contributors and developers:

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/Justar96/pytoon.git
    cd pytoon

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

    python -c "import pytoon; print(pytoon.__version__)"

Quick functionality test:

.. code-block:: python

    import pytoon
    
    data = {"test": "value"}
    encoded = pytoon.encode(data)
    print(encoded)
    # Output: test: value
    
    decoded = pytoon.decode(encoded)
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

    pip show pytoon

If not found, try:

.. code-block:: bash

    pip uninstall pytoon
    pip install pytoon

**Permission errors**

Use ``--user`` flag:

.. code-block:: bash

    pip install --user pytoon

Or use a virtual environment (recommended):

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install pytoon

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
    
    # Install pytoon
    pip install pytoon

Next Steps
----------

* :doc:`quickstart` - Get started with basic usage
* :doc:`core_api` - Learn the core API
* :doc:`/integrations/overview` - Integrate with LLM providers
