### LLM Accuracy Benchmark Results
Tested with **gpt-5** across **162 questions**

```
JSON         ███████████████████░   95.1% (154/162)
TOON         ███████████████████░   93.8% (152/162)
```

**Advantage:** TOON achieves **93.8% accuracy** (vs JSON's 95.1%) while using **48.4% fewer tokens**.

| Format | Accuracy | Avg Tokens | Avg Latency (ms) | Input Tokens | Output Tokens | Est. Cost |
|--------|----------|------------|------------------|--------------|---------------|-----------|
| `JSON` | 95.1% | 11,082 | 37781.8 | 1,670,766 | 168,320 | $3.7717 |
| `TOON` | 93.8% | 5,718 | 34411.5 | 850,510 | 175,105 | $2.8142 |

*Costs based on OpenAI pricing: $1.25 per 1M input tokens, $10.00 per 1M output tokens. Estimates use regular pricing; actual costs may be ~40-60% lower with prompt caching.*

| Dataset | JSON Tokens | TOON Tokens | Savings | Bar |
|---------|-------------|-------------|---------|-----|
| Uniform employee records (TOON optimal format) | 5,992 | 2,162 | 63.9% | `███████░░░░░░░░░░░░░ 63.9% saved` |
| E-commerce orders with nested structures | 10,680 | 7,103 | 33.5% | `█████████████░░░░░░░ 33.5% saved` |
| Time-series analytics data | 10,969 | 4,499 | 59.0% | `████████░░░░░░░░░░░░ 59.0% saved` |
| Top 100 GitHub repositories | 16,688 | 9,106 | 45.4% | `███████████░░░░░░░░░ 45.4% saved` |

<details>
<summary><strong>View detailed breakdown by dataset</strong></summary>

#### Performance by Dataset

##### Uniform employee records (TOON optimal format)

| Format | Accuracy | Tokens | Correct/Total |
|--------|----------|--------|---------------|
| `JSON` | 89.1% | 5,992 | 49/55 |
| `TOON` | 87.3% | 2,162 | 48/55 |

##### E-commerce orders with nested structures

| Format | Accuracy | Tokens | Correct/Total |
|--------|----------|--------|---------------|
| `JSON` | 97.5% | 10,680 | 39/40 |
| `TOON` | 97.5% | 7,103 | 39/40 |

##### Time-series analytics data

| Format | Accuracy | Tokens | Correct/Total |
|--------|----------|--------|---------------|
| `JSON` | 97.3% | 10,969 | 36/37 |
| `TOON` | 94.6% | 4,499 | 35/37 |

##### Top 100 GitHub repositories

| Format | Accuracy | Tokens | Correct/Total |
|--------|----------|--------|---------------|
| `JSON` | 100.0% | 16,688 | 30/30 |
| `TOON` | 100.0% | 9,106 | 30/30 |

#### Methodology

- **Semantic validation**: LLM-as-judge validates responses semantically (not exact string matching).
- **Token counting**: Using `tiktoken` with `o200k_base` encoding (equivalent to gpt-tokenizer).
- **Question types**: 162 questions across field retrieval, aggregation, and filtering tasks.
- **Datasets**: Faker-generated datasets (seeded for reproducibility) + GitHub repositories.
- **Model**: gpt-5
- **Dual API keys**: Separate OpenAI API keys used for JSON and TOON evaluations to enable independent tracking.

</details>