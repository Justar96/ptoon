Changelog
=========

All notable changes to ptoon are documented here.

Version 0.0.1 (Current)
-----------------------

*Initial Release*

Added
~~~~~

* Core encode/decode functionality
* Three array formats: inline, tabular, list
* Encoding options: delimiter, indent, length_marker
* Token counting utilities (``count_tokens``, ``estimate_savings``, ``compare_formats``)
* Comprehensive test suite (>90% coverage)
* Benchmark suite (token efficiency, speed, memory)
* OpenAI integration example
* Complete documentation site
* Type hints throughout codebase
* Debug logging support

Features
~~~~~~~~

* 30-60% token savings vs JSON
* Pure Python implementation (no dependencies)
* Supports Python 3.10+
* JSON-compatible data model
* Configurable encoding options
* Automatic format selection (tabular/inline/list)

Documentation
~~~~~~~~~~~~~

* User guides (installation, quickstart, core API, format spec)
* Integration guides (OpenAI, Anthropic, Google AI, custom clients)
* Practical guides (token optimization, error handling, streaming, encoding options)
* API reference (core, encoder, decoder, utils, types)
* Troubleshooting guide
* Benchmark results
* Contributing guide

Future Versions
---------------

Planned for 0.1.0
~~~~~~~~~~~~~~~~~

* Additional integration examples (Anthropic, Google AI)
* Performance optimizations
* Enhanced error messages
* Streaming support improvements
* Additional utility functions
* More comprehensive documentation

Planned for 0.2.0
~~~~~~~~~~~~~~~~~

* CLI tool for encoding/decoding files
* Configuration file support
* Custom delimiter support
* Additional encoding strategies
* Plugin system for custom encoders

Planned for 1.0.0
~~~~~~~~~~~~~~~~~

* Stable API
* Production-ready
* Complete test coverage
* Comprehensive documentation
* All major LLM providers supported

Version History
---------------

See `GitHub Releases <https://github.com/Justar96/ptoon/releases>`_ for detailed release notes.

See Also
--------

* `SPEC.md <https://github.com/Justar96/ptoon/blob/main/SPEC.md>`_ - Format specification changes
* `Release Notes <https://github.com/Justar96/ptoon/releases>`_
