"""Answer validation using LLM-as-judge pattern.

This module validates LLM answers against expected ground truth using semantic
comparison via OpenAI's API, with fallback to string matching on errors.
"""

import logging
import os


logger = logging.getLogger(__name__)

# Try to import OpenAI client
try:
    import openai
except ImportError:
    logger.warning(
        "OpenAI library not available. Install with: pip install openai. "
        "Validation will fall back to string comparison only."
    )
    openai = None  # type: ignore[assignment]


def validate_answer(
    actual: str,
    expected: str,
    question: str,
    api_key: str | None = None,
    use_fallback: bool = False,
    model: str | None = None,
) -> bool:
    """Validate if actual answer matches expected answer semantically.

    Uses LLM-as-judge approach with configurable OpenAI model for semantic
    comparison. Falls back to simple string comparison if API call fails.

    Args:
        actual: The answer provided by the LLM being evaluated
        expected: The ground truth answer
        question: The question that was asked (provides context for validation)
        api_key: Optional OpenAI API key. Defaults to OPENAI_API_KEY_VALIDATION env var,
                falling back to OPENAI_API_KEY_JSON if not set. Using a separate validation
                key avoids quota coupling with evaluation calls.
        use_fallback: If True, bypass LLM validation and use fallback directly.
                     Useful for testing. Default is False.
        model: Optional validation model. Defaults to VALIDATION_MODEL env var
               or "gpt-4o-mini" if not set.

    Returns:
        True if the actual answer is semantically correct, False otherwise

    Examples:
        >>> validate_answer("50000", "$50,000", "What is the salary?")
        True
        >>> validate_answer("Engineering", "engineering", "What department?")
        True
        >>> validate_answer("42", "100", "How many employees?")
        False
        >>> validate_answer("50000", "$50,000", "What is the salary?", use_fallback=True)
        True
    """
    # If use_fallback is True, skip LLM validation
    if use_fallback:
        logger.debug("use_fallback=True, using fallback validation directly")
        return _fallback_validation(actual, expected)

    # Determine API key - prefer OPENAI_API_KEY_VALIDATION for separate quota tracking
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY_VALIDATION") or os.getenv("OPENAI_API_KEY_JSON")

    # Determine validation model
    if model is None:
        model = os.getenv("VALIDATION_MODEL", "gpt-4o-mini")

    # If no API key or no OpenAI library, fall back to string comparison
    if not api_key or openai is None:
        logger.debug("No API key available or OpenAI not installed, using string comparison fallback")
        return _fallback_validation(actual, expected)

    # Try LLM-as-judge validation
    try:
        return _llm_judge_validation(actual, expected, question, api_key, model)
    except Exception as e:
        logger.warning(f"LLM validation failed for question '{question}': {e}. Falling back to string comparison.")
        return _fallback_validation(actual, expected)


