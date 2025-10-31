# ptoon

A Python implementation of [TOON](https://github.com/johannschopplich/toon) (Token-Oriented Object Notation), a text format optimized for LLM token efficiency.

## What is TOON?

TOON is a text format designed to reduce LLM token consumption by 30-60% compared to JSON while maintaining human readability and semantic clarity. It's optimized for common data patterns in LLM applications:

- **Tabular data** (API responses, database records) - uses column-based format
- **Structured objects** - removes redundant syntax like quotes and braces
- **Arrays** - compact inline or list formats based on content

**Key Benefits:**
- 🎯 **30-60% token reduction** - Direct cost savings on LLM API calls
- 📖 **Human-readable** - Easy to understand and debug
- 🔄 **Lossless** - Perfect round-trip encoding/decoding
- 🐍 **Pure Python** - No runtime dependencies

**When to use TOON:**
- Large structured datasets in prompts (RAG, analytics, catalogs)
- Cost-sensitive applications where tokens drive costs
- Context window optimization (fit more data in limited context)

**When to use JSON:**
- Strict API contracts (OpenAI function calling, tool use)
- Tiny payloads (< 100 tokens) where overhead isn't worth it
- Real-time streaming where encoding latency matters

## Quick Start

1. Install `ptoon`:

   ```bash
   pip install ptoon
   ```

2. Encode and decode data while measuring token savings:

```python
import ptoon

# Encode Python data to TOON format
data = {
    "users": [
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Designer"}
    ]
}

toon_str = ptoon.encode(data)
print(toon_str)
# Output:
# users[2]{id, name, role}:
#   1, Alice, Engineer
#   2, Bob, Designer

# Decode TOON back to Python
decoded = ptoon.decode(toon_str)
assert decoded == data

# Compare token efficiency
result = ptoon.estimate_savings(data)
print(f"Savings: {result['savings_percent']:.1f}%")  # 35.7%
```

For optional extras (examples, benchmarks, docs), see the Installation section in the documentation.

## Format Limitations & Best Practices

### Array Nesting Depth

TOON supports up to **2 levels** of array nesting (e.g., `[[1,2], [3,4]]`). Deeper nesting (3+ levels like `[[[1,2]]]`) is intentionally not supported to maintain token efficiency and format simplicity.

**Why this limit exists:** Deep nesting actually uses MORE tokens than JSON. TOON is optimized for common real-world data patterns (API responses, database records, tabular data), which rarely exceed 2 levels of nesting.

**If you have deeply nested data**, consider these token-efficient alternatives:

```python
# ❌ Anti-pattern: Deeply nested tree (3+ levels)
tree = {
    "name": "root",
    "children": [{"name": "child", "children": [{"name": "grandchild"}]}]
}

# ✅ Better: Flat adjacency list (TOON-friendly)
tree_flat = {
    "nodes": [
        {"id": 1, "name": "root", "parent": None},
        {"id": 2, "name": "child", "parent": 1},
        {"id": 3, "name": "grandchild", "parent": 2}
    ]
}
# Result: 50-60% token savings vs nested + works with TOON!
```

**More restructuring patterns:**
- **Trees/hierarchies** → Use adjacency lists with parent IDs
- **3D arrays/tensors** → Flatten with explicit shape metadata
- **Nested collections** → Normalize into separate tables (database-style)

See [`examples/better_patterns_demo.py`](examples/better_patterns_demo.py) for runnable examples with token measurements.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [README](README.md) - Quick start and overview
- [SPEC](SPEC.md) - Formal TOON format specification
- [Changelog](docs/changelog.rst) - Version history and changes
- [docs/](docs/) - Full documentation, guides, and API reference

For detailed guides on token optimization, encoding options, and advanced usage, refer to the documentation in the `docs/` directory.

## API Stability

The core `encode()` and `decode()` functions have stable signatures and behavior. Utility functions (`count_tokens`, `estimate_savings`, `compare_formats`) are additive and optional. Future updates will maintain backward compatibility for core functionality.

## Testing

Install development dependencies and run the test suite with pytest:

```bash
pip install -e ".[dev]"
pytest
```

Useful commands:

- Run a specific module: `pytest tests/test_primitives.py`
- Run with coverage: `pytest --cov=ptoon --cov-report=html`
- Verbose output: `pytest -v`

The test suite covers primitive encoding/decoding, objects (simple, nested, special keys), array formats (inline, tabular, list), delimiter options (comma, tab, pipe), length marker option, round‑trip validation, whitespace/formatting invariants, and non‑JSON type handling.

## Examples

> ⚠️ Running the examples can incur OpenAI API costs. Enable guardrails with `SMALL_DATA=1` and `DRY_RUN=true` (see `examples/.env.example`).

The `examples/` directory contains practical demonstrations of using ptoon with LLM providers.

### OpenAI Integration

See [`examples/openai_integration.py`](examples/openai_integration.py) for a comprehensive example demonstrating:

- Basic Pattern: Encode data with `ptoon.encode()` → send to OpenAI → decode response
- Token Comparison: Measure token savings vs JSON (typically 30-60%)
- RAG Use Case: Question-answering over structured data
- Error Handling: Robust parsing with fallback strategies

Installation:
```bash
pip install -e ".[examples]"
export OPENAI_API_KEY="your-api-key"
```

Run the example:
```bash
python examples/openai_integration.py
```

Expected results:
- Token savings: 30-60% vs JSON
- Cost reduction: Proportional to token savings
- Same semantic accuracy as JSON

See [`examples/README.md`](examples/README.md) for more details and additional examples.

## Benchmarking

ptoon is optimized for token efficiency and performance. The benchmark suite measures:

- **Token Efficiency:** 30-60% reduction vs JSON
- **Speed Performance:** Encode/decode speed comparison
- **Memory Usage:** Memory consumption and output size
- **LLM Accuracy:** Real-world question-answering accuracy

**Quick Start:**

```bash
# Install benchmark dependencies
pip install -e ".[benchmark]"

# Run all benchmarks
python -m benchmarks

# Run specific benchmarks
python -m benchmarks --token-efficiency
```

For detailed benchmark documentation, configuration options, LLM accuracy testing, and results, see [`benchmarks/README.md`](benchmarks/README.md).

## Building Documentation

To build the documentation locally:

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build HTML documentation
cd docs && make html

# Open in browser
open _build/html/index.html  # macOS
# or
xdg-open _build/html/index.html  # Linux
# or
start _build/html/index.html  # Windows
```

The built documentation will be in `docs/_build/html/`.

## Changelog

See [docs/changelog.rst](docs/changelog.rst) for release history and upgrade notes.
