"""Async evaluation pipeline for LLM accuracy benchmarks.

This module mirrors the TypeScript reference implementation found in the
toon-ts project, providing dual-format (JSON vs TOON) evaluation with
parallelized OpenAI calls, robust error handling, and progress tracking.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any


try:  # Optional dependency for progress reporting
    from tqdm import tqdm
except ImportError:  # pragma: no cover - tqdm is optional
    tqdm = None  # type: ignore[assignment]

try:  # OpenAI SDK (requires v1.2+)
    from openai import APIConnectionError, APIError, RateLimitError
except ImportError:  # pragma: no cover - defer hard failure to runtime use
    APIError = APIConnectionError = RateLimitError = Exception  # type: ignore[assignment]

import ptoon
from benchmarks.datasets import (
    generate_analytics_data,
    generate_nested_dataset,
    generate_tabular_dataset,
    load_github_dataset,
)

from .providers import LLMProvider
from .providers.openai_provider import OpenAIProvider
from .providers.vertex_provider import VertexAIProvider
from .questions import generate_questions
from .types import EvaluationResult, Question
from .validation import validate_answer


logger = logging.getLogger(__name__)


# Evaluation model - can be overridden via OPENAI_MODEL environment variable
# Default: gpt-5-mini (maps to gemini-2.5-flash on Vertex AI - best price/performance)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
DEFAULT_CONCURRENCY = 20
# DRY_RUN_MAX_QUESTIONS: Maximum questions to evaluate when DRY_RUN is enabled.
# Precedence: CLI --dry-run flag takes precedence, otherwise .env DRY_RUN is honored.
DRY_RUN_MAX_QUESTIONS = 10
# Validation model - can be overridden via VALIDATION_MODEL environment variable
# Default: gpt-5 (maps to gemini-2.5-pro on Vertex AI - best quality for validation)
VALIDATION_MODEL = os.getenv("VALIDATION_MODEL", "gpt-5")


def is_dry_run() -> bool:
    """Check if DRY_RUN mode is enabled via environment variable.

    Returns True if DRY_RUN env var is set to 'true' (case-insensitive).
    This function reads the environment at call time, allowing .env files
    loaded after module import to take effect.
    """
    return os.getenv("DRY_RUN", "false").lower() == "true"


_provider_cache: dict[str, LLMProvider] = {}


def _get_provider(
    provider_type: str, json_config: dict[str, str], toon_config: dict[str, str]
) -> tuple[LLMProvider, LLMProvider]:
    """Get or create provider instances for JSON and TOON evaluations.

    Args:
        provider_type: 'openai' or 'vertex'
        json_config: Configuration for JSON evaluation provider
        toon_config: Configuration for TOON evaluation provider

    Returns:
        Tuple of (json_provider, toon_provider)
    """
    cache_key_json = f"{provider_type}_json_{hash(frozenset(json_config.items()))}"
    cache_key_toon = f"{provider_type}_toon_{hash(frozenset(toon_config.items()))}"

    if cache_key_json not in _provider_cache:
        if provider_type == "openai":
            _provider_cache[cache_key_json] = OpenAIProvider(api_key=json_config["api_key"])
        elif provider_type == "vertex":
            _provider_cache[cache_key_json] = VertexAIProvider(
                project_id=json_config["project_id"],
                location=json_config.get("location", "us-central1"),
                credentials_path=json_config.get("credentials_path"),
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    if cache_key_toon not in _provider_cache:
        if provider_type == "openai":
            _provider_cache[cache_key_toon] = OpenAIProvider(api_key=toon_config["api_key"])
        elif provider_type == "vertex":
            _provider_cache[cache_key_toon] = VertexAIProvider(
                project_id=toon_config["project_id"],
                location=toon_config.get("location", "us-central1"),
                credentials_path=toon_config.get("credentials_path"),
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    return _provider_cache[cache_key_json], _provider_cache[cache_key_toon]


def format_datasets(datasets: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Format datasets in both JSON and TOON representations."""

    formatted: dict[str, dict[str, str]] = {"JSON": {}, "TOON": {}}

    for name, data in datasets.items():
        json_str = json.dumps(data, indent=2)
        toon_str = ptoon.encode(data)

        formatted["JSON"][name] = json_str
        formatted["TOON"][name] = toon_str

        logger.info(
            "Formatted dataset '%s': JSON chars=%d, TOON chars=%d",
            name,
            len(json_str),
            len(toon_str),
        )

    return formatted


