# Vertex AI Setup Guide for LLM Accuracy Benchmark

This guide explains how to use Google Vertex AI instead of OpenAI for running the LLM accuracy benchmark, allowing you to leverage free credits and reduce costs.

## Prerequisites

1. **Google Cloud Account**: Sign up at https://cloud.google.com/
2. **Google Cloud Project**: Create or select a project in the [GCP Console](https://console.cloud.google.com/)
3. **Vertex AI API**: Enable the Vertex AI API for your project
4. **Authentication**: Set up Application Default Credentials (ADC)

## Step-by-Step Setup

### 1. Enable Vertex AI API

```bash
# Using gcloud CLI
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID

# Or visit: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
```

### 2. Set Up Authentication

Choose one of these methods:

#### Option A: User Credentials (Recommended for Development)

```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate with your Google account
gcloud auth application-default login

# Set your default project
gcloud config set project YOUR_PROJECT_ID
```

#### Option B: Service Account (Recommended for Production)

```bash
# Create a service account
gcloud iam service-accounts create toon-benchmark \
    --display-name="TOON Benchmark Service Account"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:toon-benchmark@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/toon-benchmark-key.json \
    --iam-account=toon-benchmark@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/toon-benchmark-key.json
```

### 3. Install Dependencies

```bash
# Install LLM benchmark dependencies (includes Vertex AI SDK)
uv sync --extra llm-benchmark

# Or using pip
pip install -e .[llm-benchmark]
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and set:

```bash
# Required: Your Google Cloud Project ID
VERTEX_PROJECT_ID=your-project-id

# Optional: GCP region (default: us-central1)
VERTEX_LOCATION=us-central1

# Optional: Concurrency (default: 20)
CONCURRENCY=20

# Optional: Dry run mode for testing (limits to 10 questions)
DRY_RUN=false
```

### 5. Run the Benchmark

```bash
# Run with Vertex AI
uv run python -m benchmarks.llm_accuracy --provider vertex

# Or using the CLI shorthand
uv run toon-llm-benchmark --provider vertex

# Dry run with limited questions (saves costs)
uv run python -m benchmarks.llm_accuracy --provider vertex --dry-run

# Specify custom concurrency
uv run python -m benchmarks.llm_accuracy --provider vertex --concurrency 10
```

## Model Selection

The benchmark automatically maps generic model names to Vertex AI models:

| Generic Name | Vertex AI Model | Description |
|-------------|-----------------|-------------|
| `gpt-4`, `gpt-5`, `gpt-4o` | `gemini-1.5-pro-002` | Latest Gemini Pro (best quality) |
| `gpt-4o-mini`, `gpt-3.5-turbo` | `gemini-1.5-flash-002` | Latest Gemini Flash (faster, cheaper) |

You can also specify Vertex AI models directly via environment variables:

```bash
OPENAI_MODEL=gemini-1.5-pro-002
VALIDATION_MODEL=gemini-1.5-flash-002
```

Or use Claude models available on Vertex AI:

```bash
OPENAI_MODEL=claude-3-5-sonnet@20240620
```

## Cost Estimation

Vertex AI pricing (as of 2025):

- **Gemini 1.5 Pro**: ~$3.50 per 1M input tokens, ~$10.50 per 1M output tokens
- **Gemini 1.5 Flash**: ~$0.35 per 1M input tokens, ~$1.05 per 1M output tokens

A full benchmark run (200 questions) typically uses:
- ~500K input tokens (JSON + TOON formats combined)
- ~100K output tokens

Estimated cost per full run:
- With Gemini Pro: ~$3-5
- With Gemini Flash: ~$0.30-0.50

Use `--dry-run` flag to limit to 10 questions for testing (~$0.15-0.25).

## Troubleshooting

### Error: "Application Default Credentials are not available"

**Solution**: Run `gcloud auth application-default login`

### Error: "Permission denied on resource project"

**Solution**: Ensure your account/service account has the `roles/aiplatform.user` role:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/aiplatform.user"
```

### Error: "API [aiplatform.googleapis.com] not enabled"

**Solution**: Enable the Vertex AI API:

```bash
gcloud services enable aiplatform.googleapis.com
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
