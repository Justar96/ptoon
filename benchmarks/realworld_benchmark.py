"""Real-world API response validation and token efficiency benchmark.

This module validates TOON format compatibility with diverse real-world API
responses and measures token efficiency across different API patterns including
GitHub API, OpenAPI specs, GraphQL responses, REST pagination, and JSON-LD.

Data Source:
    The benchmark uses statically curated JSON samples from data/realworld/.
    Automatic data collectors are NOT implemented. All samples are manually
    curated offline to ensure reproducibility, no external dependencies, and
    consistent test data for regression testing. See data/realworld/README.md
    for details on adding new samples.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import ptoon
from ptoon.utils import count_tokens


# Directory for real-world API response samples
DATA_DIR = Path(__file__).resolve().parent / "data" / "realworld"

# API pattern categories with glob patterns
API_PATTERNS: list[tuple[str, str]] = [
    ("GitHub API", "github_*.json"),
    ("OpenAPI Specs", "openapi_*.json"),
    ("GraphQL", "graphql_*.json"),
    ("REST Pagination", "rest_pagination_*.json"),
    ("JSON-LD", "jsonld_*.json"),
    ("Recipes", "recipes_*.json"),
    ("Time-Series Data", "nasdaq_*.json"),
    ("Time-Series Data", "timeseries_*.json"),
    ("Scientific Articles", "articles_*.json"),
]

# Large file handling
LARGE_FILE_THRESHOLD_MB = 10  # Files larger than this will be sampled
SAMPLE_SIZE = 1000  # Number of records to sample from large arrays


# ============================================================================
# Data Loading Functions
# ============================================================================


def load_realworld_samples() -> list[tuple[str, str, dict[str, Any]]]:
    """Load real-world API response samples from data directory.

    Large files (>10MB) are automatically sampled to maintain reasonable runtime.

    Returns:
        List of (pattern_type, filename, data) tuples sorted by pattern then
        filename. Returns empty list with warning if directory doesn't exist.
    """
    if not DATA_DIR.exists():
        print(f"Warning: Real-world data directory not found: {DATA_DIR}")
        print("Create the directory and add sample JSON files to run this benchmark.")
        return []

    samples: list[tuple[str, str, dict[str, Any]]] = []

    for json_file in DATA_DIR.glob("*.json"):
        try:
            # Check file size before loading
            file_size_mb = json_file.stat().st_size / (1024 * 1024)

            if file_size_mb > LARGE_FILE_THRESHOLD_MB:
                print(f"  Note: {json_file.name} is {file_size_mb:.1f}MB, sampling first {SAMPLE_SIZE} records...")
                data, _ = _load_and_sample(json_file)
            else:
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)

            pattern_type = _get_pattern_type(json_file.name)
            samples.append((pattern_type, json_file.name, data))

        except Exception as e:
            print(f"Warning: Failed to load {json_file.name}: {e}")
            continue

    # Sort by pattern type then filename for consistent ordering
    samples.sort(key=lambda x: (x[0], x[1]))

    return samples


def _load_and_sample(json_file: Path) -> tuple[Any, bool]:
    """Load and sample a large JSON file.

    Args:
        json_file: Path to JSON file

    Returns:
        Tuple of (sampled_data, was_sampled)
    """
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # If data is a list and exceeds sample size, take first N records
    if isinstance(data, list) and len(data) > SAMPLE_SIZE:
        sampled_data = data[:SAMPLE_SIZE]
        return sampled_data, True

    # If data is dict with large array, sample the array
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > SAMPLE_SIZE:
                data[key] = value[:SAMPLE_SIZE]
                return data, True

    # Data is small enough or not a sampleable structure
    return data, False


def _get_pattern_type(filename: str) -> str:
    """Determine API pattern type from filename.

    Args:
        filename: Name of the JSON file

    Returns:
        Pattern type string, or "Other" if no match
    """
    for pattern_name, pattern_glob in API_PATTERNS:
        # Convert glob pattern to simple prefix check
        prefix = pattern_glob.replace("*.json", "")
        if filename.startswith(prefix):
            return pattern_name

    return "Other"


# ============================================================================
# Validation Functions
# ============================================================================


def validate_roundtrip(data: Any, sample_name: str) -> tuple[dict[str, Any], str | None]:
    """Test encode → decode → compare for format compatibility.

    Args:
        data: Original data to validate
        sample_name: Name of the sample for error reporting

    Returns:
        Tuple of (result_dict, toon_str). The result_dict contains keys:
        sample, compatible (bool), error (str | None), original_type, decoded_type.
        The toon_str is the encoded TOON string if successful, None otherwise.
    """
    result: dict[str, Any] = {
        "sample": sample_name,
        "compatible": False,
        "error": None,
        "original_type": type(data).__name__,
        "decoded_type": None,
    }
    toon_str = None

    try:
        # Encode to TOON
        toon_str = ptoon.encode(data)

        # Decode back
        decoded = ptoon.decode(toon_str)
        result["decoded_type"] = type(decoded).__name__

        # Deep equality check
        if data == decoded:
            result["compatible"] = True
        else:
            result["error"] = "Roundtrip data mismatch (encoded ≠ decoded)"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        toon_str = None

    return result, toon_str


def measure_token_efficiency(data: Any, sample_name: str, toon_str: str | None = None) -> dict[str, Any]:
    """Measure token efficiency comparing JSON vs TOON.

    Args:
        data: Data to measure
        sample_name: Name of the sample for error reporting
        toon_str: Optional pre-encoded TOON string to avoid re-encoding

    Returns:
        Dict with keys: sample, json_tokens, toon_tokens, savings,
        savings_percent, json_chars, toon_chars
    """
    result: dict[str, Any] = {
        "sample": sample_name,
        "json_tokens": 0,
        "toon_tokens": 0,
        "savings": 0,
        "savings_percent": 0.0,
        "json_chars": 0,
        "toon_chars": 0,
    }

    try:
        # Encode as JSON with indent=2 for readability
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        result["json_chars"] = len(json_str)

        # Encode as TOON (or use provided string)
        if toon_str is None:
            toon_str = ptoon.encode(data)
        result["toon_chars"] = len(toon_str)

        # Count tokens using ptoon.utils
        result["json_tokens"] = count_tokens(json_str)
        result["toon_tokens"] = count_tokens(toon_str)

        # Calculate savings
        result["savings"] = result["json_tokens"] - result["toon_tokens"]
        if result["json_tokens"] > 0:
            result["savings_percent"] = result["savings"] / result["json_tokens"] * 100.0

    except Exception as e:
        print(f"Warning: Failed to measure tokens for {sample_name}: {e}")

    return result


# ============================================================================
# Benchmark Runner
# ============================================================================


def run_realworld_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    """Run real-world API response validation and token efficiency benchmark.

    Args:
        output_dir: Output directory for results (default: benchmarks/results)

    Returns:
        Dict with keys: samples (list), by_pattern (dict), summary (dict), output (str)
    """
    samples = load_realworld_samples()

    if not samples:
        # Return empty results if no samples found
        return {
            "samples": [],
            "by_pattern": {},
            "summary": {
                "total_samples": 0,
                "compatible": 0,
                "incompatible": 0,
                "avg_savings_percent": 0.0,
                "total_json_tokens": 0,
                "total_toon_tokens": 0,
                "total_savings": 0,
            },
            "output": "",
        }

    results: list[dict[str, Any]] = []

    print(f"Testing {len(samples)} real-world API samples...")

    for i, (pattern_type, filename, data) in enumerate(samples, 1):
        print(f"  [{i}/{len(samples)}] {filename}...", end=" ", flush=True)

        # Validate roundtrip compatibility (also returns encoded TOON string)
        validation, toon_str = validate_roundtrip(data, filename)

        # Measure token efficiency (reuse the encoded TOON string)
        efficiency = measure_token_efficiency(data, filename, toon_str)

        # Combine results
        sample_result = {
            "pattern": pattern_type,
            **validation,
            **efficiency,
        }
        results.append(sample_result)

        if validation["compatible"]:
            savings_pct = efficiency["savings_percent"]
            print(f"✓ Compatible, {savings_pct:.1f}% saved")
        else:
            print(f"✗ Incompatible: {validation['error']}")

    # Aggregate results by pattern type
    by_pattern: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        pattern = result["pattern"]
        if pattern not in by_pattern:
            by_pattern[pattern] = []
        by_pattern[pattern].append(result)

    # Calculate summary statistics
    compatible_count = sum(1 for r in results if r["compatible"])
    incompatible_count = len(results) - compatible_count

    total_json_tokens = sum(r["json_tokens"] for r in results)
    total_toon_tokens = sum(r["toon_tokens"] for r in results)
    total_savings = total_json_tokens - total_toon_tokens

    avg_savings_percent = 0.0
    if results:
        avg_savings_percent = sum(r["savings_percent"] for r in results) / len(results)

    summary = {
        "total_samples": len(results),
        "compatible": compatible_count,
        "incompatible": incompatible_count,
        "avg_savings_percent": avg_savings_percent,
        "total_json_tokens": total_json_tokens,
        "total_toon_tokens": total_toon_tokens,
        "total_savings": total_savings,
    }

    # Generate report
    report_md = _generate_realworld_report(results, by_pattern, summary)

    # Write output files
    out_dir = output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "realworld-benchmark.md"
    json_path = out_dir / "realworld-benchmark.json"

    md_path.write_text(report_md, encoding="utf-8")
    json_path.write_text(
        json.dumps({"samples": results, "by_pattern": by_pattern, "summary": summary}, indent=2),
        encoding="utf-8",
    )

    return {
        "samples": results,
        "by_pattern": by_pattern,
        "summary": summary,
        "output": str(md_path),
    }


# ============================================================================
# Report Generation
# ============================================================================


def _generate_realworld_report(
    results: list[dict[str, Any]],
    by_pattern: dict[str, list[dict[str, Any]]],
    summary: dict[str, Any],
) -> str:
    """Generate markdown report for real-world benchmark.

    Args:
        results: List of all sample results
        by_pattern: Results grouped by pattern type
        summary: Summary statistics

    Returns:
        Markdown report string
    """
    lines = ["# Real-World API Response Benchmark", ""]

    # Header with summary
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        f"Samples: {summary['compatible']}/{summary['total_samples']} compatible | "
        f"Avg token savings: {summary['avg_savings_percent']:.1f}%"
    )
    lines.append("")

    # Overview table
    lines.append("## Overview")
    lines.append("")
    lines.append("| Sample | Pattern | Compatible | JSON Tokens | TOON Tokens | Savings % | Status |")
    lines.append("|---|---|---|---:|---:|---:|---|")

    for r in results:
        sample = r["sample"]
        pattern = r["pattern"]
        compatible = "✓" if r["compatible"] else "✗"
        json_tokens = _format_number(r["json_tokens"])
        toon_tokens = _format_number(r["toon_tokens"])
        savings_pct = f"{r['savings_percent']:.1f}%"
        status = "✓ Pass" if r["compatible"] else "✗ Fail"

        lines.append(
            f"| {sample} | {pattern} | {compatible} | {json_tokens} | {toon_tokens} | {savings_pct} | {status} |"
        )

    lines.append("")

    # Analysis by pattern
    lines.append("## Analysis by Pattern")
    lines.append("")

    for pattern_name, pattern_results in sorted(by_pattern.items()):
        lines.append(f"### {pattern_name}")
        lines.append("")

        # Calculate pattern statistics
        pattern_compatible = sum(1 for r in pattern_results if r["compatible"])
        pattern_total = len(pattern_results)
        pattern_compat_rate = pattern_compatible / pattern_total * 100.0 if pattern_total > 0 else 0.0
        pattern_avg_savings = (
            sum(r["savings_percent"] for r in pattern_results) / pattern_total if pattern_total > 0 else 0.0
        )

        # Find best performer
        best_result = max(pattern_results, key=lambda r: r["savings_percent"])

        lines.append(f"- Samples: {pattern_total}")
        lines.append(f"- Compatibility: {pattern_compatible}/{pattern_total} ({pattern_compat_rate:.1f}%)")
        lines.append(f"- Avg token savings: {pattern_avg_savings:.1f}%")
        lines.append(f"- Best performer: {best_result['sample']} ({best_result['savings_percent']:.1f}% savings)")
        lines.append("")

        lines.append("**Individual Results:**")
        for r in pattern_results:
            compat_icon = "✓" if r["compatible"] else "✗"
            status_text = "Compatible" if r["compatible"] else f"Incompatible ({r['error']})"
            json_tok = _format_number(r["json_tokens"])
            toon_tok = _format_number(r["toon_tokens"])
            savings = r["savings_percent"]

            lines.append(
                f"- {r['sample']}: {compat_icon} {status_text}, {json_tok} → {toon_tok} tokens ({savings:.1f}% savings)"
            )

        lines.append("")

    # Incompatibilities section
    incompatible_results = [r for r in results if not r["compatible"]]
    if incompatible_results:
        lines.append("## Incompatibilities")
        lines.append("")
        for r in incompatible_results:
            lines.append(f"- **{r['sample']}**: {r['error']}")
        lines.append("")

    # Token efficiency summary with bar charts
    lines.append("## Token Efficiency Summary")
    lines.append("")

    for pattern_name, pattern_results in sorted(by_pattern.items()):
        pattern_avg_savings = (
            sum(r["savings_percent"] for r in pattern_results) / len(pattern_results) if pattern_results else 0.0
        )
        bar = _generate_bar_chart(pattern_avg_savings)
        lines.append(f"- {pattern_name}: {bar}")

    lines.append("")

    # Sample details with collapsible sections
    lines.append("## Sample Details")
    lines.append("")

    for r in results:
        sample_name = r["sample"]
        savings_pct = r["savings_percent"]

        lines.append(f"<details><summary>{sample_name} — {savings_pct:.1f}% saved</summary>")
        lines.append("")

        # Try to load original JSON for display
        json_file = DATA_DIR / sample_name
        if json_file.exists():
            try:
                with json_file.open("r", encoding="utf-8") as f:
                    original_data = json.load(f)

                json_str = json.dumps(original_data, ensure_ascii=False, indent=2)
                toon_str = ptoon.encode(original_data)

                json_truncated = _truncate_for_display(json_str, 500)
                toon_truncated = _truncate_for_display(toon_str, 500)

                lines.append("**JSON (truncated):**")
                lines.append("```json")
                lines.append(json_truncated)
                lines.append("```")
                lines.append("")

                lines.append("**TOON (truncated):**")
                lines.append("```")
                lines.append(toon_truncated)
                lines.append("```")
                lines.append("")

            except Exception:
                lines.append("_Could not load sample for display_")
                lines.append("")

        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Utility Functions
# ============================================================================


def _truncate_for_display(text: str, max_chars: int = 500) -> str:
    """Truncate text for display in report.

    Args:
        text: Text to truncate
        max_chars: Maximum characters to show

    Returns:
        Truncated text with "..." suffix if needed
    """
    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n..."


def _format_number(n: int) -> str:
    """Format integer with thousand separators.

    Args:
        n: Number to format

    Returns:
        Formatted string (e.g., "1,234")
    """
    return f"{n:,}"


def _generate_bar_chart(percentage: float, max_width: int = 25) -> str:
    """Generate visual bar chart for token savings.

    Args:
        percentage: Savings percentage (e.g., 63.9 means 63.9% savings)
        max_width: Maximum width of bar in characters

    Returns:
        Bar chart string showing savings visually and numerically
    """
    pct = max(0.0, min(100.0, percentage))
    # Filled portion represents TOON's size (100 - savings)
    # So if savings is 63.9%, TOON is 36.1% of JSON's size
    filled = int(round((100 - pct) / 100 * max_width))
    empty = max_width - filled
    # Label shows the savings percentage to match table headers
    return f"{'█' * filled}{'░' * empty} {pct:.1f}% saved"


if __name__ == "__main__":
    res = run_realworld_benchmark()
    print(json.dumps(res["summary"], indent=2))
