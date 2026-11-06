"""
Windows Credential Manager Store (SEC-04, LOG-11) for 8-Bit Cyber Operations Office GUI.
Provides secure persistent storage of provider API keys & refresh tokens via `keyring`
(target format `security-team-gui:{provider}:{account_id}`), while maintaining ephemeral
short-lived access tokens in memory for size safety.
Strictly disallows fallback to plaintext `.env` files.
"""

import time
from typing import Dict, Any, Optional, Set
import keyring
from keyring.errors import KeyringError

from gui.server.redactor import register_secret

SERVICE_PREFIX: str = "security-team-gui"

# In-memory store for short-lived access tokens (LOG-11 Size Safety)
# Format: f"{provider}:{account_id}" -> {"token": str, "expires_at": Optional[float]}
_IN_MEMORY_TOKENS: Dict[str, Dict[str, Any]] = {}

# Set of all secrets retrieved or stored during the current session
_SESSION_LOADED_SECRETS: Set[str] = set()


class CredStoreError(Exception):
    """Base exception for Credential Store operations."""
    pass


class CredStoreUnavailableError(CredStoreError):
    """Raised when the underlying OS keyring/Credential Manager is locked or unavailable."""
    pass


def format_target(provider: str, account_id: str) -> str:
    """
    Format service target string for Windows Credential Manager:
    `security-team-gui:{provider}:{account_id}`
    """
    p = str(provider).strip().lower()
    a = str(account_id).strip()
    return f"{SERVICE_PREFIX}:{p}:{a}"


def is_available() -> bool:
    """
    Check if a viable non-fail OS keyring backend is available.
    """
    try:
        kr = keyring.get_keyring()
        if kr is None:
            return False
        # 'keyring.backends.fail.Keyring' indicates no functional keyring
        name = kr.__class__.__name__.lower()
        if "fail" in name:
            return False
        return True
    except Exception:
        return False


def set_credential(provider: str, account_id: str, secret: str) -> bool:
    """
    Store an API key or refresh token in the OS Credential Manager.
    Raises CredStoreUnavailableError if keyring fails or is unavailable.
    NEVER falls back to plaintext storage.
    """
    if not is_available():
        raise CredStoreUnavailableError(
            "Windows Credential Manager is unavailable or locked. Plaintext fallback is prohibited."
        )

    if not provider or not account_id:
        raise ValueError("Provider and account_id must be non-empty strings.")

    if not secret or not isinstance(secret, str):
        raise ValueError("Secret must be a non-empty string.")

    target = format_target(provider, account_id)
    try:
        # Use target as service_name and 'secret' as username
        keyring.set_password(target, "secret", secret)
        _SESSION_LOADED_SECRETS.add(secret)
        register_secret(secret)
        return True
    except KeyringError as e:
        raise CredStoreError(f"Failed to save credential in Credential Manager for '{target}': {e}") from e
    except Exception as e:
        raise CredStoreError(f"Unexpected error storing credential for '{target}': {e}") from e


def get_credential(provider: str, account_id: str) -> Optional[str]:
    """
    Retrieve an API key or refresh token from the OS Credential Manager.
    Raises CredStoreUnavailableError if keyring is unavailable.
    """
    if not is_available():
        raise CredStoreUnavailableError(
            "Windows Credential Manager is unavailable or locked. Plaintext fallback is prohibited."
        )

    if not provider or not account_id:
        raise ValueError("Provider and account_id must be non-empty strings.")

    target = format_target(provider, account_id)
    try:
        secret = keyring.get_password(target, "secret")
        if secret:
            _SESSION_LOADED_SECRETS.add(secret)
            register_secret(secret)
        return secret
    except KeyringError as e:
        raise CredStoreError(f"Failed to read credential from Credential Manager for '{target}': {e}") from e
    except Exception as e:
        raise CredStoreError(f"Unexpected error reading credential for '{target}': {e}") from e


def delete_credential(provider: str, account_id: str) -> bool:
    """
    Remove a credential from the OS Credential Manager and purge in-memory tokens.
    """
    if not is_available():
        raise CredStoreUnavailableError(
            "Windows Credential Manager is unavailable or locked."
        )

    if not provider or not account_id:
        raise ValueError("Provider and account_id must be non-empty strings.")

    target = format_target(provider, account_id)
    mem_key = f"{provider.lower()}:{account_id}"
    had_memory_token = _IN_MEMORY_TOKENS.pop(mem_key, None) is not None

    keyring_deleted = False
    try:
        keyring.delete_password(target, "secret")
        keyring_deleted = True
    except keyring.errors.PasswordDeleteError:
        # Credential was already deleted or did not exist in keyring
        keyring_deleted = False
    except KeyringError as e:
        raise CredStoreError(f"Failed to delete credential for '{target}': {e}") from e
    except Exception as e:
        raise CredStoreError(f"Unexpected error deleting credential for '{target}': {e}") from e

    return keyring_deleted or had_memory_token


def set_access_token(provider: str, account_id: str, access_token: str, expires_in_sec: Optional[float] = None) -> None:
    """
    Store a short-lived access token strictly in RAM (LOG-11 Size Safety).
    """
    mem_key = f"{provider.lower()}:{account_id}"
    expires_at = (time.time() + expires_in_sec) if expires_in_sec else None
    _IN_MEMORY_TOKENS[mem_key] = {
        "token": access_token,
        "expires_at": expires_at
    }
    _SESSION_LOADED_SECRETS.add(access_token)
    register_secret(access_token)


def get_access_token(provider: str, account_id: str) -> Optional[str]:
    """
    Retrieve valid non-expired in-memory access token.
    """
    mem_key = f"{provider.lower()}:{account_id}"
    record = _IN_MEMORY_TOKENS.get(mem_key)
    if not record:
        return None

    if record.get("expires_at") is not None and time.time() > record["expires_at"]:
        # Expired token
        _IN_MEMORY_TOKENS.pop(mem_key, None)
        return None

    return record.get("token")


def get_active_secret(provider: str, account_id: str) -> Optional[str]:
    """
    Return the active secret: prefers short-lived RAM access token if present/valid,
    otherwise retrieves persistent API key / refresh token from Windows Credential Manager.
    """
    token = get_access_token(provider, account_id)
    if token:
        return token
    return get_credential(provider, account_id)


def get_all_secrets() -> Set[str]:
    """
    Return all loaded and in-memory secrets for redactor synchronization.
    """
    return set(_SESSION_LOADED_SECRETS)


def reset_memory_store() -> None:
    """Reset ephemeral in-memory tokens (for tests)."""
    _IN_MEMORY_TOKENS.clear()
    _SESSION_LOADED_SECRETS.clear()
