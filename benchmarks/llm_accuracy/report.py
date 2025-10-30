"""Report generation for LLM accuracy benchmarks.

This module provides comprehensive report generation capabilities including:
- Token counting and efficiency analysis
- Accuracy statistics aggregation
- Cost estimation using OpenAI pricing
- Markdown report generation with visualizations
- JSON result serialization
"""

import functools
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict


# Number of timestamped result sets to keep (can be overridden via env var)
DEFAULT_KEEP_LAST_N_RUNS = 10
KEEP_LAST_N_RUNS = int(os.environ.get("KEEP_LAST_N_RUNS", str(DEFAULT_KEEP_LAST_N_RUNS)))

try:
    import tiktoken
except ImportError:
    tiktoken = None

from benchmarks.token_efficiency import generate_bar_chart

from .types import EvaluationResult, Question


# Configure module logger
logger = logging.getLogger(__name__)

# OpenAI Pricing for GPT-5 (August 2025 launch pricing, verified October 2025)
# Official pricing: https://openai.com/api/pricing/
# Can be overridden via environment variables: OPENAI_PRICE_INPUT_PER_1M, OPENAI_PRICE_OUTPUT_PER_1M, OPENAI_PRICE_CACHED_INPUT_PER_1M
GPT5_INPUT_PRICE_PER_1M = float(
    os.environ.get("OPENAI_PRICE_INPUT_PER_1M", "1.25")
)  # Input tokens per million for gpt-5-2025-08-07
GPT5_OUTPUT_PRICE_PER_1M = float(
    os.environ.get("OPENAI_PRICE_OUTPUT_PER_1M", "10.00")
)  # Output tokens per million for gpt-5-2025-08-07
GPT5_CACHED_INPUT_PRICE_PER_1M = float(
    os.environ.get("OPENAI_PRICE_CACHED_INPUT_PER_1M", "0.125")
)  # Cached input tokens (90% discount) - requires prompt caching enabled

# Dataset Metadata
DATASET_DESCRIPTIONS = {
    "tabular": "Uniform employee records (TOON optimal format)",
    "nested": "E-commerce orders with nested structures",
    "analytics": "Time-series analytics data",
    "github": "Top 100 GitHub repositories",
}


class FormatResult(TypedDict):
    """Statistics for a single format (JSON or TOON)."""

    format: str  # "JSON" or "TOON"
    accuracy: float  # 0.0 to 1.0
    total_tokens: int  # average across datasets
    average_latency: float  # milliseconds
    correct_count: int
    total_count: int
    total_input_tokens: int  # sum across all evaluations
    total_output_tokens: int  # sum across all evaluations
    estimated_cost: float  # USD


