"""Provider-aware pricing for LLM benchmark cost estimation.

This module provides accurate cost calculations based on the actual LLM provider
and model being used. Pricing data is sourced from official provider documentation
and updated as of October 2025.

Pricing Sources:
- OpenAI: https://openai.com/api/pricing/
- Google Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/pricing
"""

from __future__ import annotations

import logging
import os
from typing import TypedDict


logger = logging.getLogger(__name__)


class ModelPricing(TypedDict):
    """Pricing information for a specific model."""

    input: float  # Price per 1M input tokens (USD)
    output: float  # Price per 1M output tokens (USD)
    cached_input: float  # Price per 1M cached input tokens (USD)


# Provider-specific pricing (per 1M tokens, USD)
# Last updated: October 31, 2025
PRICING_TABLE: dict[str, dict[str, ModelPricing]] = {
    "openai": {
        # GPT-5 series (launched August 2025)
        "gpt-5": {
            "input": 1.25,
            "output": 10.00,
            "cached_input": 0.125,  # 90% discount
        },
        "gpt-5-mini": {
            "input": 0.15,
            "output": 0.60,
            "cached_input": 0.015,  # 90% discount
        },
        # GPT-4o series
        "gpt-4o": {
            "input": 2.50,
            "output": 10.00,
            "cached_input": 0.250,  # 90% discount
        },
        "gpt-4o-mini": {
            "input": 0.15,
            "output": 0.60,
            "cached_input": 0.015,  # 90% discount
        },
        # GPT-4 Turbo
        "gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00,
            "cached_input": 1.00,  # 90% discount
        },
        # GPT-3.5 Turbo
        "gpt-3.5-turbo": {
            "input": 0.50,
            "output": 1.50,
            "cached_input": 0.05,  # 90% discount
        },
    },
    "vertex": {
        # Gemini 2.5 series (latest stable models as of Oct 2025)
        "gemini-2.5-pro": {
            "input": 1.25,
            "output": 10.00,
            "cached_input": 0.125,  # 90% discount
        },
        "gemini-2.5-flash": {
            "input": 0.30,
            "output": 2.50,
            "cached_input": 0.030,  # 90% discount
        },
        "gemini-2.5-flash-lite": {
            "input": 0.10,
            "output": 0.40,
            "cached_input": 0.010,  # 90% discount
        },
        # Gemini 2.0 series
        "gemini-2.0-flash": {
            "input": 0.0375,
            "output": 0.15,
            "cached_input": 0.00375,  # 90% discount
        },
        "gemini-2.0-flash-lite": {
            "input": 0.01875,
            "output": 0.075,
            "cached_input": 0.001875,  # 90% discount
        },
        # Legacy Gemini 1.5 series (deprecated but still available)
        "gemini-1.5-pro": {
            "input": 1.25,
            "output": 5.00,
            "cached_input": 0.125,  # 90% discount
        },
        "gemini-1.5-flash": {
            "input": 0.075,
            "output": 0.30,
            "cached_input": 0.0075,  # 90% discount
        },
        # Claude models on Vertex AI (partner models)
        "claude-3-5-sonnet@20240620": {
            "input": 3.00,
            "output": 15.00,
            "cached_input": 0.30,  # 90% discount
        },
        "claude-3-opus@20240229": {
            "input": 15.00,
            "output": 75.00,
            "cached_input": 1.50,  # 90% discount
        },
        "claude-3-sonnet@20240229": {
            "input": 3.00,
            "output": 15.00,
            "cached_input": 0.30,  # 90% discount
        },
    },
}


def normalize_model_name(model: str, provider: str) -> str:
    """Normalize model name to match pricing table keys.

    Args:
        model: Raw model name (e.g., 'gpt-5-2025-08-07', 'gemini-2.5-flash-001')
        provider: Provider type ('openai' or 'vertex')

    Returns:
        Normalized model name for pricing lookup
    """
    model_lower = model.lower()

    # Remove version suffixes and timestamps
    # Examples: gpt-5-2025-08-07 -> gpt-5, gemini-2.5-flash-001 -> gemini-2.5-flash
    if provider == "openai":
        # Strip date suffixes (YYYY-MM-DD)
        if model_lower.startswith("gpt-"):
            parts = model_lower.split("-")
            # Keep only gpt-X or gpt-X-mini/turbo
            if len(parts) >= 2:
                base = f"{parts[0]}-{parts[1]}"  # gpt-5
                if len(parts) >= 3 and parts[2] in ("mini", "turbo"):
                    base = f"{base}-{parts[2]}"  # gpt-5-mini
                return base

    elif provider == "vertex":
        # Handle Gemini models
        if model_lower.startswith("gemini-"):
            # Remove version suffixes like -001, -002
            parts = model_lower.split("-")
            # gemini-2.5-flash-001 -> gemini-2.5-flash
            if len(parts) >= 3:
                # Check if last part is a version number
                if parts[-1].isdigit():
                    return "-".join(parts[:-1])
            return model_lower

        # Claude models on Vertex AI - keep as-is (include version)
        if model_lower.startswith("claude-"):
            return model_lower

    return model_lower


