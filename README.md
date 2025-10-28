# Toon (Python)

A Python implementation of [toon](https://github.com/johannschopplich/toon), a Token-Oriented Object Notation for LLMs.

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

The `examples/` directory contains practical demonstrations of using TOON with LLM providers.

### OpenAI Integration

See [`examples/openai_integration.py`](examples/openai_integration.py) for a comprehensive example demonstrating:

- Basic Pattern: Encode data with `toon.encode()` → send to OpenAI → decode response
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

```bash
pip install -e ".[benchmark]"
```

Required packages: `tiktoken` (GPT tokenizer), `faker` (dataset generation). These are optional and only needed to run benchmarks.

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

See `benchmarks/results/` for detailed reports.

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
