"""Comparison utilities for LLM accuracy benchmark results.

This module provides tools for comparing benchmark results across runs to track
improvements and regressions over time.

Features:
- Load and compare results from different timestamps
- Generate markdown comparison reports
- Calculate delta metrics (accuracy, cost, latency, tokens)
- Automatic detection of most recent previous run
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

from .report import DATASET_DESCRIPTIONS, FormatResult


# Configure module logger
logger = logging.getLogger(__name__)


class ComparisonMetrics(TypedDict):
    """Delta metrics between two benchmark runs."""

    accuracy_delta: float  # Percentage point change
    token_delta: float  # Percentage change in token count
    latency_delta: float  # Percentage change in latency
    cost_delta: float  # Percentage change in cost
    input_token_delta: int  # Absolute change in input tokens
    output_token_delta: int  # Absolute change in output tokens


def find_previous_results(output_dir: Path) -> Path | None:
    """Find the most recent previous summary file.

    Args:
        output_dir: Directory containing benchmark results

    Returns:
        Path to most recent timestamped summary file, or None if not found
    """
    if not output_dir.exists():
        logger.warning(f"Output directory does not exist: {output_dir}")
        return None

    # Find all timestamped summary files
    summary_files = list(output_dir.glob("summary-*.json"))

    if not summary_files:
        logger.info("No previous benchmark results found")
        return None

    # Sort by modification time (most recent first)
    summary_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Return most recent (skip the latest.json if it exists)
    for summary_file in summary_files:
        # Skip if this is the current run (very recent file)
        age_seconds = datetime.now().timestamp() - summary_file.stat().st_mtime
        if age_seconds > 10:  # File is older than 10 seconds, likely previous run
            logger.info(f"Found previous results: {summary_file}")
            return summary_file

    logger.info("No previous results found (only current run exists)")
    return None


def load_summary(summary_path: Path) -> dict[str, Any]:
    """Load summary JSON from file.

    Args:
        summary_path: Path to summary.json or summary-TIMESTAMP.json

    Returns:
        Parsed summary dictionary

    Raises:
        FileNotFoundError: If summary file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not summary_path.exists():
        raise FileNotFoundError(f"Summary file not found: {summary_path}")

    try:
        content = summary_path.read_text(encoding="utf-8")
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {summary_path}: {e}")
        raise


def calculate_comparison_metrics(current: FormatResult, previous: FormatResult) -> ComparisonMetrics:
    """Calculate delta metrics between two format results.

    Args:
        current: Current run's format result
        previous: Previous run's format result

    Returns:
        ComparisonMetrics with delta values
    """
    # Accuracy delta (percentage point change)
    accuracy_delta = (current["accuracy"] - previous["accuracy"]) * 100

    # Token delta (percentage change)
    if previous["total_tokens"] > 0:
        token_delta = (current["total_tokens"] - previous["total_tokens"]) / previous["total_tokens"] * 100
    else:
        token_delta = 0.0

    # Latency delta (percentage change)
    if previous["average_latency"] > 0:
        latency_delta = (current["average_latency"] - previous["average_latency"]) / previous["average_latency"] * 100
    else:
        latency_delta = 0.0

    # Cost delta (percentage change)
    if previous["estimated_cost"] > 0:
        cost_delta = (current["estimated_cost"] - previous["estimated_cost"]) / previous["estimated_cost"] * 100
    else:
        cost_delta = 0.0

    # Token deltas (absolute change)
    input_token_delta = current["total_input_tokens"] - previous["total_input_tokens"]
    output_token_delta = current["total_output_tokens"] - previous["total_output_tokens"]

    return ComparisonMetrics(
        accuracy_delta=accuracy_delta,
        token_delta=token_delta,
        latency_delta=latency_delta,
        cost_delta=cost_delta,
        input_token_delta=input_token_delta,
        output_token_delta=output_token_delta,
    )


def format_delta(value: float, is_percentage: bool = True, inverse: bool = False) -> str:
    """Format a delta value with appropriate sign and color indicator.

    Args:
        value: Delta value to format
        is_percentage: If True, add % suffix
        inverse: If True, negative is good (e.g., for cost/latency reduction)

    Returns:
        Formatted string with sign and indicator
    """
    # Determine if this is an improvement
    is_improvement = (value < 0) if inverse else (value > 0)

    # Format the value
    formatted = f"{value:+.1f}%" if is_percentage else f"{value:+.0f}"

    # Add indicator
    if abs(value) < 0.05:  # Negligible change
        indicator = "→"
    elif is_improvement:
        indicator = "✓"
    else:
        indicator = "✗"

    return f"{indicator} {formatted}"