def get_model_pricing(
    model: str,
    provider: str,
    use_env_override: bool = True,
) -> ModelPricing:
    """Get pricing information for a specific model and provider.

    Args:
        model: Model identifier (e.g., 'gpt-5', 'gemini-2.5-flash')
        provider: Provider type ('openai' or 'vertex')
        use_env_override: If True, check environment variables for custom pricing

    Returns:
        ModelPricing with input, output, and cached_input prices per 1M tokens

    Raises:
        ValueError: If provider is unknown or model pricing not found
    """
    if provider not in PRICING_TABLE:
        raise ValueError(f"Unknown provider: {provider}. Supported providers: {list(PRICING_TABLE.keys())}")

    # Check environment variable overrides first
    if use_env_override:
        env_input = os.getenv("PRICING_INPUT_PER_1M")
        env_output = os.getenv("PRICING_OUTPUT_PER_1M")
        env_cached = os.getenv("PRICING_CACHED_INPUT_PER_1M")

        if env_input and env_output:
            logger.info(
                f"Using custom pricing from environment variables: input=${env_input}/1M, output=${env_output}/1M"
            )
            return {
                "input": float(env_input),
                "output": float(env_output),
                "cached_input": float(env_cached) if env_cached else float(env_input) * 0.1,
            }

    # Normalize model name for lookup
    normalized_model = normalize_model_name(model, provider)

    # Look up pricing
    provider_pricing = PRICING_TABLE[provider]
    if normalized_model in provider_pricing:
        return provider_pricing[normalized_model]

    # Fallback: try to find a reasonable default
    logger.warning(
        f"Pricing not found for model '{model}' (normalized: '{normalized_model}') "
        f"on provider '{provider}'. Using fallback pricing."
    )

    # Fallback defaults
    if provider == "openai":
        # Default to GPT-5 pricing
        return provider_pricing.get("gpt-5", {"input": 1.25, "output": 10.00, "cached_input": 0.125})
    elif provider == "vertex":
        # Default to Gemini 2.5 Pro pricing
        return provider_pricing.get("gemini-2.5-pro", {"input": 1.25, "output": 10.00, "cached_input": 0.125})

    # Ultimate fallback (should never reach here)
    return {"input": 1.25, "output": 10.00, "cached_input": 0.125}


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    provider: str,
    cached_tokens: int = 0,
) -> float:
    """Calculate estimated cost for an LLM API call.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model identifier
        provider: Provider type ('openai' or 'vertex')
        cached_tokens: Number of cached input tokens (if prompt caching enabled)

    Returns:
        Estimated cost in USD
    """
    pricing = get_model_pricing(model, provider)

    # Calculate regular input tokens (excluding cached)
    regular_input_tokens = max(0, input_tokens - cached_tokens)

    cost = (
        (regular_input_tokens / 1_000_000 * pricing["input"])
        + (cached_tokens / 1_000_000 * pricing["cached_input"])
        + (output_tokens / 1_000_000 * pricing["output"])
    )

    return cost


def format_pricing_info(model: str, provider: str) -> str:
    """Format pricing information as a human-readable string.

    Args:
        model: Model identifier
        provider: Provider type

    Returns:
        Formatted pricing string
    """
    try:
        pricing = get_model_pricing(model, provider)
        return (
            f"${pricing['input']:.2f} per 1M input tokens, "
            f"${pricing['output']:.2f} per 1M output tokens "
            f"(cached: ${pricing['cached_input']:.3f}/1M)"
        )
    except ValueError as e:
        return f"Pricing unavailable: {e}"


__all__ = [
    "ModelPricing",
    "PRICING_TABLE",
    "get_model_pricing",
    "calculate_cost",
    "format_pricing_info",
    "normalize_model_name",
]
