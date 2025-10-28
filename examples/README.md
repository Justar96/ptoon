# TOON Examples

This directory contains practical examples demonstrating how to use TOON with various LLM providers and use cases.

## Prerequisites

Install TOON with example dependencies:

```bash
pip install -e ".[benchmark]"  # Includes tiktoken and faker
pip install openai  # For OpenAI examples
```

Set your API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Available Examples

### OpenAI Integration (`openai_integration.py`)

Comprehensive example demonstrating TOON usage with OpenAI SDK.

What it covers:
- Basic encode → send → decode pattern
- Token count comparison (JSON vs TOON)
- RAG-style data retrieval with real questions
- Error handling and fallback strategies

Run it:
```bash
python examples/openai_integration.py
```

Expected output:
- Token savings: 30-60% vs JSON
- Cost comparison for different usage volumes
- Side-by-side format examples
- Error handling demonstrations

Use cases:
- Large structured datasets in prompts (RAG, analytics)
- Cost-sensitive applications
- Context window optimization

## When to Use TOON

✅ Use TOON when:
- Sending large structured datasets to LLMs (RAG, analytics, catalogs)
- Token count is a concern (cost or context limits)
- Data has uniform structure (arrays of similar objects)
- You control both encoding and decoding

❌ Don't use TOON when:
- Payloads are tiny (< 100 tokens)
- Using strict JSON contracts (function calling, tool use)
- Data structure is highly heterogeneous
- Real-time streaming where encoding overhead matters

## Performance Characteristics

Based on benchmark results:

| Metric | JSON | TOON | Savings |
|--------|------|------|----------|
| Tokens (100 employees) | ~2,500 | ~1,200 | 52% |
| Tokens (180 analytics) | ~3,800 | ~1,600 | 58% |
| Encoding speed | Baseline | ~0.8x | -20% |
| Decoding speed | Baseline | ~0.9x | -10% |

Key insight: Token savings far outweigh encoding overhead for LLM applications,
where API costs and inference time are dominated by token count.

## Contributing Examples

Want to add an example? Follow these guidelines:

1. Self-contained: Each example should be runnable independently
2. Well-documented: Include docstrings and inline comments
3. Error handling: Demonstrate robust error handling
4. Clear output: Print informative messages and results
5. Dependencies: Document required packages and API keys

See `openai_integration.py` as a template.

## Troubleshooting

Import errors:
```bash
# Install missing dependencies
pip install openai tiktoken faker
```

API key errors:
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set it if missing
export OPENAI_API_KEY="your-key"
```

Module not found errors:
```bash
# Install toon in development mode
pip install -e .
```

## Additional Resources

- [TOON Documentation](../README.md)
- [Benchmark Results](../benchmarks/results/)
- [Test Suite](../tests/)
- [TypeScript Implementation](../toon-ts/)

## License

MIT License - see [LICENSE](../LICENSE) for details.
