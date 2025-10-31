# Quick Start: Using Vertex AI with py-toon Benchmarks

This guide gets you running the LLM accuracy benchmark with Google Vertex AI in under 5 minutes.

## Why Vertex AI?

- **Free credits**: New GCP accounts get $300 in free credits
- **Lower cost**: Gemini 2.5 Flash costs ~$0.30-0.50 per full benchmark (vs $15-25 for GPT-4o)
- **Latest models**: Access to Gemini 2.5 series (Oct 2025) - best price/performance
- **No separate billing**: Use your existing GCP account

## Prerequisites

1. Google Cloud account with a project
2. Vertex AI API enabled
3. Service account JSON key file (recommended) OR gcloud CLI

## Quick Setup (5 minutes)

### 1. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### 2. Create Service Account and Download JSON Key

```bash
# Create service account
gcloud iam service-accounts create toon-benchmark \
    --display-name="TOON Benchmark" \
    --project=YOUR_PROJECT_ID

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:toon-benchmark@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download JSON key
gcloud iam service-accounts keys create ~/toon-vertex-key.json \
    --iam-account=toon-benchmark@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Set Environment Variables

Create `.env` in the project root:

```bash
# Required
VERTEX_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/home/your-user/toon-vertex-key.json

# Optional (defaults shown)
VERTEX_LOCATION=us-central1
CONCURRENCY=20

# Model configuration (uses latest Gemini 2.5)
# OPENAI_MODEL=gpt-5-mini           # Maps to gemini-2.5-flash (default, cost-optimized)
# VALIDATION_MODEL=gpt-5            # Maps to gemini-2.5-pro (default, quality-optimized)
```

### 4. Install Dependencies

```bash
uv sync --extra llm-benchmark
```

### 5. Run Benchmark

```bash
# Dry run first (10 questions, ~$0.02-0.03 with Gemini Flash)
uv run python -m benchmarks.llm_accuracy --provider vertex --dry-run

# Full run (200 questions, ~$0.30-0.50 with Gemini 2.5 Flash default)
uv run python -m benchmarks.llm_accuracy --provider vertex
```

## Model Selection

**Default configuration (optimized for cost):**
- **Benchmark model**: `gpt-5-mini` → `gemini-2.5-flash` (best price/performance)
- **Validation model**: `gpt-5` → `gemini-2.5-pro` (best quality)

The benchmark automatically maps generic model names to latest Vertex AI models (Gemini 2.5 series - Oct 2025):

| Generic Name | Vertex AI Model | Description |
|-------------|-----------------|-------------|
| `gpt-5-mini`, `gpt-4o-mini`, `gpt-3.5-turbo` | `gemini-2.5-flash` | Latest Flash (fastest, cheapest) |
| `gpt-5`, `gpt-4`, `gpt-4o` | `gemini-2.5-pro` | Latest Pro (best quality) |

You can also specify Vertex AI models directly:

```bash
# In .env file
OPENAI_MODEL=gemini-2.5-flash      # For benchmark (cost-optimized)
VALIDATION_MODEL=gemini-2.5-pro    # For validation (quality-optimized)
```

Or use Claude models available on Vertex AI:

```bash
OPENAI_MODEL=claude-3-5-sonnet@20240620
```

## Cost Comparison

**Full benchmark run (200 questions):**

| Provider | Model | Est. Cost |
|----------|-------|-----------|
| OpenAI | GPT-4o | $15-25 |
| OpenAI | GPT-4o-mini | $3-5 |
| Vertex AI | Gemini 2.5 Pro | $3-5 |
| **Vertex AI** | **Gemini 2.5 Flash** | **$0.30-0.50** ✅ |

**97% cost savings** using Gemini 2.5 Flash (default) vs GPT-4o!

**Recommendation**: Start with `--dry-run` to test (~$0.02-0.03), then use default Gemini Flash for full runs.

## Troubleshooting

### "Credentials file not found"

Make sure the path in `GOOGLE_APPLICATION_CREDENTIALS` points to your JSON key file:

```bash
# Check the file exists
ls -la ~/toon-vertex-key.json

# Use absolute path in .env
GOOGLE_APPLICATION_CREDENTIALS=/home/ubuntu/toon-vertex-key.json
```

### "Permission denied on resource project"

Ensure your service account has the `roles/aiplatform.user` role:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:toon-benchmark@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### "API not enabled"

Enable the Vertex AI API:

```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### Rate Limiting

If you hit rate limits, reduce concurrency:

```bash
uv run python -m benchmarks.llm_accuracy --provider vertex --concurrency 5
```

Or set in `.env`:

```bash
CONCURRENCY=5
```

## Alternative: Use gcloud Auth (Not Recommended for Production)

If you don't want to use a JSON key file, you can use gcloud authentication:

```bash
# Authenticate with your user account
gcloud auth application-default login

# Don't set GOOGLE_APPLICATION_CREDENTIALS in .env
# The SDK will use ADC automatically
```

**Note**: Service account JSON keys are recommended for automated/production use.

## Switching Between OpenAI and Vertex AI

You can easily switch between providers:

```bash
# Use OpenAI
uv run python -m benchmarks.llm_accuracy --provider openai

# Use Vertex AI
uv run python -m benchmarks.llm_accuracy --provider vertex
```

Both providers generate compatible results that can be compared using the benchmark's built-in comparison reports.

## Monitoring Usage

Track your Vertex AI usage in the GCP Console:

1. Visit: https://console.cloud.google.com/billing
2. View cost breakdowns by service
3. Set up budget alerts to avoid unexpected charges

## Free Credits

New GCP accounts receive $300 in free credits valid for 90 days. This is typically sufficient for extensive benchmark testing.

Check your credits: https://console.cloud.google.com/billing/credits

## Summary

✅ **Setup**: 5 minutes with JSON key file  
✅ **Cost**: $0.30-0.50 per full run (97% savings vs GPT-4o)  
✅ **Models**: Latest Gemini 2.5 Flash & Pro (Oct 2025)  
✅ **Performance**: Fast, reliable, production-ready  

For more details, see [docs/vertex-ai-setup.md](docs/vertex-ai-setup.md).
