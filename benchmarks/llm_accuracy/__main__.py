"""Command-line interface for the LLM accuracy benchmark."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from benchmarks.datasets import (
    generate_analytics_data,
    generate_nested_dataset,
    generate_tabular_dataset,
    load_github_dataset,
)
from benchmarks.llm_accuracy.realworld_datasets import (
    generate_code_generation_dataset,
    generate_customer_support_dataset,
    generate_data_analysis_dataset,
    generate_multidoc_reasoning_dataset,
    generate_rag_documentation_dataset,
)

from .compare import compare_and_save
from .evaluate import (
    DEFAULT_CONCURRENCY,
    DRY_RUN_MAX_QUESTIONS,
    MODEL,
    format_datasets,
    is_dry_run,
    run_evaluation,
)
from .questions import generate_questions
from .realworld_questions import generate_realworld_questions
from .report import generate_report


logger = logging.getLogger(__name__)


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
        logger.debug("Loaded .env file using python-dotenv")
        return
    except ImportError:
        pass

    # Fallback: simple custom .env loader
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        logger.debug("No .env file found at %s", env_file)
        return

    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]

                # Only set if not already in environment
                if key and key not in os.environ:
                    os.environ[key] = value

        logger.debug("Loaded .env file from %s", env_file)
    except Exception as e:
        logger.warning("Failed to load .env file: %s", e)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def print_banner(model: str = MODEL) -> None:
    print("LLM Accuracy Benchmark for TOON")
    print(f"Comparing JSON vs TOON format accuracy with {model}")
    print()


def check_dependencies() -> None:
    """Check that required dependencies are installed."""
    try:
        import tiktoken  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "tiktoken is required for report generation.\n"
            "Install it with: pip install tiktoken\n"
            "Or install all benchmark dependencies: pip install -e .[benchmark]"
        ) from exc


def validate_environment(provider_type: str = "openai") -> dict[str, str]:
    """Validate environment variables for the selected provider.

    Args:
        provider_type: 'openai' or 'vertex'

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If required environment variables are missing
    """
    if provider_type == "openai":
        json_key = os.getenv("OPENAI_API_KEY_JSON")
        toon_key = os.getenv("OPENAI_API_KEY_TOON")

        if not json_key or not toon_key:
            raise ValueError(
                "Both OPENAI_API_KEY_JSON and OPENAI_API_KEY_TOON are required. "
                "Dual API keys enable separate tracking in OpenAI console for JSON vs TOON evaluations."
            )

        config = {
            "OPENAI_API_KEY_JSON": json_key,
            "OPENAI_API_KEY_TOON": toon_key,
            "CONCURRENCY": os.getenv("CONCURRENCY", str(DEFAULT_CONCURRENCY)),
            "provider": "openai",
        }

    elif provider_type == "vertex":
        project_id = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION", "us-central1")

        if not project_id:
            raise ValueError(
                "VERTEX_PROJECT_ID is required for Vertex AI provider. Set it to your Google Cloud project ID."
            )

        config = {
            "VERTEX_PROJECT_ID": project_id,
            "VERTEX_LOCATION": location,
            "CONCURRENCY": os.getenv("CONCURRENCY", str(DEFAULT_CONCURRENCY)),
            "provider": "vertex",
        }

    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Must be 'openai' or 'vertex'.")

    return config


def print_section(title: str) -> None:
    print(f"=== {title} ===")


def _default_output_dir() -> Path:
    return Path(__file__).parent.parent / "results" / "llm_accuracy"


def _load_existing_results(
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_path = output_dir / "raw-results.json"
    summary_path = output_dir / "summary.json"

    if not raw_path.exists() or not summary_path.exists():
        raise FileNotFoundError(
            f"Existing results not found in {output_dir}. Expected raw-results.json and summary.json."
        )

    raw_results = json.loads(raw_path.read_text(encoding="utf-8"))
    if not isinstance(raw_results, list):
        raise ValueError(f"raw-results.json in {output_dir} is not a list")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise ValueError(f"summary.json in {output_dir} is not an object")

    format_results = summary.get("formatResults")
    if not isinstance(format_results, list):
        raise ValueError("summary.json does not contain formatResults list")

    return raw_results, format_results


def _resolve_questions_from_results(results: list[dict[str, Any]], use_realworld: bool = False) -> list[dict[str, Any]]:
    questions = generate_realworld_questions() if use_realworld else generate_questions()
    question_map = {q["id"]: q for q in questions}
    seen_ids = {entry.get("question_id") for entry in results if "question_id" in entry}
    ordered: list[dict[str, Any]] = [question_map[q["id"]] for q in questions if q["id"] in seen_ids]
    return ordered


def _build_datasets(use_realworld: bool = False) -> dict[str, dict[str, Any]]:
    if use_realworld:
        return {
            "rag-documentation": generate_rag_documentation_dataset(),
            "code-generation": generate_code_generation_dataset(),
            "customer-support": generate_customer_support_dataset(),
            "data-analysis": generate_data_analysis_dataset(),
            "multi-document": generate_multidoc_reasoning_dataset(),
        }
    else:
        return {
            "tabular": generate_tabular_dataset(),
            "nested": generate_nested_dataset(),
            "analytics": generate_analytics_data(180),
            "github": load_github_dataset(),
        }


def _display_summary(summary: dict[str, Any]) -> None:
    format_results = summary.get("format_results")
    if not isinstance(format_results, list) or not format_results:
        print("No summary available.")
        return

    total_questions = format_results[0].get("total_count", 0)
    print(f"- Total questions evaluated: {total_questions}")

    json_result = None
    toon_result = None

    for entry in format_results:
        fmt = entry.get("format", "")
        accuracy = float(entry.get("accuracy", 0.0)) * 100
        correct = entry.get("correct_count", 0)
        total = entry.get("total_count", 0)
        cost = float(entry.get("estimated_cost", 0.0))
        print(f"- {fmt} accuracy: {accuracy:.1f}% ({correct}/{total}) | Estimated cost: ${cost:.4f}")
        if fmt == "JSON":
            json_result = entry
        elif fmt == "TOON":
            toon_result = entry

    if json_result and toon_result:
        json_tokens = float(json_result.get("total_tokens", 0) or 0)
        toon_tokens = float(toon_result.get("total_tokens", 0) or 0)
        if json_tokens > 0:
            savings = (1 - toon_tokens / json_tokens) * 100
            print(f"- Token savings (TOON vs JSON): {savings:.1f}%")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run LLM accuracy benchmark comparing JSON vs TOON formats",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "vertex"],
        default="openai",
        help="LLM provider to use (default: openai)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=f"Limit to {DRY_RUN_MAX_QUESTIONS} questions for cost control (takes precedence over .env DRY_RUN)",
    )
    parser.add_argument(
        "--max-questions",
        type=int,
        default=None,
        help="Limit number of questions (useful for testing)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: benchmarks/results/llm_accuracy)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Parallel evaluation tasks (default: 20, overrides CONCURRENCY env var)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--regenerate-report",
        action="store_true",
        help="Regenerate report from existing results without re-running evaluation",
    )
    parser.add_argument(
        "--realworld",
        action="store_true",
        help="Use real-world scenario questions (RAG, code generation, customer support, etc.)",
    )

    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    # Load .env file before reading environment variables
    load_env_file()

    print_banner()

    # Check required dependencies
    try:
        check_dependencies()
    except RuntimeError as exc:
        logger.error(str(exc))
        return 1

    try:
        env_config = validate_environment(args.provider)
    except ValueError as exc:
        logger.error(str(exc))
        return 1

    output_dir = args.output_dir or _default_output_dir()

    # Determine concurrency setting
    concurrency = args.concurrency if args.concurrency is not None else int(env_config["CONCURRENCY"])
    os.environ["CONCURRENCY"] = str(concurrency)

    # Determine effective dry-run mode
    # CLI --dry-run flag takes precedence over .env DRY_RUN
    effective_dry_run = args.dry_run or is_dry_run()

    logger.info(
        "Configuration: provider=%s, dry_run=%s (cli=%s, env=%s), concurrency=%s, max_questions=%s, output_dir=%s",
        args.provider,
        effective_dry_run,
        args.dry_run,
        is_dry_run(),
        concurrency,
        args.max_questions,
        output_dir,
    )

    if args.regenerate_report:
        try:
            results, _ = _load_existing_results(output_dir)
        except (OSError, ValueError) as exc:
            logger.error("Failed to load existing results: %s", exc)
            return 1

        print_section("Generating Report")
        questions = _resolve_questions_from_results(results, use_realworld=args.realworld)
        datasets = _build_datasets(use_realworld=args.realworld)
        formatted = format_datasets(datasets)

        try:
            summary = generate_report(
                results, questions, formatted, model=MODEL, output_dir=output_dir, provider=args.provider
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to regenerate report: %s", exc)
            return 1

        print(f"Results saved to: {output_dir}")
        print("  - Raw results: raw-results.json")
        print("  - Summary: summary.json")
        print("  - Report: report.md")

        # Generate comparison report if previous results exist
        print_section("Comparison")
        try:
            current_summary_path = Path(summary["summary_path"])
            comparison_path = compare_and_save(current_summary_path, output_dir=output_dir)
            if comparison_path:
                print(f"Comparison report generated: {comparison_path.name}")
            else:
                print("No previous results found for comparison.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to generate comparison report: %s", exc)

        print_section("Summary")
        _display_summary(summary)
        return 0

    print_section("Generating Questions")
    if args.realworld:
        questions = generate_realworld_questions()
        logger.info("Generated %d real-world scenario questions", len(questions))
    else:
        questions = generate_questions()
        logger.info("Generated %d questions across datasets", len(questions))

    # CLI --dry-run flag: slice here to take precedence over .env or evaluate_all_questions() behavior
    # .env DRY_RUN: handled by evaluate_all_questions() for both CLI and library usage
    if args.dry_run:
        logger.warning(
            "DRY RUN MODE (--dry-run flag): Limited to %d questions for cost control",
            DRY_RUN_MAX_QUESTIONS,
        )
        questions = questions[:DRY_RUN_MAX_QUESTIONS]
    elif effective_dry_run:
        # Log that .env DRY_RUN is active; evaluate_all_questions() will apply the limit
        logger.warning(
            "DRY RUN MODE (.env config): Will limit to %d questions during evaluation",
            DRY_RUN_MAX_QUESTIONS,
        )

    # Apply max_questions limit if specified and not already limited by dry-run
    if args.max_questions is not None and len(questions) > args.max_questions:
        questions = questions[: args.max_questions]
        logger.info("Limited questions to %d", len(questions))

    print_section("Running Evaluation")
    start_time = time.time()

    # Build datasets before evaluation
    datasets = _build_datasets(use_realworld=args.realworld)

    try:
        results = run_evaluation(questions, provider_type=args.provider, datasets=datasets)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Evaluation failed: %s", exc)
        return 1

    elapsed = time.time() - start_time
    logger.info("Evaluation completed in %.1fs", elapsed)

    print_section("Generating Report")
    formatted = format_datasets(datasets)

    try:
        summary = generate_report(
            results, questions, formatted, model=MODEL, output_dir=output_dir, provider=args.provider
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to generate report: %s", exc)
        return 1

    print(f"Results saved to: {output_dir}")
    print("  - Raw results: raw-results.json")
    print("  - Summary: summary.json")
    print("  - Report: report.md")

    # Generate comparison report if previous results exist
    print_section("Comparison")
    try:
        current_summary_path = Path(summary["summary_path"])
        comparison_path = compare_and_save(current_summary_path, output_dir=output_dir)
        if comparison_path:
            print(f"Comparison report generated: {comparison_path.name}")
            print("  View the comparison to see improvements/regressions from the previous run.")
        else:
            print("No previous results found for comparison.")
            print("  Run the benchmark again to see improvements over time.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to generate comparison report: %s", exc)
        print("  (Comparison generation failed - see logs)")

    print_section("Summary")
    _display_summary(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