@functools.lru_cache(maxsize=1)
def _get_tiktoken_encoding():
    """Get cached tiktoken encoding instance."""
    if tiktoken is None:
        raise RuntimeError(
            "tiktoken is not installed. Install it with: pip install tiktoken"
        )
    return tiktoken.get_encoding("o200k_base")


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken o200k_base encoding.

    Args:
        text: String to count tokens in

    Returns:
        Number of tokens in the text

    Raises:
        RuntimeError: If tiktoken is not installed
    """
    encoding = _get_tiktoken_encoding()
    return len(encoding.encode(text))


def calculate_token_counts(formatted_datasets: dict[str, dict[str, str]]) -> dict[str, int]:
    """Calculate token counts for all format+dataset combinations.

    Args:
        formatted_datasets: Structure like:
            {"JSON": {"tabular": "...", "nested": "..."},
             "TOON": {"tabular": "...", "nested": "..."}}

    Returns:
        Token counts dict with keys like "JSON-tabular", "TOON-nested", etc.
    """
    token_counts = {}

    for format_name, datasets in formatted_datasets.items():
        for dataset_name, formatted_text in datasets.items():
            key = f"{format_name}-{dataset_name}"
            token_count = count_tokens(formatted_text)
            token_counts[key] = token_count
            logger.info(f"Token count for {key}: {token_count:,}")

    return token_counts


def calculate_format_results(
    results: list[EvaluationResult],
    token_counts: dict[str, int]
) -> list[FormatResult]:
    """Aggregate per-format statistics from evaluation results.

    Args:
        results: List of evaluation results from all evaluations
        token_counts: Token counts per format+dataset combination

    Returns:
        List of FormatResult dicts, sorted by accuracy descending
    """
    if not results:
        logger.warning("Empty results list provided to calculate_format_results")
        return []

    # Extract unique format names
    format_names = sorted({result["format"] for result in results})
    format_results = []

    for format_name in format_names:
        # Filter results for this format
        format_specific_results = [r for r in results if r["format"] == format_name]

        # Calculate statistics
        correct_count = sum(1 for r in format_specific_results if r["is_correct"])
        total_count = len(format_specific_results)
        accuracy = correct_count / total_count if total_count > 0 else 0.0

        # Calculate average latency
        latencies = [r["latency_ms"] for r in format_specific_results]
        average_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Calculate token totals
        total_input_tokens = sum(r["input_tokens"] for r in format_specific_results)
        total_output_tokens = sum(r["output_tokens"] for r in format_specific_results)

        # Calculate average dataset token count for this format
        format_token_counts = [
            count for key, count in token_counts.items()
            if key.startswith(f"{format_name}-")
        ]
        if format_token_counts:
            avg = sum(format_token_counts) / len(format_token_counts)
            total_tokens = int(round(avg))
        else:
            total_tokens = 0

        # Calculate estimated cost
        # NOTE: This uses regular input token pricing. If prompt caching is enabled,
        # actual costs will be lower (cached tokens are 90% cheaper at $0.125/1M).
        # The OpenAI API response doesn't separate cached vs regular input tokens,
        # so we calculate upper-bound estimates here.
        estimated_cost = (
            (total_input_tokens / 1_000_000 * GPT5_INPUT_PRICE_PER_1M) +
            (total_output_tokens / 1_000_000 * GPT5_OUTPUT_PRICE_PER_1M)
        )

        format_result: FormatResult = {
            "format": format_name,
            "accuracy": accuracy,
            "total_tokens": total_tokens,
            "average_latency": average_latency,
            "correct_count": correct_count,
            "total_count": total_count,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "estimated_cost": estimated_cost,
        }
        format_results.append(format_result)

        logger.debug(
            f"Format {format_name}: {accuracy:.1%} accuracy "
            f"({correct_count}/{total_count}), "
            f"${estimated_cost:.4f} estimated cost"
        )

    # Sort by accuracy descending
    format_results.sort(key=lambda x: x["accuracy"], reverse=True)
    return format_results


def create_progress_bar(value: float, max_value: float, width: int = 20) -> str:
    """Generate ASCII progress bar.

    Args:
        value: Current value
        max_value: Maximum value (scale)
        width: Width of bar in characters

    Returns:
        ASCII bar string like "████████████████░░░░"
    """
    if max_value == 0:
        return '░' * width

    filled = round((value / max_value) * width)
    empty = width - filled
    return '█' * filled + '░' * empty


def generate_markdown_report(
    format_results: list[FormatResult],
    results: list[EvaluationResult],
    questions: list[Question],
    token_counts: dict[str, int],
    model: str
) -> str:
    """Generate comprehensive markdown report.

    Args:
        format_results: Aggregated statistics per format
        results: All evaluation results
        questions: All questions used in evaluation
        token_counts: Token counts per format+dataset
        model: Model name used for evaluation

    Returns:
        Complete markdown report string
    """
    sections = []

    # Section 1: Header and Overview
    sections.append("### LLM Accuracy Benchmark Results")
    sections.append(f"Tested with **{model}** across **{len(questions)} questions**")
    sections.append("")

    # Section 2: Overall Accuracy Comparison
    sections.append("```")
    for format_result in format_results:
        format_name = format_result["format"]
        accuracy = format_result["accuracy"]
        correct = format_result["correct_count"]
        total = format_result["total_count"]

        bar = create_progress_bar(accuracy, 1.0, 20)
        accuracy_pct = accuracy * 100
        sections.append(f"{format_name.ljust(12)} {bar} {accuracy_pct:>6.1f}% ({correct}/{total})")
    sections.append("```")
    sections.append("")

    # Section 3: Summary Comparison
    toon_result = next((r for r in format_results if r["format"] == "TOON"), None)
    json_result = next((r for r in format_results if r["format"] == "JSON"), None)

    if toon_result and json_result:
        toon_accuracy = toon_result["accuracy"] * 100
        json_accuracy = json_result["accuracy"] * 100

        # Guard against division by zero
        if json_result["total_tokens"] > 0:
            token_savings = (1 - toon_result["total_tokens"] / json_result["total_tokens"]) * 100
            sections.append(
                f"**Advantage:** TOON achieves **{toon_accuracy:.1f}% accuracy** "
                f"(vs JSON's {json_accuracy:.1f}%) while using **{token_savings:.1f}% fewer tokens**."
            )
            sections.append("")

    # Section 4: Cost Analysis
    sections.append("| Format | Accuracy | Avg Tokens | Avg Latency (ms) | Input Tokens | Output Tokens | Est. Cost |")
    sections.append("|--------|----------|------------|------------------|--------------|---------------|-----------|")

    for format_result in format_results:
        format_name = format_result["format"]
        accuracy = format_result["accuracy"] * 100
        tokens = format_result["total_tokens"]
        latency = format_result["average_latency"]
        input_tokens = format_result["total_input_tokens"]
        output_tokens = format_result["total_output_tokens"]
        cost = format_result["estimated_cost"]

        sections.append(
            f"| `{format_name}` | {accuracy:.1f}% | {tokens:,} | "
            f"{latency:.1f} | {input_tokens:,} | {output_tokens:,} | ${cost:.4f} |"
        )

    sections.append(
        f"\n*Costs based on OpenAI pricing: ${GPT5_INPUT_PRICE_PER_1M:.2f} per 1M input tokens, "
        f"${GPT5_OUTPUT_PRICE_PER_1M:.2f} per 1M output tokens. "
        f"Estimates use regular pricing; actual costs may be ~40-60% lower with prompt caching.*"
    )
    sections.append("")

    # Section 5: Token Efficiency Breakdown
    sections.append("| Dataset | JSON Tokens | TOON Tokens | Savings | Bar |")
    sections.append("|---------|-------------|-------------|---------|-----|")

    for dataset_name in ["tabular", "nested", "analytics", "github"]:
        json_key = f"JSON-{dataset_name}"
        toon_key = f"TOON-{dataset_name}"

        if json_key in token_counts and toon_key in token_counts:
            json_tokens = token_counts[json_key]
            toon_tokens = token_counts[toon_key]

            # Guard against division by zero
            if json_tokens > 0:
                savings = (json_tokens - toon_tokens) / json_tokens * 100
                bar = generate_bar_chart(savings, max_width=20)
                savings_display = f"{savings:.1f}%"
            else:
                savings_display = "n/a"
                bar = "n/a"

            sections.append(
                f"| {DATASET_DESCRIPTIONS[dataset_name]} | "
                f"{json_tokens:,} | {toon_tokens:,} | {savings_display} | `{bar}` |"
            )

    sections.append("")

    # Section 6: Collapsible Details Section
    sections.append("<details>")
    sections.append("<summary><strong>View detailed breakdown by dataset</strong></summary>")
    sections.append("")

    # Section 6a: Performance by Dataset
    sections.append("#### Performance by Dataset")
    sections.append("")

    # Create question to dataset mapping
    question_dataset_map = {q["id"]: q["dataset"] for q in questions}

    for dataset_name in ["tabular", "nested", "analytics", "github"]:
        sections.append(f"##### {DATASET_DESCRIPTIONS[dataset_name]}")
        sections.append("")
        sections.append("| Format | Accuracy | Tokens | Correct/Total |")
        sections.append("|--------|----------|--------|---------------|")

        # Filter results for this dataset
        dataset_results = [
            r for r in results
            if question_dataset_map.get(r["question_id"]) == dataset_name
        ]

        # Calculate per-format statistics for this dataset
        dataset_format_stats = []
        for format_name in ["JSON", "TOON"]:
            format_dataset_results = [
                r for r in dataset_results if r["format"] == format_name
            ]

            if format_dataset_results:
                correct = sum(1 for r in format_dataset_results if r["is_correct"])
                total = len(format_dataset_results)
                accuracy = (correct / total * 100) if total > 0 else 0.0
                tokens = token_counts.get(f"{format_name}-{dataset_name}", 0)

                dataset_format_stats.append({
                    "format": format_name,
                    "accuracy": accuracy,
                    "tokens": tokens,
                    "correct": correct,
                    "total": total,
                })

        # Sort by accuracy descending
        dataset_format_stats.sort(key=lambda x: x["accuracy"], reverse=True)

        for stat in dataset_format_stats:
            sections.append(
                f"| `{stat['format']}` | {stat['accuracy']:.1f}% | "
                f"{stat['tokens']:,} | {stat['correct']}/{stat['total']} |"
            )

        sections.append("")

    # Section 6b: Methodology
    sections.append("#### Methodology")
    sections.append("")
    sections.append("- **Semantic validation**: LLM-as-judge validates responses semantically (not exact string matching).")
    sections.append("- **Token counting**: Using `tiktoken` with `o200k_base` encoding (equivalent to gpt-tokenizer).")
    sections.append(f"- **Question types**: {len(questions)} questions across field retrieval, aggregation, and filtering tasks.")
    sections.append("- **Datasets**: Faker-generated datasets (seeded for reproducibility) + GitHub repositories.")
    sections.append(f"- **Model**: {model}")
    sections.append("- **Dual API keys**: Separate OpenAI API keys used for JSON and TOON evaluations to enable independent tracking.")
    sections.append("")

    # Section 7: Close details tag
    sections.append("</details>")

    return "\n".join(sections).strip()


def cleanup_old_results(output_dir: Path, keep_last_n: int = KEEP_LAST_N_RUNS) -> None:
    """Remove old timestamped result files, keeping only the most recent N runs.

    Args:
        output_dir: Directory containing benchmark results
        keep_last_n: Number of timestamped result sets to keep

    Note:
        This only removes timestamped files (e.g., report-20251030-125823.md).
        Latest files (report.md, summary.json, raw-results.json) are never removed.
    """
    if keep_last_n <= 0:
        logger.debug("Cleanup disabled (keep_last_n=%d)", keep_last_n)
        return

    if not output_dir.exists():
        return

    # Find all timestamped files (grouped by type)
    patterns = [
        "raw-results-*.json",
        "summary-*.json",
        "report-*.md",
        "comparison-*.md",
    ]

    for pattern in patterns:
        files = list(output_dir.glob(pattern))

        if len(files) <= keep_last_n:
            continue  # Nothing to clean up for this file type

        # Sort by modification time (newest first)
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Remove old files (keep only the most recent N)
        for old_file in files[keep_last_n:]:
            try:
                old_file.unlink()
                logger.info(f"Removed old result file: {old_file.name}")
            except OSError as e:
                logger.warning(f"Failed to remove {old_file.name}: {e}")


def save_results(
    results: list[EvaluationResult],
    format_results: list[FormatResult],
    questions: list[Question],
    token_counts: dict[str, int],
    formatted_datasets: dict[str, dict[str, str]],
    model: str,
    output_dir: Path | None = None
) -> Path:
    """Save all results to disk in timestamped and latest files.

    Creates two sets of files:
    1. Timestamped files (e.g., raw-results-20251030-125823.json) for versioning
    2. Latest files (e.g., raw-results.json) that always point to most recent run

    Args:
        results: All evaluation results
        format_results: Aggregated statistics per format
        questions: All questions used
        token_counts: Token counts per format+dataset
        formatted_datasets: Formatted dataset strings
        model: Model name used
        output_dir: Output directory (defaults to benchmarks/results/llm_accuracy)

    Returns:
        Path to output directory

    Raises:
        OSError: If file operations fail
        PermissionError: If directory creation or file writes fail
    """
    # Setup output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "results" / "llm_accuracy"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Generate timestamp suffix for this run
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")

        # Prepare summary data (used in both timestamped and latest)
        summary = {
            "formatResults": format_results,
            "questions": len(questions),
            "model": model,
            "datasets": [
                {"name": name, "description": desc}
                for name, desc in DATASET_DESCRIPTIONS.items()
            ],
            "tokenCounts": token_counts,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # File 1: raw-results (timestamped + latest)
        raw_json = json.dumps(results, indent=2, ensure_ascii=False)

        raw_results_timestamped = output_dir / f"raw-results-{timestamp}.json"
        raw_results_timestamped.write_text(raw_json + "\n", encoding="utf-8")
        logger.info(f"Saved timestamped raw results to {raw_results_timestamped}")

        raw_results_latest = output_dir / "raw-results.json"
        raw_results_latest.write_text(raw_json + "\n", encoding="utf-8")
        logger.info(f"Saved latest raw results to {raw_results_latest}")

        # File 2: summary (timestamped + latest)
        summary_json = json.dumps(summary, indent=2, ensure_ascii=False)

        summary_timestamped = output_dir / f"summary-{timestamp}.json"
        summary_timestamped.write_text(summary_json + "\n", encoding="utf-8")
        logger.info(f"Saved timestamped summary to {summary_timestamped}")

        summary_latest = output_dir / "summary.json"
        summary_latest.write_text(summary_json + "\n", encoding="utf-8")
        logger.info(f"Saved latest summary to {summary_latest}")

        # File 3: report.md (timestamped + latest)
        markdown = generate_markdown_report(
            format_results, results, questions, token_counts, model
        )

        report_timestamped = output_dir / f"report-{timestamp}.md"
        report_timestamped.write_text(markdown, encoding="utf-8")
        logger.info(f"Saved timestamped markdown report to {report_timestamped}")

        report_latest = output_dir / "report.md"
        report_latest.write_text(markdown, encoding="utf-8")
        logger.info(f"Saved latest markdown report to {report_latest}")

        # Clean up old timestamped files (keep only last N runs)
        cleanup_old_results(output_dir)

        return output_dir

    except (OSError, PermissionError) as e:
        logger.error(f"Failed to save results to {output_dir}: {e}")
        raise


def generate_report(
    results: list[EvaluationResult],
    questions: list[Question],
    formatted_datasets: dict[str, dict[str, str]],
    model: str = "gpt-5",
    output_dir: Path | None = None
) -> dict[str, Any]:
    """Main entry point for report generation.

    Orchestrates the full report generation pipeline:
    1. Calculate token counts for all datasets
    2. Aggregate format statistics
    3. Save results to JSON and markdown files
    4. Return summary dictionary

    Args:
        results: All evaluation results
        questions: All questions used in evaluation
        formatted_datasets: Formatted dataset strings for token counting
        model: Model name used for evaluation
        output_dir: Optional output directory override

    Returns:
        Summary dict with keys:
            - format_results: list of FormatResult dicts
            - token_counts: dict of token counts
            - output_dir: str path to output directory
            - report_path: str path to report.md
            - summary_path: str path to summary.json
            - raw_results_path: str path to raw-results.json

    Raises:
        ValueError: If results or questions are empty
        OSError: If file operations fail
    """
    # Validate inputs
    if not results:
        raise ValueError("Results list is empty")
    if not questions:
        raise ValueError("Questions list is empty")

    logger.info(f"Generating report for {len(results)} evaluation results")

    # Step 1: Calculate token counts
    token_counts = calculate_token_counts(formatted_datasets)

    # Step 2: Calculate format results
    format_results = calculate_format_results(results, token_counts)

    # Step 3: Save all results
    output_path = save_results(
        results, format_results, questions, token_counts,
        formatted_datasets, model, output_dir
    )

    # Step 4: Log summary statistics
    logger.info(f"Total questions evaluated: {len(questions)}")
    for format_result in format_results:
        format_name = format_result["format"]
        accuracy = format_result["accuracy"] * 100
        cost = format_result["estimated_cost"]
        logger.info(
            f"{format_name}: {accuracy:.1f}% accuracy, "
            f"${cost:.4f} estimated cost"
        )

    # Calculate token savings if both formats exist
    if len(format_results) >= 2:
        json_result = next((r for r in format_results if r["format"] == "JSON"), None)
        toon_result = next((r for r in format_results if r["format"] == "TOON"), None)
        if json_result and toon_result and json_result["total_tokens"] > 0:
            savings_pct = (
                (1 - toon_result["total_tokens"] / json_result["total_tokens"]) * 100
            )
            logger.info(f"TOON token savings: {savings_pct:.1f}%")

    # Step 5: Return summary
    return {
        "format_results": format_results,
        "token_counts": token_counts,
        "output_dir": str(output_path),
        "report_path": str(output_path / "report.md"),
        "summary_path": str(output_path / "summary.json"),
        "raw_results_path": str(output_path / "raw-results.json"),
    }


# Module exports
__all__ = [
    "count_tokens",
    "calculate_token_counts",
    "calculate_format_results",
    "create_progress_bar",
    "generate_markdown_report",
    "cleanup_old_results",
    "save_results",
    "generate_report",
    "FormatResult",
    "KEEP_LAST_N_RUNS",
]
