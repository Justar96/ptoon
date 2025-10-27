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