def _llm_judge_validation(actual: str, expected: str, question: str, api_key: str, model: str = "gpt-4o-mini") -> bool:
    """Perform LLM-as-judge validation using OpenAI API.

    Args:
        actual: The actual answer to validate
        expected: The expected ground truth answer
        question: The question for context
        api_key: OpenAI API key
        model: OpenAI model to use for validation (default: gpt-4o-mini)

    Returns:
        True if LLM judges the answer as correct, False otherwise

    Raises:
        Exception: If API call fails (caught by caller)
    """
    if openai is None:
        raise RuntimeError("OpenAI library not available")

    client = openai.OpenAI(api_key=api_key)

    # Construct validation prompt
    prompt = f"""You are validating answers to questions about structured data.

Question: {question}
Expected answer: {expected}
Actual answer: {actual}

Is the actual answer correct? Consider:
- Exact matches are correct
- Semantically equivalent answers are correct (e.g., "50000" vs "$50,000" vs "50000 dollars")
- Minor formatting differences are acceptable (e.g., "2025-01-01" vs "Jan 1, 2025")
- Case-insensitive comparison for text (e.g., "Engineering" vs "engineering")
- Numerical precision differences within reason are acceptable

Respond with only "YES" or "NO"."""

    # Make API call with retries
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=10,  # Only need YES/NO
            )

            # Extract and parse response
            answer = (response.choices[0].message.content or "").strip().upper()

            # Check if response contains YES
            if "YES" in answer:
                logger.debug(f"LLM validation: PASS for question '{question}'")
                return True
            elif "NO" in answer:
                logger.debug(f"LLM validation: FAIL for question '{question}'")
                return False
            else:
                logger.warning(f"Unexpected LLM response '{answer}' for question '{question}', treating as incorrect")
                return False

        except openai.RateLimitError:
            if attempt < max_retries - 1:
                logger.warning(f"Rate limit hit, retrying... (attempt {attempt + 1})")
                import time

                time.sleep(2**attempt)  # Exponential backoff
            else:
                raise
        except (openai.APIError, openai.APIConnectionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"API error, retrying... (attempt {attempt + 1}): {e}")
                import time

                time.sleep(1)
            else:
                raise

    # Should not reach here, but if we do, fall back
    raise RuntimeError("Failed to get valid response after retries")


def _fallback_validation(actual: str, expected: str) -> bool:
    """String comparison fallback with numeric normalization support.

    Handles numeric/currency formatting variations (e.g., "50000" vs "$50,000")
    by normalizing and comparing numerically. Falls back to case-insensitive
    string comparison for non-numeric values.

    Args:
        actual: The actual answer
        expected: The expected answer

    Returns:
        True if values match (numerically or as strings), False otherwise
    """
    # Try numeric comparison first
    actual_num = _parse_numeric(actual)
    expected_num = _parse_numeric(expected)

    if actual_num is not None and expected_num is not None:
        # Both are numeric - compare with small tolerance for floating point
        tolerance = 1e-6
        match = abs(actual_num - expected_num) < tolerance

        if match:
            logger.debug(f"Fallback validation: PASS (numeric: {actual_num} ≈ {expected_num})")
        else:
            logger.debug(f"Fallback validation: FAIL (numeric: {actual_num} != {expected_num})")
        return match

    # Fall back to case-insensitive string comparison
    actual_normalized = actual.strip().lower()
    expected_normalized = expected.strip().lower()

    match = actual_normalized == expected_normalized

    if match:
        logger.debug(f"Fallback validation: PASS (string: '{actual}' == '{expected}')")
    else:
        logger.debug(f"Fallback validation: FAIL (string: '{actual}' != '{expected}')")

    return match


def _parse_numeric(value: str) -> float | None:
    """Parse a string as a numeric value, handling currency formatting.

    Normalizes by removing:
    - Currency symbols ($, €, £, ¥, etc.)
    - Commas (thousands separators)
    - Extra whitespace

    Args:
        value: String to parse

    Returns:
        Parsed float value, or None if not a valid number
    """
    # Normalize: strip whitespace
    normalized = value.strip()

    # Remove common currency symbols
    currency_symbols = ["$", "€", "£", "¥", "¢", "₹", "₽", "₩", "₪"]
    for symbol in currency_symbols:
        normalized = normalized.replace(symbol, "")

    # Remove commas (thousands separators)
    normalized = normalized.replace(",", "")

    # Remove any remaining whitespace
    normalized = normalized.replace(" ", "")

    # Try to parse as float
    try:
        return float(normalized)
    except (ValueError, TypeError):
        return None


# Additional helper for batch validation
def validate_answers_batch(results: list[tuple[str, str, str]], api_key: str | None = None) -> list[bool]:
    """Validate multiple answers in batch.

    Args:
        results: List of (actual, expected, question) tuples
        api_key: Optional OpenAI API key

    Returns:
        List of boolean validation results, same order as input
    """
    return [validate_answer(actual, expected, question, api_key) for actual, expected, question in results]