async def evaluate_single_question(
    question: Question,
    format_name: str,
    formatted_data: str,
    provider: LLMProvider,
    semaphore: asyncio.Semaphore,
    provider_type: str = "openai",
) -> EvaluationResult:
    """Evaluate a single question for a given data format using an LLM provider."""

    prompt = (
        f"Given the following data in {format_name} format:\n\n"
        "```\n"
        f"{formatted_data}\n"
        "```\n\n"
        f"Question: {question['prompt']}\n\n"
        "Provide only the direct answer, without any additional explanation or formatting."
    )

    loop = asyncio.get_running_loop()
    overall_start = time.perf_counter()
    last_latency_ms: float | None = None

    async with semaphore:
        max_attempts = 3
        backoff_seconds = 1.0

        for attempt in range(1, max_attempts + 1):
            attempt_start = time.perf_counter()
            try:
                result = await provider.complete(prompt, MODEL)
                last_latency_ms = result.latency_ms

                is_correct = await loop.run_in_executor(
                    None,
                    validate_answer,
                    result.content,
                    question["ground_truth"],
                    question["prompt"],
                    None,  # api_key
                    True,  # use_fallback - use string comparison for now
                    VALIDATION_MODEL,  # model
                )

                return {
                    "question_id": question["id"],
                    "format": format_name,  # type: ignore[assignment]
                    "model": MODEL,
                    "expected": question["ground_truth"],
                    "actual": result.content,
                    "is_correct": is_correct,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "latency_ms": result.latency_ms,
                    "provider": provider_type,
                }

            except RateLimitError as err:  # type: ignore[misc]
                last_latency_ms = (time.perf_counter() - attempt_start) * 1000
                if attempt == max_attempts:
                    logger.warning(
                        "Rate limit error on question %s (%s) after %d attempts: %s",
                        question["id"],
                        format_name,
                        attempt,
                        err,
                    )
                    break
                sleep_for = backoff_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited on question %s (%s), retrying in %.1fs (attempt %d/%d)",
                    question["id"],
                    format_name,
                    sleep_for,
                    attempt,
                    max_attempts,
                )
                await asyncio.sleep(sleep_for)
            except (APIError, APIConnectionError) as err:  # type: ignore[misc]
                last_latency_ms = (time.perf_counter() - attempt_start) * 1000
                if attempt == max_attempts:
                    logger.error(
                        "API error on question %s (%s) after %d attempts: %s",
                        question["id"],
                        format_name,
                        attempt,
                        err,
                    )
                    break
                logger.warning(
                    "Transient API error on question %s (%s), retrying (attempt %d/%d): %s",
                    question["id"],
                    format_name,
                    attempt,
                    max_attempts,
                    err,
                )
                await asyncio.sleep(1.0)
            except Exception as err:  # noqa: BLE001
                last_latency_ms = (time.perf_counter() - attempt_start) * 1000
                logger.exception(
                    "Unexpected error evaluating question %s (%s): %s",
                    question["id"],
                    format_name,
                    err,
                )
                break

    # Fallback result on failure
    fallback_latency_ms = (
        last_latency_ms if last_latency_ms is not None else (time.perf_counter() - overall_start) * 1000
    )

    return {
        "question_id": question["id"],
        "format": format_name,  # type: ignore[assignment]
        "model": MODEL,
        "expected": question["ground_truth"],
        "actual": "",
        "is_correct": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": fallback_latency_ms,
        "provider": provider_type,
    }


async def evaluate_all_questions(
    questions: list[Question],
    formatted_datasets: dict[str, dict[str, str]],
    json_provider: LLMProvider,
    toon_provider: LLMProvider,
    concurrency: int = DEFAULT_CONCURRENCY,
    provider_type: str = "openai",
) -> list[EvaluationResult]:
    """Evaluate all questions across both JSON and TOON formats."""

    if not questions:
        logger.info("No questions provided for evaluation.")
        return []

    if is_dry_run():
        logger.warning(
            "DRY RUN MODE: Limited to %d questions for cost control",
            DRY_RUN_MAX_QUESTIONS,
        )
        questions = questions[:DRY_RUN_MAX_QUESTIONS]

    semaphore = asyncio.Semaphore(concurrency)

    tasks: list[Callable[[], Awaitable[EvaluationResult]]] = []

    for question in questions:
        dataset_name = question["dataset"]
        try:
            json_payload = formatted_datasets["JSON"][dataset_name]
            toon_payload = formatted_datasets["TOON"][dataset_name]
        except KeyError as err:
            raise KeyError(f"Missing formatted dataset '{dataset_name}' for format evaluation") from err

        tasks.append(
            lambda q=question, data=json_payload: evaluate_single_question(
                q, "JSON", data, json_provider, semaphore, provider_type
            )
        )
        tasks.append(
            lambda q=question, data=toon_payload: evaluate_single_question(
                q, "TOON", data, toon_provider, semaphore, provider_type
            )
        )

    total_tasks = len(tasks)
    logger.info(
        "Starting evaluation: %d questions x 2 formats = %d tasks (concurrency=%d)",
        len(questions),
        total_tasks,
        concurrency,
    )

    progress = tqdm(total=total_tasks, desc="Evaluating", unit="task") if tqdm else None
    completed_counts = defaultdict(int)
    completed_total = 0

    async def _tracked(
        coro_factory: Callable[[], Awaitable[EvaluationResult]],
    ) -> EvaluationResult:
        nonlocal completed_total
        result = await coro_factory()
        completed_counts[result["format"]] += 1
        completed_total += 1
        if progress is not None:
            progress.update(1)
            progress.set_postfix(JSON=completed_counts["JSON"], TOON=completed_counts["TOON"])
        elif completed_total % 10 == 0:
            logger.info(
                "Progress: %d/%d tasks completed (JSON=%d, TOON=%d)",
                completed_total,
                total_tasks,
                completed_counts["JSON"],
                completed_counts["TOON"],
            )
        return result

    coroutines = [_tracked(factory) for factory in tasks]
    results_raw = await asyncio.gather(*coroutines, return_exceptions=True)

    if progress is not None:
        progress.close()

    results: list[EvaluationResult] = []

    for entry in results_raw:
        if isinstance(entry, Exception):
            logger.error("Evaluation task raised an exception: %s", entry)
            continue
        results.append(entry)

    logger.info("Completed evaluation: %d successful results", len(results))
    return results


