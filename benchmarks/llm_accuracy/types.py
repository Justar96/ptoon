"""Type definitions for LLM accuracy benchmark.

This module mirrors the TypeScript implementation in toon-ts/benchmarks/src/types.ts
and provides type safety for question generation, evaluation, and validation.
"""

from typing import Any, Literal, TypedDict


# Question type categories
QuestionType = Literal["field-retrieval", "aggregation", "filtering"]

# Dataset names
DatasetName = Literal["tabular", "nested", "analytics", "github"]


class Question(TypedDict):
    """Represents a benchmark question with expected answer.

    Attributes:
        id: Unique identifier (e.g., "q1", "q2")
        prompt: The question text presented to the LLM
        ground_truth: Expected answer as string
        type: Category of question (field-retrieval, aggregation, filtering)
        dataset: Source dataset name

    Example:
        {
            "id": "q1",
            "prompt": "What is Alice Johnson's salary?",
            "ground_truth": "95000",
            "type": "field-retrieval",
            "dataset": "tabular"
        }
    """

    id: str
    prompt: str
    ground_truth: str
    type: QuestionType
    dataset: DatasetName


class EvaluationResult(TypedDict):
    """Results from evaluating an LLM's answer to a question.

    Attributes:
        question_id: Reference to the question being evaluated
        format: Data format used ("JSON" or "TOON")
        model: LLM model identifier
        expected: Ground truth answer
        actual: LLM's actual answer
        is_correct: Whether the answer was validated as correct
        input_tokens: Number of tokens in the prompt
        output_tokens: Number of tokens in the response
        latency_ms: Response time in milliseconds
    """

    question_id: str
    format: Literal["JSON", "TOON"]
    model: str
    expected: str
    actual: str
    is_correct: bool
    input_tokens: int
    output_tokens: int
    latency_ms: float


class Dataset(TypedDict):
    """Metadata and data for a benchmark dataset.

    Attributes:
        name: Dataset identifier
        description: Human-readable description
        data: The actual dataset (structure varies by dataset type)
    """

    name: str
    description: str
    data: dict[str, Any]


__all__ = [
    "QuestionType",
    "DatasetName",
    "Question",
    "EvaluationResult",
    "Dataset",
]
