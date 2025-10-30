"""OpenAI client wrappers with automatic TOON encoding for structured data."""

from collections.abc import Mapping, Sequence
from typing import Any

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion

from ._utils import process_messages


class Pytoon:
    """
    Synchronous OpenAI client wrapper with automatic TOON encoding.

    This is a drop-in replacement for openai.OpenAI that automatically encodes
    structured data (dict/list) in message content to TOON format for improved
    token efficiency.

    Example:
        >>> client = Pytoon(api_key="your-api-key")
        >>> response = client.chat.completions.create(
        ...     "gpt-5",
        ...     [{"role": "user", "content": {"data": [1, 2, 3]}}]
        ... )
    """

    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int = 2,
        default_headers: dict | None = None,
        default_query: dict | None = None,
        **kwargs,
    ):
        """
        Initialize the Pytoon client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            organization: OpenAI organization ID
            base_url: Override the default API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            default_headers: Default headers to include in all requests
            default_query: Default query parameters to include in all requests
            **kwargs: Additional parameters to pass to the OpenAI client
        """
        self._client = OpenAI(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            **kwargs,
        )
        self.chat = self._ChatNamespace(self._client)

    class _ChatNamespace:
        """Namespace for chat-related operations."""

        def __init__(self, client: OpenAI, parent_class=None):
            self._client = client
            # Defer lookup to avoid circular reference during class definition
            if parent_class is None:
                parent_class = Pytoon
            self.completions = parent_class._CompletionsNamespace(client)

    class _CompletionsNamespace:
        """Namespace for chat completions operations."""

        def __init__(self, client: OpenAI):
            self._client = client

        def create(
            self,
            model: str,
            messages: Sequence[Mapping[str, Any]],
            **kwargs,
        ) -> ChatCompletion:
            """
            Create a chat completion with automatic TOON encoding.

            Structured data (dict/list) in message content is automatically
            encoded to TOON format before sending to the API.

            Args:
                model: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
                messages: Sequence of message mappings
                **kwargs: Additional parameters (temperature, max_tokens, etc.)

            Returns:
                ChatCompletion response object from OpenAI
            """
            processed_messages = process_messages(messages)
            return self._client.chat.completions.create(
                model=model,
                messages=processed_messages,  # type: ignore[arg-type]
                **kwargs,
            )


class AsyncPytoon:
    """
    Asynchronous OpenAI client wrapper with automatic TOON encoding.

    This is a drop-in replacement for openai.AsyncOpenAI that automatically
    encodes structured data (dict/list) in message content to TOON format for
    improved token efficiency.

    Example:
        >>> client = AsyncPytoon(api_key="your-api-key")
        >>> response = await client.chat.completions.create(
        ...     "gpt-4",
        ...     [{"role": "user", "content": {"data": [1, 2, 3]}}]
        ... )
    """

    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int = 2,
        default_headers: dict | None = None,
        default_query: dict | None = None,
        **kwargs,
    ):
        """
        Initialize the AsyncPytoon client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            organization: OpenAI organization ID
            base_url: Override the default API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            default_headers: Default headers to include in all requests
            default_query: Default query parameters to include in all requests
            **kwargs: Additional parameters to pass to the OpenAI client
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            **kwargs,
        )
        self.chat = self._ChatNamespace(self._client)

    class _ChatNamespace:
        """Namespace for chat-related operations."""

        def __init__(self, client: AsyncOpenAI, parent_class=None):
            self._client = client
            # Defer lookup to avoid circular reference during class definition
            if parent_class is None:
                parent_class = AsyncPytoon
            self.completions = parent_class._CompletionsNamespace(client)

    class _CompletionsNamespace:
        """Namespace for chat completions operations."""

        def __init__(self, client: AsyncOpenAI):
            self._client = client

        async def create(
            self,
            model: str,
            messages: Sequence[Mapping[str, Any]],
            **kwargs,
        ) -> ChatCompletion:
            """
            Create a chat completion with automatic TOON encoding.

            Structured data (dict/list) in message content is automatically
            encoded to TOON format before sending to the API.

            Args:
                model: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
                messages: Sequence of message mappings
                **kwargs: Additional parameters (temperature, max_tokens, etc.)

            Returns:
                ChatCompletion response object from OpenAI
            """
            processed_messages = process_messages(messages)
            return await self._client.chat.completions.create(
                model=model,
                messages=processed_messages,  # type: ignore[arg-type]
                **kwargs,
            )
