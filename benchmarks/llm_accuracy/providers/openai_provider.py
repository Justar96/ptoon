"""OpenAI provider implementation."""

from __future__ import annotations

import time

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore[assignment]

from . import CompletionResult, LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
        """
        if AsyncOpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package is required for OpenAI provider")
        self.client = AsyncOpenAI(api_key=api_key)

    async def complete(self, prompt: str, model: str) -> CompletionResult:
        """Send completion request to OpenAI API."""
        start = time.perf_counter()

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = (time.perf_counter() - start) * 1000

        content = (
            (response.choices[0].message.content or "") if response.choices else ""
        )

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)

        input_tokens = int(prompt_tokens) if prompt_tokens is not None else 0
        output_tokens = int(completion_tokens) if completion_tokens is not None else 0

        return CompletionResult(
            content=content.strip(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "OpenAI"
