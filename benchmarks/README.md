# ptoon Benchmarks

This directory contains comprehensive benchmarks for measuring ptoon's token efficiency, speed performance, memory usage, and LLM accuracy compared to JSON.

## Important Note

**Benchmarks are development tools** and are **not included in the PyPI package**. To run benchmarks, you must clone the repository and install from source.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Justar96/ptoon
cd ptoon
```

### 2. Install Benchmark Dependencies

Install benchmark dependencies using the `[benchmark]` extra:

```bash
pip install -e ".[benchmark]"
# or using uv (recommended)
uv sync --extra benchmark
```

This installs:
- `tiktoken` - GPT tokenizer for token counting
- `faker` - Dataset generation
- `tqdm` - Progress bars

For LLM accuracy benchmarks, install additional dependencies:

```bash
pip install -e ".[llm-benchmark]"
```

### 3. Run Benchmarks

**All benchmarks:**
```bash
python -m benchmarks
# or using uv
uv run python -m benchmarks
```

**Specific benchmarks:**
```bash
# Token efficiency only
python -m benchmarks --token-efficiency

# Speed benchmark only
python -m benchmarks --speed

# Memory benchmark only
python -m benchmarks --memory

# Real-world API validation
python -m benchmarks --realworld

# JSON output
python -m benchmarks --all --json

# Help
python -m benchmarks --help
```

Results are written to `benchmarks/results/` as markdown reports.

## Benchmark Types

### 1. Token Efficiency

Measures token count reduction vs JSON using GPT tokenizers.

**Metrics:**
- Token count (JSON vs TOON)
- Percentage savings
- Absolute token reduction

**Expected Results:**
- 30-60% token reduction vs JSON
- Varies by data structure (tabular data shows highest savings)

**Report:** [`results/token-efficiency.md`](results/token-efficiency.md)

### 2. Speed Performance

Measures encoding/decoding speed vs Python stdlib JSON.

**Metrics:**
- Encode time (ms)
- Decode time (ms)
- Throughput (ops/sec)

**Expected Results:**
- JSON may be faster (C-optimized implementation)
- TOON focuses on token savings over encoding speed
- For LLM applications, token count is the primary cost driver

**Report:** [`results/speed-benchmark.md`](results/speed-benchmark.md)

### 3. Memory Usage

Measures memory consumption during encoding/decoding and output size.

**Metrics:**
- Peak memory usage
- Output size (bytes)
- Memory efficiency

**Expected Results:**
- Comparable memory usage in typical datasets
- Smaller output size due to format efficiency

**Report:** [`results/memory-benchmark.md`](results/memory-benchmark.md)

### 4. Real-World API Response Validation

Validates TOON format compatibility with diverse real-world API responses and measures token efficiency across different API patterns.

**Metrics:**
- Format compatibility (roundtrip validation)
- Token count reduction vs JSON
- Character size reduction
- Compatibility rate by API pattern type

**API Patterns Tested:**
- GitHub API (repositories, users, issues, pull requests)
- OpenAPI/Swagger specifications
- GraphQL responses (nested queries, fragments, unions)
- REST pagination (cursor-based, offset-based, link headers)
- JSON-LD linked data (Schema.org, Activity Streams)

**Data Source:**
The benchmark uses **statically curated JSON samples** from `data/realworld/`. Automatic data collectors are **not implemented** to ensure:
- Reproducible benchmark runs
- No dependency on external API availability
- Consistent test data for regression testing
- No API keys or credentials required

See [`data/realworld/README.md`](data/realworld/README.md) for details on adding new samples.

**Expected Results:**
- High compatibility rate (>95% of samples should pass roundtrip validation)
- Token savings vary by pattern: 30-50% for tabular data, 20-40% for nested structures
- Identifies any edge cases where TOON format may need adjustments

**Report:** [`results/realworld-benchmark.md`](results/realworld-benchmark.md)

### 5. LLM Accuracy Benchmark

Measures how well LLMs can extract information from TOON vs JSON formats using real question-answering tasks.

**What it measures:**
- Accuracy of information extraction (TOON vs JSON)
- Token efficiency in real LLM scenarios
- Cost and latency comparison

**Installation:**

```bash
pip install -e ".[llm-benchmark]"
```

**Configuration:**

The benchmark supports both OpenAI and Google Vertex AI providers.

**Option 1: OpenAI (default)**

Set up dual OpenAI API keys for independent tracking:

```bash
export OPENAI_API_KEY_JSON="your-json-evaluation-key"
export OPENAI_API_KEY_TOON="your-toon-evaluation-key"
```

**Option 2: Google Vertex AI (recommended for free credits)**

Set up Vertex AI credentials:

```bash
# Set your Google Cloud project ID
export VERTEX_PROJECT_ID="your-project-id"
export VERTEX_LOCATION="us-central1"  # Optional, defaults to us-central1

