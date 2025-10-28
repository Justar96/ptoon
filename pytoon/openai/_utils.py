"""Utility functions for processing OpenAI messages with TOON encoding."""

from typing import Any, Mapping, Optional, Sequence

import pytoon


def should_encode_to_toon(content: Any) -> bool:
    """
    Determine if content should be TOON-encoded.

    Args:
        content: The content to check

    Returns:
        True if content is a dict or list (structured data), False otherwise.
        Returns False for OpenAI content-part lists (lists where every element
        is a dict with a 'type' key, used for multimodal messages).
    """
    # Always encode plain dicts
    if isinstance(content, dict):
        return True

    # For lists, check if it's an OpenAI content-part list
    if isinstance(content, list):
        # Empty lists should be encoded
        if not content:
            return True

        # If every element is a dict with a "type" key, it's a content-part list
        # (e.g., [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {...}}])
        if all(isinstance(item, dict) and "type" in item for item in content):
            return False

        # Otherwise, it's a regular list that should be encoded
        return True

    return False


def encode_content(content: Any) -> Optional[str]:
    """
    Encode message content to TOON format if applicable.

    Args:
        content: The content to encode (dict, list, string, None, or other type)

    Returns:
        None if content is None, TOON-encoded string if content is dict/list,
        otherwise string representation
    """
    # Handle None explicitly to avoid converting to "None" string
    if content is None:
        return None

    if should_encode_to_toon(content):
        return pytoon.encode(content)
    if isinstance(content, str):
        return content
    return str(content)


def process_messages(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """
    Process a list of messages, encoding structured content to TOON format.

    Args:
        messages: Sequence of message mappings with 'content' field

    Returns:
        New list of messages with structured content encoded to TOON
    """
    processed = []
    for message in messages:
        # Create a shallow copy using dict unpacking to support Mapping types
        new_message = {**message}
        if "content" in new_message:
            new_message["content"] = encode_content(new_message["content"])
        processed.append(new_message)
    return processed

