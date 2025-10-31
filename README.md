# Toon (Python)

[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://pytoon.readthedocs.io/)

A Python implementation of [toon](https://github.com/johannschopplich/toon), a Token-Oriented Object Notation for LLMs.

## Quick Start

1. Install `pytoon`:

   ```bash
   pip install pytoon
   ```

2. Encode and decode data while measuring token savings:

```python
import pytoon

# Encode Python data to TOON format
data = {
    "users": [
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Designer"}
    ]
}

toon_str = pytoon.encode(data)
print(toon_str)
# Output:
# users[2]{id, name, role}:
#   1, Alice, Engineer
#   2, Bob, Designer

# Decode TOON back to Python
decoded = pytoon.decode(toon_str)
assert decoded == data

# Compare token efficiency
result = pytoon.estimate_savings(data)
print(f"Savings: {result['savings_percent']:.1f}%")  # 35.7%
```

For optional extras (examples, benchmarks, docs), see the [Installation guide](https://pytoon.readthedocs.io/en/latest/installation.html).

For more details, see the [Quick Start guide](https://pytoon.readthedocs.io/en/latest/user_guide/quickstart.html).

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

Comprehensive documentation is available at:

- **[Read the Docs](https://pytoon.readthedocs.io/)** (full documentation, guides, API reference)
- [Changelog](https://pytoon.readthedocs.io/en/latest/changelog.html) (version history and changes)
- [README](README.md) (quick start and overview)
- [SPEC](SPEC.md) (formal TOON format specification)

For detailed guides on token optimization, encoding options, and advanced usage, refer to the full documentation.

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
- Run with coverage: `pytest --cov=toon --cov-report=html`
- Verbose output: `pytest -v`

The test suite covers primitive encoding/decoding, objects (simple, nested, special keys), array formats (inline, tabular, list), delimiter options (comma, tab, pipe), length marker option, round‑trip validation, whitespace/formatting invariants, and non‑JSON type handling.

## Examples

> ⚠️ Running the examples can incur OpenAI API costs. Enable guardrails with `SMALL_DATA=1` and `DRY_RUN=true` (see `examples/.env.example`).

The `examples/` directory contains practical demonstrations of using TOON with LLM providers.

### OpenAI Integration

See [`examples/openai_integration.py`](examples/openai_integration.py) for a comprehensive example demonstrating:

- Basic Pattern: Encode data with `pytoon.encode()` → send to OpenAI → decode response
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

### When to Use TOON with LLMs

✅ Ideal use cases:
- Large structured datasets in prompts (RAG, analytics, catalogs)
- Cost-sensitive applications (tokens = primary cost driver)
- Context window optimization (fit more data in limited context)
- Repeated queries over the same dataset

❌ Not recommended for:
- Tiny payloads (< 100 tokens) where overhead isn't worth it
- Strict JSON contracts (OpenAI function calling, tool use)
- Real-time streaming where encoding latency matters
- Highly heterogeneous data structures

Key insight: For LLM applications, token count is the primary cost driver, not encoding time. TOON's 30-60% token reduction translates directly to cost savings and faster inference.

### Performance Trade-offs

| Aspect | JSON | TOON | Notes |
|--------|------|------|-------|
| Token count | Baseline | -30% to -60% | Varies by data structure |
| Encoding speed | Baseline | ~0.8x | Python implementation |
| Decoding speed | Baseline | ~0.9x | Optimized parser |
| LLM inference | Baseline | Faster | Fewer tokens to process |
| API cost | Baseline | -30% to -60% | Proportional to tokens |

See [`examples/README.md`](examples/README.md) for more details and additional examples.

## Benchmarking

TOON is optimized for token efficiency and performance. The benchmark suite measures token count reduction, encoding/decoding speed, and memory usage compared to JSON.

### Installing Benchmark Dependencies

Install benchmark dependencies using the `[benchmark]` extra:

```bash
pip install -e ".[benchmark]"
```

This installs `tiktoken` (GPT tokenizer), `faker` (dataset generation), and `tqdm` (progress bars). These are optional and only needed to run benchmarks. See the [Installation guide](https://pytoon.readthedocs.io/en/latest/installation.html) for more details on available extras.

### Running Benchmarks

- All benchmarks: `python -m benchmarks` or `toon-benchmark`
- Token efficiency only: `python -m benchmarks --token-efficiency`
- JSON output: `python -m benchmarks --all --json`
- Help: `python -m benchmarks --help`

Results are written to `benchmarks/results/` as markdown reports.

### Benchmark Types

- Token Efficiency: Token count reduction vs JSON (typically 30–60% savings)
- Speed Performance: Encode/decode speed vs Python stdlib JSON
- Memory Usage: Memory consumption during encoding/decoding and output size

See [`benchmarks/results/`](benchmarks/results/) for detailed reports:
- [Token Efficiency Results](benchmarks/results/token-efficiency.md)
- [Speed Benchmark](benchmarks/results/speed-benchmark.md)
- [Memory Benchmark](benchmarks/results/memory-benchmark.md)
- [LLM Accuracy Report](benchmarks/results/llm_accuracy/report.md) - Compares TOON vs JSON accuracy with real LLMs

### LLM Accuracy Benchmark

The LLM accuracy benchmark measures how well LLMs can extract information from TOON vs JSON formats using real question-answering tasks.

**Installation:**

```bash
pip install -e ".[llm-benchmark]"
```

**Configuration:**

Set up dual OpenAI API keys for independent tracking (allows monitoring JSON and TOON evaluations separately in the OpenAI console):

```bash
export OPENAI_API_KEY_JSON="your-json-evaluation-key"
export OPENAI_API_KEY_TOON="your-toon-evaluation-key"
```

**Running the benchmark:**

```bash
# Full benchmark
uv run toon-llm-benchmark

# Dry run (limited questions for cost control)
uv run toon-llm-benchmark --dry-run

# Custom concurrency (default: 20)
uv run toon-llm-benchmark --concurrency 10

# Verbose output
uv run toon-llm-benchmark --verbose

# Regenerate report from existing results
uv run toon-llm-benchmark --regenerate-report
```

**Environment variables:**

- `OPENAI_API_KEY_JSON` - API key for JSON format evaluation (required)
- `OPENAI_API_KEY_TOON` - API key for TOON format evaluation (required)
- `CONCURRENCY` - Parallel evaluation concurrency (default: 20)
- `DRY_RUN` - Enable dry-run mode (default: false)
- `VERBOSE` - Enable verbose logging (default: false)
- `KEEP_LAST_N_RUNS` - Number of historical result sets to keep (default: 10, set to 0 to disable cleanup)

See `examples/.env.example` for full configuration details and `benchmarks/llm_accuracy/README.md` for more information.

### Datasets

- GitHub Repositories: 100 uniform records (tabular optimal)
- Daily Analytics: 180 days of time-series metrics
- E-Commerce Orders: Nested structures with customer and items
- Employee Records: 100 uniform employee records

Datasets use seeded randomness for reproducible results.

### Expected Results

- Token savings: 30–60% reduction vs JSON (varies by dataset structure)
- Speed: JSON may be faster (C-optimized); TOON focuses on token savings
- Memory: Comparable in typical datasets

For LLM applications, token count is the primary cost driver; encoding overhead is usually negligible compared to inference time.

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

## Migration from Earlier Versions

**Removed OpenAI Wrapper (v0.0.1+)**

The `pytoon.openai` module and wrapper functions have been removed to keep the library focused on encoding/decoding. Use the direct-encode pattern with the raw OpenAI SDK instead:

```python
import pytoon
from openai import OpenAI

client = OpenAI()

# Encode data to TOON format
data = {"employees": [...]}  # Your data
toon_str = pytoon.encode(data)

# Send to OpenAI with TOON-formatted data
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Data:\n{toon_str}\n\nQuestion: How many employees?"}
    ]
)

# Decode TOON responses if needed
if "format: toon" in response.choices[0].message.content.lower():
    result = pytoon.decode(response.choices[0].message.content)
```

See [`examples/openai_integration.py`](examples/openai_integration.py) for a complete working example with token comparison, error handling, and RAG patterns.

**Deprecated Imports:**

- `from pytoon.openai import encode_and_send` ❌ (removed)
- `from pytoon import encode; from openai import OpenAI` ✅ (use this)

## Changelog

See [docs/changelog.rst](docs/changelog.rst) or the [published changelog](https://pytoon.readthedocs.io/en/latest/changelog.html) for release history and upgrade notes.
