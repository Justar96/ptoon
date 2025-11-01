"""Google Vertex AI provider implementation."""

from __future__ import annotations

import asyncio
import time
from functools import partial
from pathlib import Path


try:
    import vertexai
    from google.oauth2 import service_account
    from vertexai.generative_models import GenerationConfig, GenerativeModel
except ImportError:  # pragma: no cover
    vertexai = None  # type: ignore[assignment]
    GenerativeModel = None  # type: ignore[assignment]
    GenerationConfig = None  # type: ignore[assignment]
    service_account = None  # type: ignore[assignment]

from . import CompletionResult, LLMProvider


class VertexAIProvider(LLMProvider):
    """Google Vertex AI provider using the latest stable API (Gemini 2.5 series)."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        credentials_path: str | None = None,
    ):
        """Initialize Vertex AI provider.

        Args:
            project_id: Google Cloud project ID
            location: GCP region (default: us-central1)
            credentials_path: Path to service account JSON key file (optional)
                If not provided, uses Application Default Credentials (ADC)
        """
        if vertexai is None or GenerativeModel is None:  # pragma: no cover
            raise RuntimeError(
                "google-cloud-aiplatform>=1.122.0 is required for Vertex AI provider.\n"
                "Install it with: pip install google-cloud-aiplatform\n"
                "Or install LLM benchmark dependencies: pip install -e .[llm-benchmark]"
            )

        self.project_id = project_id
        self.location = location

        # Initialize credentials from JSON key file if provided
        credentials = None
        if credentials_path:
            creds_file = Path(credentials_path).expanduser()
            if not creds_file.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {credentials_path}\n"
                    f"Make sure the JSON key file exists at the specified path."
                )
            credentials = service_account.Credentials.from_service_account_file(str(creds_file))

        # Initialize Vertex AI with credentials or ADC
        vertexai.init(project=project_id, location=location, credentials=credentials)

    async def complete(self, prompt: str, model: str) -> CompletionResult:
        """Send completion request to Vertex AI."""
        start = time.perf_counter()

        # Vertex AI uses synchronous API, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, partial(self._sync_complete, prompt, model))

        latency_ms = (time.perf_counter() - start) * 1000
        return CompletionResult(
            content=response["content"],
            input_tokens=response["input_tokens"],
            output_tokens=response["output_tokens"],
            latency_ms=latency_ms,
        )

    def _sync_complete(self, prompt: str, model: str) -> dict:
        """Synchronous completion call (runs in executor)."""
        # Map common model names to Vertex AI model names
        vertex_model = self._map_model_name(model)

        # Initialize model with generation config for consistency
        model_instance = GenerativeModel(vertex_model)

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.0,  # Deterministic for benchmarking
            max_output_tokens=8192,  # Increased to avoid MAX_TOKENS errors
            top_p=1.0,
        )

        # Generate content with retry logic for rate limits
        max_retries = 3
        retry_delay = 2.0

        for attempt in range(max_retries):
            try:
                response = model_instance.generate_content(
                    prompt,
                    generation_config=generation_config,
                )
                break  # Success, exit retry loop
            except Exception as e:
                error_msg = str(e)
                # Check if it's a rate limit error
                if ("429" in error_msg or "Resource exhausted" in error_msg) and attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = retry_delay * (2**attempt)
                    time.sleep(wait_time)
                    continue
                # Re-raise if not rate limit or max retries exceeded
                raise

        # Extract usage metadata (available in latest API)
        usage_metadata = response.usage_metadata if hasattr(response, "usage_metadata") else None
        input_tokens = getattr(usage_metadata, "prompt_token_count", 0) if usage_metadata else 0
        output_tokens = getattr(usage_metadata, "candidates_token_count", 0) if usage_metadata else 0

        # Extract text content safely
        content = ""
        try:
            if hasattr(response, "text"):
                content = response.text
        except (ValueError, AttributeError) as e:
            # Handle cases where response.text raises an error (e.g., safety filters, MAX_TOKENS)
            # Try to extract from candidates directly
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    parts = candidate.content.parts
                    if parts:
                        content = "".join(part.text for part in parts if hasattr(part, "text"))

            # If still empty, log the error
            if not content:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Could not extract text from response: {e}")

        return {
            "content": content.strip(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    def _map_model_name(self, model: str) -> str:
        """Map generic model names to Vertex AI model identifiers.

        Args:
            model: Generic model name (e.g., 'gpt-4', 'gpt-5', 'claude-3.5')

        Returns:
            Vertex AI model identifier (latest Gemini 2.5 series as of Oct 2025)
        """
        # Mappings to latest stable Gemini 2.5 models (Oct 2025)
        model_map = {
            # Latest Flash models - optimized for speed and cost
            "gpt-5-mini": "gemini-2.5-flash",  # Latest Flash - best price/performance
            "gpt-4o-mini": "gemini-2.5-flash",
            "gpt-3.5-turbo": "gemini-2.5-flash",
            "gpt-4-turbo": "gemini-2.5-flash",
            # Latest Pro models - optimized for quality
            "gpt-5": "gemini-2.5-pro",  # Latest Pro - best quality
            "gpt-4": "gemini-2.5-pro",
            "gpt-4o": "gemini-2.5-pro",
            # Legacy 1.5 models (still available but deprecated)
            "gemini-1.5-pro": "gemini-2.5-pro",
            "gemini-1.5-flash": "gemini-2.5-flash",
            # Claude models available on Vertex AI
            "claude-3.5": "claude-3-5-sonnet@20240620",
            "claude-3-opus": "claude-3-opus@20240229",
            "claude-3-sonnet": "claude-3-sonnet@20240229",
        }

        # If model is already a Vertex AI model name, return as-is
        if model.startswith("gemini-") or model.startswith("claude-"):
            return model

        # Otherwise try to map it
        return model_map.get(model, "gemini-2.5-pro")  # Default to latest Pro model

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "Vertex AI"
