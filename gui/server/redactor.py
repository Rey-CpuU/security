"""
Dual Redaction Engine (SEC-08) for 8-Bit Cyber Operations Office GUI.
Combines strict regex pattern masking with exact in-memory secret substring redaction.
Prevents leakage of API keys, bearer tokens, and credentials in logs, REST responses, and WebSockets.
"""

import re
from typing import Any, Iterable, List, Set, Union

# Regex patterns for well-known API keys and tokens.
# NOTE: '-' is placed at the very end of the character class [A-Za-z0-9_.-] to avoid accidental range interpretation.
KEY_PATTERNS: List[re.Pattern] = [
    # Anthropic Claude API keys (sk-ant-...)
    re.compile(r"sk-ant-[A-Za-z0-9_.-]{20,}", re.IGNORECASE),
    # OpenAI API keys (sk-...)
    re.compile(r"sk-[A-Za-z0-9_.-]{20,}", re.IGNORECASE),
    # Google AI / Gemini API keys (AIza...)
    re.compile(r"AIza[A-Za-z0-9_.-]{30,}", re.IGNORECASE),
    # Authorization Bearer tokens
    re.compile(r"Bearer\s+[A-Za-z0-9_.-]{20,}", re.IGNORECASE),
    # Agent Proxy Tokens (apt_...)
    re.compile(r"apt_[A-Za-z0-9_.-]{20,}", re.IGNORECASE),
    # WebSocket Tickets (wst_...)
    re.compile(r"wst_[A-Za-z0-9_.-]{20,}", re.IGNORECASE),
]

# In-memory registry of exact secret substrings loaded in Credential Store
_REGISTERED_SECRETS: Set[str] = set()
MIN_SECRET_LENGTH: int = 6


def register_secret(secret: str) -> None:
    """
    Register an exact secret substring into the redactor memory.
    Ignores empty or excessively short strings to prevent false-positive over-redaction.
    """
    if secret and isinstance(secret, str):
        cleaned = secret.strip()
        if len(cleaned) >= MIN_SECRET_LENGTH:
            _REGISTERED_SECRETS.add(cleaned)


def register_secrets(secrets: Iterable[str]) -> None:
    """Register multiple secret strings into memory."""
    for s in secrets:
        register_secret(s)


def clear_registered_secrets() -> None:
    """Clear all registered exact secrets (useful for test resets)."""
    _REGISTERED_SECRETS.clear()


def get_registered_secrets() -> Set[str]:
    """Return a copy of all currently registered exact secrets."""
    return set(_REGISTERED_SECRETS)


def redact(text: Union[str, Any]) -> str:
    """
    Sanitize text by redacting all known API key patterns and registered exact secret substrings.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    if not text:
        return ""

    result = text

    # 1. Regex Pattern Redaction (sk-*, AIza*, sk-ant-*, Bearer)
    for pattern in KEY_PATTERNS:
        result = pattern.sub("[REDACTED_API_KEY]", result)

    # 2. Exact Secret Substring Redaction
    # Sort registered secrets by length descending to match longest secrets first
    sorted_secrets = sorted(_REGISTERED_SECRETS, key=len, reverse=True)
    for secret in sorted_secrets:
        if secret in result:
            result = result.replace(secret, "[REDACTED_SECRET]")

    return result


def redact_object(data: Any) -> Any:
    """
    Recursively redact strings in dictionaries, lists, or primitive values.
    """
    if isinstance(data, str):
        return redact(data)
    elif isinstance(data, dict):
        return {k: redact_object(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_object(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(redact_object(item) for item in data)
    elif isinstance(data, set):
        return {redact_object(item) for item in data}
    return data
