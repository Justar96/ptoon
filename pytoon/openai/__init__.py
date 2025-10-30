"""
TOON-enabled OpenAI SDK wrapper with automatic encoding.

This module provides drop-in replacements for the OpenAI SDK clients that
automatically encode structured data (dict/list) in message content to TOON
format for improved token efficiency.

Basic Usage:
    >>> from pytoon.openai import Pytoon
    >>>
    >>> client = Pytoon(api_key="your-api-key")
    >>>
    >>> # Structured data is automatically encoded to TOON
    >>> response = client.chat.completions.create(
    ...     "gpt-4",
    ...     [{
    ...         "role": "user",
    ...         "content": {
    ...             "employees": [
    ...                 {"name": "Alice", "salary": 120000},
    ...                 {"name": "Bob", "salary": 95000}
    ...             ]
    ...         }
    ...     }]
    ... )

Async Usage:
    >>> from pytoon.openai import AsyncPytoon
    >>> import asyncio
    >>>
    >>> async def main():
    ...     client = AsyncPytoon(api_key="your-api-key")
    ...     response = await client.chat.completions.create(
    ...         "gpt-4",
    ...         [{
    ...             "role": "user",
    ...             "content": {"data": [1, 2, 3, 4, 5]}
    ...         }]
    ...     )
    ...     return response
    >>>
    >>> asyncio.run(main())

Key Features:
    - Automatic TOON encoding for dict/list content (30-60% token savings)
    - Plain strings passed through unchanged
    - 100% OpenAI SDK API compatibility
    - Supports all OpenAI client parameters and features
"""

from ._client import AsyncPytoon, Pytoon


__all__ = ["Pytoon", "AsyncPytoon"]