def run_evaluation(
    questions: list[Question] | None = None,
    provider_type: str = "openai",
    datasets: dict[str, dict[str, Any]] | None = None,
) -> list[EvaluationResult]:
    """Synchronously execute the full evaluation workflow.

    Args:
        questions: Optional list of questions to evaluate. If None, generates all questions.
        provider_type: LLM provider to use ('openai' or 'vertex')
        datasets: Optional dict of datasets. If None, generates default datasets.

    Returns:
        List of evaluation results
    """

    if questions is None:
        questions = generate_questions()

    if datasets is None:
        datasets = {
            "tabular": generate_tabular_dataset(),
            "nested": generate_nested_dataset(),
            "analytics": generate_analytics_data(180),
            "github": load_github_dataset(),
        }

    formatted = format_datasets(datasets)

    # Get provider-specific configuration
    if provider_type == "openai":
        json_api_key = os.getenv("OPENAI_API_KEY_JSON")
        toon_api_key = os.getenv("OPENAI_API_KEY_TOON")

        if not json_api_key or not toon_api_key:
            raise ValueError("Missing OPENAI_API_KEY_JSON or OPENAI_API_KEY_TOON environment variables")

        json_config = {"api_key": json_api_key}
        toon_config = {"api_key": toon_api_key}

    elif provider_type == "vertex":
        project_id = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION", "us-central1")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not project_id:
            raise ValueError("Missing VERTEX_PROJECT_ID environment variable")

        json_config = {
            "project_id": project_id,
            "location": location,
            "credentials_path": credentials_path,
        }
        toon_config = {
            "project_id": project_id,
            "location": location,
            "credentials_path": credentials_path,
        }

    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

    json_provider, toon_provider = _get_provider(provider_type, json_config, toon_config)

    concurrency = int(os.getenv("CONCURRENCY", str(DEFAULT_CONCURRENCY)))

    results = asyncio.run(
        evaluate_all_questions(
            questions,
            formatted,
            json_provider=json_provider,
            toon_provider=toon_provider,
            concurrency=concurrency,
            provider_type=provider_type,
        )
    )

    _log_summary(results)

    # Store the actual model identifier in results metadata
    # This is used by report generation for accurate pricing
    if provider_type == "vertex":
        # Map the generic model name to Vertex AI model name
        from .providers.vertex_provider import VertexAIProvider

        temp_provider = VertexAIProvider(project_id="temp", location="us-central1")
        actual_model = temp_provider._map_model_name(MODEL)
    else:
        actual_model = MODEL

    for result in results:
        result["actual_model"] = actual_model  # type: ignore[typeddict-unknown-key]

    return results


def _log_summary(results: list[EvaluationResult]) -> None:
    if not results:
        logger.info("No results to summarize.")
        return

    by_format: dict[str, dict[str, float]] = defaultdict(lambda: {"correct": 0, "total": 0})
    latencies: list[float] = []

    for result in results:
        fmt = result["format"]
        by_format[fmt]["total"] += 1
        if result["is_correct"]:
            by_format[fmt]["correct"] += 1
        latencies.append(result.get("latency_ms", 0.0))

    summaries = []
    for fmt, stats in by_format.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] else 0.0
        summaries.append(f"{fmt}: {accuracy:.1f}% ({int(stats['correct'])}/{int(stats['total'])})")

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    logger.info(
        "Evaluation summary: %s | Avg latency: %.1f ms",
        "; ".join(summaries),
        avg_latency,
    )


__all__ = [
    "MODEL",
    "DEFAULT_CONCURRENCY",
    "is_dry_run",
    "DRY_RUN_MAX_QUESTIONS",
    "VALIDATION_MODEL",
    "format_datasets",
    "evaluate_single_question",
    "evaluate_all_questions",
    "run_evaluation",
]
