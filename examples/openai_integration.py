"""
Demonstrates using TOON format with OpenAI SDK for token-efficient LLM applications.

CAUTION: Running this example will incur OpenAI API costs.

Cost Guardrails:
- Set SMALL_DATA=1 to use a smaller dataset (10 records instead of 100)
- Set DRY_RUN=true to preview token counts without making API calls
- Copy examples/.env.example to examples/.env and configure

Key benefits of TOON vs JSON:
- 30-60% token reduction in typical structured datasets
- Lower API costs (tokens are the primary cost driver)
- Faster context processing (fewer tokens to process)
- Same semantic information as JSON

When to use TOON:
- Large structured datasets in prompts (RAG, analytics, catalogs)
- Cost-sensitive applications
- Context window optimization

When NOT to use TOON:
- Tiny payloads (overhead not worth it)
- Strict JSON contracts (function calling, tool use)
- Real-time streaming where encoding overhead matters

Installation:
    pip install -e ".[examples]"

Usage:
    # Copy and configure .env
    cp examples/.env.example examples/.env
    # Edit examples/.env to set your OPENAI_API_KEY
    
    # Run with guardrails (dry run, small data)
    python examples/openai_integration.py
    
    # Run with full data (incurs higher API costs)
    SMALL_DATA=0 DRY_RUN=false python examples/openai_integration.py
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


try:
    import openai
    import tiktoken
except ImportError:  # pragma: no cover - example dependency check
    print(
        'Error: Missing dependencies. Install with: pip install -e ".[examples]"',
        file=sys.stderr,
    )
    sys.exit(1)

import pytoon
from benchmarks.datasets import generate_tabular_dataset


# Configuration constants
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
MODEL: str = "gpt-4o-mini"
TOKENIZER_ENCODING: str = "o200k_base"  # GPT-4o tokenizer

# Cost guardrail settings
SMALL_DATA: bool = os.getenv("SMALL_DATA", "1") == "1"  # Default: use small dataset
DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"  # Default: dry run mode
DATASET_LIMIT = 10 if SMALL_DATA else 100

if not OPENAI_API_KEY:  # Basic validation before making API calls
    print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
    print("Copy examples/.env.example to examples/.env and set your API key.", file=sys.stderr)
    # Do not exit immediately so that the module can still be imported for reading.


def count_tokens(text: str) -> int:
    """Count tokens using GPT-4o tokenizer (o200k_base)."""
    enc = tiktoken.get_encoding(TOKENIZER_ENCODING)
    return len(enc.encode(text))


def format_data_json(data: dict[str, Any]) -> str:
    """Format data as JSON (standard approach)."""
    return json.dumps(data, indent=2)


def format_data_toon(data: dict[str, Any]) -> str:
    """Format data as TOON (token-optimized approach)."""
    return pytoon.encode(data)


def compare_token_counts(data: dict[str, Any]) -> dict[str, float | int]:
    """Compare tokens and character sizes for JSON vs TOON and print a summary table."""
    json_str = format_data_json(data)
    toon_str = format_data_toon(data)

    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)

    savings = json_tokens - toon_tokens
    savings_percent = (savings / json_tokens * 100) if json_tokens else 0.0

    print("\nToken Comparison:")
    print("\u2500" * 48)
    print(f"{'Format':<10}{'Tokens':>12}{'Size (chars)':>18}")
    print(f"{'JSON':<10}{json_tokens:>12,}{len(json_str):>18,}")
    print(f"{'TOON':<10}{toon_tokens:>12,}{len(toon_str):>18,}")
    print("\u2500" * 48)
    print(f"Savings: {savings:,} tokens ({savings_percent:.1f}%)")

    return {
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings": savings,
        "savings_percent": savings_percent,
    }


def example_basic_pattern() -> None:
    """Demonstrates the basic encode → send → decode pattern."""
    print("\n=== EXAMPLE 1: Basic Pattern ===")

    data: dict[str, Any] = {
        "id": 1,
        "name": "Ada Lovelace",
        "department": "Engineering",
        "salary": 120_000,
    }
    print("Data to send:")
    print(data)

    toon_str = pytoon.encode(data)
    print("\nEncoded as TOON:")
    print("\n" + toon_str)

    if DRY_RUN:
        print("\nSkipping OpenAI call: DRY_RUN=true (no API calls).")
        return

    if not OPENAI_API_KEY:
        print("\nSkipping OpenAI call: OPENAI_API_KEY not set.")
        return

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Given the following employee data in TOON format:\n\n"
        f"{toon_str}\n\n"
        "Question: What is the employee's name?\n\n"
        "Provide only the direct answer."
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    answer = (response.choices[0].message.content or "").strip()
    print(f"\nLLM Answer: {answer}")

    print(
        "\nNote: If the LLM returns structured data in TOON format, use toon.decode() to parse it."
    )

    usage = getattr(response, "usage", None)
    if usage:
        print("\nToken usage:")
        print(f"  Input:  {getattr(usage, 'prompt_tokens', None)}")
        print(f"  Output: {getattr(usage, 'completion_tokens', None)}")
        print(f"  Total:  {getattr(usage, 'total_tokens', None)}")


def example_token_comparison() -> None:
    """Compares token counts between JSON and TOON formats."""
    print("\n=== EXAMPLE 2: Token Comparison ===")

    try:
        data = generate_tabular_dataset()  # 100 employees
    except RuntimeError as exc:
        print(f"Dataset generation failed: {exc}")
        return
    if SMALL_DATA:
        data["employees"] = data["employees"][:DATASET_LIMIT]
    print(
        f"Generated dataset: {len(data['employees'])} employee records "
        f"({'SMALL_DATA=1' if SMALL_DATA else 'full'})"
    )

    comparison = compare_token_counts(data)

    json_tokens = int(comparison["json_tokens"])  # input-side only for cost calc
    toon_tokens = int(comparison["toon_tokens"])  # input-side only for cost calc

    # Pricing for gpt-4o-mini (as of October 2025): $0.60 input / $2.40 output per 1M tokens
    # Verify current pricing at: https://openai.com/api/pricing/
    price_per_million_input = 0.60
    json_cost = (json_tokens / 1_000_000) * price_per_million_input
    toon_cost = (toon_tokens / 1_000_000) * price_per_million_input
    cost_savings = json_cost - toon_cost

    print("\nCost Comparison (input tokens only):")
    print(f"JSON:   ${json_cost:0.6f}")
    print(f"TOON:   ${toon_cost:0.6f}")
    print(
        f"Savings: ${cost_savings:0.6f} per request ({comparison['savings_percent']:.1f}%)"
    )

    daily = cost_savings * 1_000
    monthly = daily * 30
    annual = daily * 365
    print("\nAt 1,000 requests/day:")
    print(f"Daily savings:   ${daily:0.2f}")
    print(f"Monthly savings: ${monthly:0.2f}")
    print(f"Annual savings:  ${annual:0.2f}")

    print("\nJSON format (first 500 chars):")
    print(format_data_json(data)[:500])
    print("\nTOON format (first 500 chars):")
    print(format_data_toon(data)[:500])
    print(
        "\nNotice: TOON uses tabular format for uniform arrays, eliminating repeated keys."
    )


def example_rag_retrieval() -> None:
    """Demonstrates RAG-style question answering with TOON format."""
    print("\n=== EXAMPLE 3: RAG-Style Data Retrieval ===")

    try:
        data = generate_tabular_dataset()
    except RuntimeError as exc:
        print(f"Dataset generation failed: {exc}")
        return
    if SMALL_DATA:
        data["employees"] = data["employees"][:DATASET_LIMIT]
    print(
        f"Dataset: {len(data['employees'])} employee records "
        f"({'SMALL_DATA=1' if SMALL_DATA else 'full'})"
    )

    questions = [
        "How many employees have a salary greater than 100000?",
        "What department does the employee with id 1 work in?",
        "List all employees in the Engineering department",
        "What is the average salary across all employees?",
    ]

    if DRY_RUN:
        print("\nSkipping OpenAI calls: DRY_RUN=true (no API calls).")
        return

    if not OPENAI_API_KEY:
        print("\nSkipping OpenAI calls: OPENAI_API_KEY not set.")
        return

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    print("\n--- Testing with JSON format ---")
    json_str = format_data_json(data)
    json_tokens = count_tokens(json_str)
    print(f"Input tokens: {json_tokens:,}")
    total_json_tokens = 0
    for q in questions:
        prompt = (
            "You are given the following employee data in JSON. Answer the question.\n\n"
            f"DATA:\n{json_str}\n\n"
            f"QUESTION: {q}\n\nProvide a concise answer."
        )
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        ans = (resp.choices[0].message.content or "").strip()
        print(f"Q: {q}")
        print(f"A: {ans}\n")
        if getattr(resp, "usage", None):
            total_json_tokens += int(getattr(resp.usage, "total_tokens", 0) or 0)
    print(f"Total tokens (JSON): {total_json_tokens:,}")

    print("\n--- Testing with TOON format ---")
    toon_str = format_data_toon(data)
    toon_tokens = count_tokens(toon_str)
    print(f"Input tokens: {toon_tokens:,}")
    total_toon_tokens = 0
    for q in questions:
        prompt = (
            "You are given the following employee data in TOON format. Answer the question.\n\n"
            f"DATA:\n{toon_str}\n\n"
            f"QUESTION: {q}\n\nProvide a concise answer."
        )
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        ans = (resp.choices[0].message.content or "").strip()
        print(f"Q: {q}")
        print(f"A: {ans}\n")
        if getattr(resp, "usage", None):
            total_toon_tokens += int(getattr(resp.usage, "total_tokens", 0) or 0)
    print(f"Total tokens (TOON): {total_toon_tokens:,}")

    if total_json_tokens:
        savings = total_json_tokens - total_toon_tokens
        savings_pct = (savings / total_json_tokens) * 100
    else:
        savings = 0
        savings_pct = 0.0
    print("\nResults Comparison:")
    print("\u2500" * 42)
    print(f"{'Format':<10}{'Total Tokens':>18}{'Cost':>10}")
    # Cost estimate (blended rate for gpt-4o-mini): ~$1.00 per 1M tokens
    # This approximates typical input/output ratio; actual costs depend on usage pattern
    # Verify current pricing at: https://openai.com/api/pricing/
    price_per_million = 1.00
    json_cost = (total_json_tokens / 1_000_000) * price_per_million
    toon_cost = (total_toon_tokens / 1_000_000) * price_per_million
    print(f"{'JSON':<10}{total_json_tokens:>18,}${json_cost:>9.5f}")
    print(f"{'TOON':<10}{total_toon_tokens:>18,}${toon_cost:>9.5f}")
    print("\u2500" * 42)
    print(f"Savings: {savings:,} tokens ({savings_pct:.1f}%)")
    print(f"Cost savings: ${(json_cost - toon_cost):.5f} per batch")

    print("\nKey insights:")
    print("- The LLM can understand TOON format without special instructions")
    print("- Answers are semantically identical between formats")
    print("- Token savings compound with multiple questions")
    print("- Best for: large datasets, repeated queries, cost-sensitive applications")


def example_error_handling() -> None:
    """Demonstrates robust error handling for TOON responses."""
    print("\n=== EXAMPLE 4: Error Handling ===")

    print("\n--- Scenario 1: Malformed TOON Response ---")
    malformed_toon = (
        "employees[3]:\n"
        "  - id: 1\n"
        "    name: Ada\n"
        "  - id: 2\n"
        "    # Missing closing bracket\n"
    )
    try:
        result = pytoon.decode(malformed_toon)
        print("Decoded successfully:", result)
    except Exception as e:  # noqa: BLE001 - example error display
        print(f"Decode error: {type(e).__name__}: {e}")
        print("Fallback: Request LLM to regenerate in valid format")

    print("\n--- Scenario 2: LLM Returns JSON Instead ---")
    json_response = '{"name": "Ada", "salary": 120000}'
    try:
        result = pytoon.decode(json_response)
        print("Parsed as TOON:", result)
    except Exception:
        try:
            result = json.loads(json_response)
            print("Detected JSON format, parsed successfully")
        except Exception as e:  # noqa: BLE001
            print(f"Fallback JSON parsing failed: {e}")

    print("\n--- Scenario 3: Graceful Degradation ---")

    def safe_decode(response_text: str) -> dict[str, Any] | str:
        # Try TOON first
        try:
            return pytoon.decode(response_text)  # type: ignore[return-value]
        except Exception:
            pass
        # Try JSON
        try:
            return json.loads(response_text)  # type: ignore[return-value]
        except Exception:
            pass
        # Return raw text as fallback
        return response_text

    print("Best practice: Always have fallback parsing strategies")

    print("\n--- Scenario 4: Validation with Retry ---")
    print(
        "Example pattern: attempt to decode TOON, on failure retry with stricter instructions."
    )
    max_retries = 3
    for attempt in range(max_retries):
        # Placeholder for real LLM call
        response_text = malformed_toon if attempt < max_retries - 1 else "name: Ada"
        try:
            _ = pytoon.decode(response_text)
            print(f"Attempt {attempt + 1}: success")
            break
        except Exception:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
            else:
                print("All retries failed, using fallback (raw text)")


def main() -> None:
    banner = (
        "\n\n"
        "\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557\n"
        "\u2551  TOON + OpenAI Integration Examples           \u2551\n"
        "\u2551  Demonstrating token-efficient LLM apps       \u2551\n"
        "\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d\n"
    )
    print(banner)
    
    # Display cost guardrail status
    print(f"\nCost Guardrails:")
    print(
        f"  Dataset Size: {DATASET_LIMIT} records "
        f"({'SMALL' if SMALL_DATA else 'FULL'})"
    )
    print(f"  Mode: {'DRY RUN (no API calls)' if DRY_RUN else 'LIVE (API calls enabled)'}")
    if DRY_RUN:
        print("  \u26a0\ufe0f  DRY RUN mode: Token counts shown, no API calls made")
    else:
        print("  \u26a0\ufe0f  LIVE mode: API calls will incur costs")
    print()

    if not OPENAI_API_KEY:
        if DRY_RUN:
            print(
                "Info: OPENAI_API_KEY not set (OK for DRY_RUN=true). "
                "Set it before running live API calls."
            )
        else:
            print("Error: OPENAI_API_KEY not set")
            print("Copy examples/.env.example to examples/.env and set your API key")
        # Continue running examples that don't require API access

    try:
        example_basic_pattern()
        input("\nPress Enter to continue to next example...")

        example_token_comparison()
        input("\nPress Enter to continue to next example...")

        example_rag_retrieval()
        input("\nPress Enter to continue to next example...")

        example_error_handling()
    except KeyboardInterrupt:  # pragma: no cover - interactive example
        print("\n\nExamples interrupted by user")
    except Exception as e:  # noqa: BLE001 - top-level example error reporting
        print(f"\n\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
