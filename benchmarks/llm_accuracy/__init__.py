"""LLM accuracy benchmark module for TOON format evaluation.

This module provides tools for generating benchmark questions and validating
LLM answers to measure accuracy when using TOON vs JSON formats.

The benchmark workflow:
1. Generate questions from datasets using `generate_questions()`
2. Present data in both JSON and TOON formats to an LLM
3. Validate answers using `validate_answer()` with LLM-as-judge pattern
4. Compare accuracy metrics between formats

Example:
    >>> from benchmarks.llm_accuracy import generate_questions, validate_answer
    >>> questions = generate_questions()
    >>> # ... present questions to LLM ...
    >>> is_correct = validate_answer(
    ...     actual="95000",
    ...     expected="95000",
    ...     question="What is Alice's salary?"
    ... )

Key components:
- Question generation: ~160 questions across 4 datasets
- Question types: field-retrieval, aggregation, filtering
- Validation: LLM-as-judge with fallback to string matching
- Type definitions: Question, EvaluationResult, and related types
"""

from .evaluate import (
    evaluate_all_questions,
    evaluate_single_question,
    format_datasets,
    run_evaluation,
)
from .questions import generate_questions
from .report import (
    FormatResult,
    calculate_format_results,
    calculate_token_counts,
    generate_report,
    save_results,
)
from .types import (
    Dataset,
    DatasetName,
    EvaluationResult,
    Question,
    QuestionType,
)
from .validation import validate_answer, validate_answers_batch


__all__ = [
    # Question generation
    "generate_questions",
    # Evaluation
    "format_datasets",
    "evaluate_single_question",
    "evaluate_all_questions",
    "run_evaluation",
    # Report generation
    "generate_report",
    "calculate_format_results",
    "calculate_token_counts",
    "save_results",
    # Validation
    "validate_answer",
    "validate_answers_batch",
    # Type definitions
    "Question",
    "QuestionType",
    "DatasetName",
    "EvaluationResult",
    "Dataset",
    "FormatResult",
]

__version__ = "0.1.0"