def generate_comparison_report(
    current_summary: dict[str, Any],
    previous_summary: dict[str, Any],
    current_timestamp: str | None = None,
    previous_timestamp: str | None = None,
) -> str:
    """Generate markdown comparison report between two benchmark runs.

    Args:
        current_summary: Current run's summary data
        previous_summary: Previous run's summary data
        current_timestamp: Optional timestamp string for current run
        previous_timestamp: Optional timestamp string for previous run

    Returns:
        Markdown-formatted comparison report
    """
    sections = []

    # Header
    sections.append("## Benchmark Comparison Report")
    sections.append("")

    # Timestamps
    if current_timestamp and previous_timestamp:
        sections.append(f"**Current run:** {current_timestamp}")
        sections.append(f"**Previous run:** {previous_timestamp}")
    else:
        current_ts = current_summary.get("timestamp", "unknown")
        previous_ts = previous_summary.get("timestamp", "unknown")
        sections.append(f"**Current run:** {current_ts}")
        sections.append(f"**Previous run:** {previous_ts}")
    sections.append("")

    # Extract format results
    current_formats: list[FormatResult] = current_summary.get("formatResults", [])
    previous_formats: list[FormatResult] = previous_summary.get("formatResults", [])

    # Create lookup by format name
    current_by_format = {f["format"]: f for f in current_formats}
    previous_by_format = {f["format"]: f for f in previous_formats}

    # Overall comparison table
    sections.append("### Overall Metrics Comparison")
    sections.append("")
    sections.append("| Format | Accuracy | Avg Tokens | Avg Latency | Cost | Status |")
    sections.append("|--------|----------|------------|-------------|------|--------|")

    for format_name in ["JSON", "TOON"]:
        if format_name not in current_by_format or format_name not in previous_by_format:
            continue

        current = current_by_format[format_name]
        previous = previous_by_format[format_name]
        metrics = calculate_comparison_metrics(current, previous)

        accuracy_delta = format_delta(metrics["accuracy_delta"], is_percentage=False)
        token_delta = format_delta(metrics["token_delta"], inverse=True)
        latency_delta = format_delta(metrics["latency_delta"], inverse=True)
        cost_delta = format_delta(metrics["cost_delta"], inverse=True)

        # Overall status
        improvements = sum(
            1
            for v in [
                metrics["accuracy_delta"] > 0,
                metrics["token_delta"] < 0,
                metrics["latency_delta"] < 0,
                metrics["cost_delta"] < 0,
            ]
            if v
        )

        if improvements >= 3:
            status = "🟢 Better"
        elif improvements >= 2:
            status = "🟡 Mixed"
        else:
            status = "🔴 Worse"

        sections.append(
            f"| `{format_name}` | {accuracy_delta} | {token_delta} | {latency_delta} | {cost_delta} | {status} |"
        )

    sections.append("")
    sections.append("*Legend: ✓ = improvement, ✗ = regression, → = negligible change*")
    sections.append("")

    # Token efficiency by dataset
    current_tokens = current_summary.get("tokenCounts", {})
    previous_tokens = previous_summary.get("tokenCounts", {})

    if current_tokens and previous_tokens:
        sections.append("### Token Efficiency by Dataset")
        sections.append("")
        sections.append("| Dataset | Format | Previous | Current | Change |")
        sections.append("|---------|--------|----------|---------|--------|")

        for dataset_name in ["tabular", "nested", "analytics", "github"]:
            for format_name in ["JSON", "TOON"]:
                current_key = f"{format_name}-{dataset_name}"
                previous_key = f"{format_name}-{dataset_name}"

                if current_key in current_tokens and previous_key in previous_tokens:
                    current_val = current_tokens[current_key]
                    previous_val = previous_tokens[previous_key]
                    delta = current_val - previous_val

                    if previous_val > 0:
                        delta_pct = (delta / previous_val) * 100
                        delta_str = format_delta(delta_pct, inverse=True)
                    else:
                        delta_str = "n/a"

                    sections.append(
                        f"| {DATASET_DESCRIPTIONS.get(dataset_name, dataset_name)} | "
                        f"`{format_name}` | {previous_val:,} | {current_val:,} | {delta_str} |"
                    )

        sections.append("")

    # Detailed metrics
    sections.append("<details>")
    sections.append("<summary><strong>View detailed metrics</strong></summary>")
    sections.append("")

    for format_name in ["JSON", "TOON"]:
        if format_name not in current_by_format or format_name not in previous_by_format:
            continue

        current = current_by_format[format_name]
        previous = previous_by_format[format_name]
        metrics = calculate_comparison_metrics(current, previous)

        sections.append(f"#### {format_name} Format")
        sections.append("")
        sections.append("| Metric | Previous | Current | Change |")
        sections.append("|--------|----------|---------|--------|")

        # Accuracy
        sections.append(
            f"| Accuracy | {previous['accuracy'] * 100:.1f}% | "
            f"{current['accuracy'] * 100:.1f}% | "
            f"{format_delta(metrics['accuracy_delta'], is_percentage=False)} |"
        )

        # Tokens
        sections.append(
            f"| Avg Tokens | {previous['total_tokens']:,} | "
            f"{current['total_tokens']:,} | "
            f"{format_delta(metrics['token_delta'], inverse=True)} |"
        )

        # Input tokens
        sections.append(
            f"| Total Input Tokens | {previous['total_input_tokens']:,} | "
            f"{current['total_input_tokens']:,} | "
            f"{format_delta(float(metrics['input_token_delta']), is_percentage=False, inverse=True)} |"
        )

        # Output tokens
        sections.append(
            f"| Total Output Tokens | {previous['total_output_tokens']:,} | "
            f"{current['total_output_tokens']:,} | "
            f"{format_delta(float(metrics['output_token_delta']), is_percentage=False)} |"
        )

        # Latency
        sections.append(
            f"| Avg Latency (ms) | {previous['average_latency']:.1f} | "
            f"{current['average_latency']:.1f} | "
            f"{format_delta(metrics['latency_delta'], inverse=True)} |"
        )

        # Cost
        sections.append(
            f"| Estimated Cost | ${previous['estimated_cost']:.4f} | "
            f"${current['estimated_cost']:.4f} | "
            f"{format_delta(metrics['cost_delta'], inverse=True)} |"
        )

        sections.append("")

    sections.append("</details>")

    return "\n".join(sections)


