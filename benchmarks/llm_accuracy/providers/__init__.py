"""LLM provider abstraction for benchmark evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class CompletionResult:
    """Result from an LLM completion request."""

    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(self, prompt: str, model: str) -> CompletionResult:
        """Send a completion request to the LLM provider.

        Args:
            prompt: The prompt to send to the model
            model: The model identifier to use

        Returns:
            CompletionResult with the response and usage metrics

        Raises:
            Exception: Provider-specific errors (rate limits, API errors, etc.)
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this provider (e.g., 'OpenAI', 'Vertex AI')."""
        pass


__all__ = ["LLMProvider", "CompletionResult"]
