Contributing
============

We welcome contributions to ptoon! This guide explains how to contribute.

Development Setup
-----------------

1. Clone Repository
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/Justar96/toon-py.git
    cd toon-py

2. Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -e ".[dev]"

Or with uv:

.. code-block:: bash

    uv sync --extra dev

3. Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest

Development Workflow
--------------------

1. Create a branch:

.. code-block:: bash

    git checkout -b feature/your-feature-name

2. Make changes and add tests

3. Run tests:

.. code-block:: bash

    pytest
    pytest --cov=ptoon --cov-report=html

4. Run linters:

.. code-block:: bash

    ruff check .
    black --check .
    mypy ptoon

5. Format code:

.. code-block:: bash

    black .
    ruff check --fix .

6. Commit changes:

.. code-block:: bash

    git add .
    git commit -m "feat: add new feature"

7. Push and create PR:

.. code-block:: bash

    git push origin feature/your-feature-name

Code Style
----------

* Follow PEP 8
* Use Black for formatting (line length: 120)
* Use Ruff for linting
* Type hints required for public APIs
* Google or NumPy style docstrings

Testing
-------

* All new features must have tests
* Maintain >90% code coverage
* Test edge cases and error conditions
* Use descriptive test names

.. code-block:: python

    def test_encode_simple_dict():
        data = {"key": "value"}
        result = ptoon.encode(data)
        assert result == "key: value"

Documentation
-------------

Building Docs
~~~~~~~~~~~~~

.. code-block:: bash

    cd docs
    make html
    open _build/html/index.html

Documentation Style
~~~~~~~~~~~~~~~~~~~

* Clear and concise
* Include examples
* Link to related sections
* Keep up to date with code changes

Pull Request Guidelines
-----------------------

PR Checklist
~~~~~~~~~~~~

- [ ] Tests pass
- [ ] Code formatted (Black)
- [ ] Linters pass (Ruff, mypy)
- [ ] Documentation updated
- [ ] Descriptive PR title and description

PR Description Template
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: markdown

    ## What
    Brief description of changes
    
    ## Why
    Motivation for changes
    
    ## How
    Implementation approach
    
    ## Testing
    How changes were tested

Types of Contributions
----------------------

Bug Fixes
~~~~~~~~~

1. Report bugs via GitHub Issues
2. Include minimal reproducible example
3. Submit PR with fix and test

New Features
~~~~~~~~~~~~

1. Discuss in GitHub Issues first
2. Ensure alignment with project goals
3. Include tests and documentation
4. Update benchmarks if relevant

Documentation
~~~~~~~~~~~~~

* Fix typos and errors
* Improve clarity
* Add examples
* Expand guides

Performance
~~~~~~~~~~~

* Profile before optimizing
* Include benchmarks
* Document trade-offs
* Maintain correctness

Project Structure
-----------------

.. code-block:: text

    ptoon/
    ├── ptoon/          # Core library
    │   ├── __init__.py  # Public API
    │   ├── encoder.py   # Encoding logic
    │   ├── decoder.py   # Decoding logic
    │   ├── utils.py     # Utilities
    │   └── types.py     # Type definitions
    ├── tests/           # Test suite
    ├── benchmarks/      # Benchmarks
    ├── examples/        # Examples
    ├── docs/            # Documentation
    └── pyproject.toml   # Project config

Community
---------

* Be respectful and inclusive
* Help others
* Share knowledge
* Follow code of conduct

Getting Help
------------

* GitHub Discussions
* GitHub Issues
* Stack Overflow (tag: ``ptoon``)

See Also
--------

* `GitHub Repository <https://github.com/Justar96/toon-py>`_
* `Issue Tracker <https://github.com/Justar96/toon-py/issues>`_
* `Discussions <https://github.com/Justar96/toon-py/discussions>`_