def compare_and_save(
    current_summary_path: Path,
    previous_summary_path: Path | None = None,
    output_dir: Path | None = None,
) -> Path | None:
    """Compare current results with previous run and save comparison report.

    Args:
        current_summary_path: Path to current run's summary.json
        previous_summary_path: Path to previous summary, or None to auto-detect
        output_dir: Output directory for comparison report

    Returns:
        Path to comparison report, or None if no previous results found

    Raises:
        FileNotFoundError: If summary files don't exist
        json.JSONDecodeError: If summary files are invalid
    """
    # Auto-detect previous results if not provided
    if previous_summary_path is None:
        if output_dir is None:
            output_dir = current_summary_path.parent
        previous_summary_path = find_previous_results(output_dir)

    if previous_summary_path is None:
        logger.info("No previous results to compare against")
        return None

    # Load summaries
    current_summary = load_summary(current_summary_path)
    previous_summary = load_summary(previous_summary_path)

    # Extract timestamps from filenames if possible
    current_timestamp = None
    previous_timestamp = None

    if "summary-" in current_summary_path.name:
        current_timestamp = current_summary_path.stem.replace("summary-", "")
    if "summary-" in previous_summary_path.name:
        previous_timestamp = previous_summary_path.stem.replace("summary-", "")

    # Generate comparison report
    report = generate_comparison_report(current_summary, previous_summary, current_timestamp, previous_timestamp)

    # Save comparison report
    if output_dir is None:
        output_dir = current_summary_path.parent

    # Generate timestamp for comparison report
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    comparison_path = output_dir / f"comparison-{timestamp}.md"

    comparison_path.write_text(report, encoding="utf-8")
    logger.info(f"Saved comparison report to {comparison_path}")

    return comparison_path


__all__ = [
    "find_previous_results",
    "load_summary",
    "calculate_comparison_metrics",
    "format_delta",
    "generate_comparison_report",
    "compare_and_save",
    "ComparisonMetrics",
]