# Authenticate with gcloud
gcloud auth application-default login
```

For detailed Vertex AI setup instructions, see [`../docs/vertex-ai-setup.md`](../docs/vertex-ai-setup.md).

**Running the benchmark:**

```bash
# Full benchmark with OpenAI (default)
python -m benchmarks.llm_accuracy

# Full benchmark with Vertex AI
python -m benchmarks.llm_accuracy --provider vertex

# Dry run (limited questions for cost control)
python -m benchmarks.llm_accuracy --provider vertex --dry-run

# Custom concurrency (default: 20)
python -m benchmarks.llm_accuracy --provider vertex --concurrency 10

# Verbose output
python -m benchmarks.llm_accuracy --provider vertex --verbose

# Regenerate report from existing results
python -m benchmarks.llm_accuracy --regenerate-report

# Or using uv
uv run python -m benchmarks.llm_accuracy --provider vertex
```

**Environment variables:**

For OpenAI:
- `OPENAI_API_KEY_JSON` - API key for JSON format evaluation (required)
- `OPENAI_API_KEY_TOON` - API key for TOON format evaluation (required)

For Vertex AI:
- `VERTEX_PROJECT_ID` - Your Google Cloud project ID (required)
- `VERTEX_LOCATION` - GCP region (optional, default: us-central1)
- `CONCURRENCY` - Parallel evaluation concurrency (default: 20)
- `DRY_RUN` - Enable dry-run mode (default: false)
- `VERBOSE` - Enable verbose logging (default: false)
- `KEEP_LAST_N_RUNS` - Number of historical result sets to keep (default: 10, set to 0 to disable cleanup)

**Versioning and Comparison:**

- Each benchmark run creates **timestamped files** for historical tracking
- **Latest files** (`report.md`, `summary.json`, `raw-results.json`) always contain the most recent results
- **Automatic comparison reports** are generated comparing current run to previous run
- **Auto-cleanup**: Only the last 10 timestamped result sets are kept (configurable via `KEEP_LAST_N_RUNS`)
- Results are tracked in git for permanent version history

**Report:** [`results/llm_accuracy/report.md`](results/llm_accuracy/report.md)

For more details, see [`llm_accuracy/README.md`](llm_accuracy/README.md).

## Benchmark Datasets

All datasets use seeded randomness for reproducible results:

1. **GitHub Repositories** - 100 uniform records (optimal for tabular format)
2. **Daily Analytics** - 180 days of time-series metrics
3. **E-Commerce Orders** - Nested structures with customer and items
4. **Employee Records** - 100 uniform employee records

Datasets are defined in [`datasets.py`](datasets.py).

## Performance Trade-offs

| Aspect | JSON | TOON | Notes |
|--------|------|------|-------|
| Token count | Baseline | -30% to -60% | Varies by data structure |
| Encoding speed | Baseline | ~0.8x | Python implementation |
| Decoding speed | Baseline | ~0.9x | Optimized parser |
| LLM inference | Baseline | Faster | Fewer tokens to process |
| API cost | Baseline | -30% to -60% | Proportional to tokens |

**Key Insight:** For LLM applications, token count is the primary cost driver, not encoding time. TOON's 30-60% token reduction translates directly to cost savings and faster inference.

## Expected Results

- **Token savings:** 30-60% reduction vs JSON (varies by dataset structure)
- **Speed:** JSON may be faster (C-optimized); TOON focuses on token savings
- **Memory:** Comparable in typical datasets
- **LLM accuracy:** Equivalent to JSON for information extraction

For LLM applications, token count is the primary cost driver; encoding overhead is usually negligible compared to inference time.

## Benchmark Results

All benchmark results are stored in the [`results/`](results/) directory:

- [Token Efficiency Results](results/token-efficiency.md)
- [Speed Benchmark](results/speed-benchmark.md)
- [Memory Benchmark](results/memory-benchmark.md)
- [Real-World API Validation](results/realworld-benchmark.md)
- [LLM Accuracy Report](results/llm_accuracy/report.md)

## Contributing

When adding new benchmarks:

1. Add dataset generation to `datasets.py`
2. Create benchmark script in `benchmarks/`
3. Update `run_benchmarks.py` to include new benchmark
4. Document expected results and interpretation
5. Add results to `results/` directory
6. For real-world benchmarks, add sample API responses to `data/realworld/` with proper documentation

