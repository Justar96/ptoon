# Changelog

All notable changes to ptoon are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2025-11-01

### Fixed
- Removed non-functional CLI entry points (`toon-benchmark`, `toon-llm-benchmark`) that referenced missing benchmarks package
- Benchmarks package no longer included in wheel distribution to reduce package size

### Changed
- Benchmarks are now development tools only and must be run from source repository
- Updated documentation for running benchmarks from source

### Documentation
- Added CHANGELOG.md to repository root
- Added PyPI and project status badges to README
- Enhanced benchmarks/README.md with clear setup and usage instructions
- Added integration testing documentation
- Clarified optional dependencies usage in README

### Developer Experience
- Added GitHub Actions workflow for integration testing
- Added verification tests for wheel contents
- Improved error messages and documentation links

## [0.0.1] - 2025-01-01

### Added
- Core encode/decode functionality for TOON format
- Three array formats: inline, tabular, and list
- Encoding options: delimiter (comma/pipe/tab), indent, length_marker
- Token counting utilities: `count_tokens()`, `estimate_savings()`, `compare_formats()`
- Comprehensive test suite with >90% code coverage
- Benchmark suite: token efficiency, speed, memory, and LLM accuracy tests
- OpenAI integration example
- Complete documentation site with Sphinx
- Type hints throughout codebase with py.typed marker
- Debug logging support via PTOON_DEBUG environment variable

### Features
- 30-60% token savings compared to JSON
- Pure Python implementation with zero runtime dependencies
- Support for Python 3.10, 3.11, 3.12, and 3.13
- JSON-compatible data model
- Configurable encoding options
- Automatic format selection (tabular/inline/list)
- Lossless round-trip encoding/decoding

### Documentation
- User guides: installation, quickstart, core API, format specification
- Integration guides: OpenAI, Anthropic, Google AI, custom clients
- Practical guides: token optimization, error handling, streaming, encoding options
- API reference: core, encoder, decoder, utils, types
- Troubleshooting guide
- Benchmark results and analysis
- Contributing guide

---

## Links

- [PyPI Package](https://pypi.org/project/ptoon/)
- [GitHub Repository](https://github.com/Justar96/ptoon)
- [Documentation](https://github.com/Justar96/ptoon#readme)
- [Issue Tracker](https://github.com/Justar96/ptoon/issues)
- [Format Specification](https://github.com/Justar96/ptoon/blob/main/SPEC.md)

## Version History

See [GitHub Releases](https://github.com/Justar96/ptoon/releases) for detailed release notes and downloadable artifacts.

For detailed technical specification changes, see [SPEC.md](https://github.com/Justar96/ptoon/blob/main/SPEC.md).

