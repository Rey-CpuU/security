"""
Security Guard Layer for 8-Bit Cyber Operations Office GUI.
Enforces strict localhost binding, Cross-Site WebSocket Hijacking (CSWSH) protection,
Origin validation, and ephemeral cryptographic session token verification.
"""

import hmac
import os
import secrets
import urllib.parse
from typing import Optional, Set
from fastapi import WebSocket, status

# Ephemeral cryptographic session token generated upon server startup
_SESSION_TOKEN: str = secrets.token_urlsafe(32)

# Default allowed localhost origins
DEFAULT_ALLOWED_ORIGINS: Set[str] = {
    "http://127.0.0.1:8888",
    "http://localhost:8888",
    "http://127.0.0.1",
    "http://localhost",
}


def get_session_token() -> str:
    """Return the active ephemeral session token."""
    global _SESSION_TOKEN
    return _SESSION_TOKEN


def reset_session_token() -> str:
    """Generate and return a new session token (useful for test resets)."""
    global _SESSION_TOKEN
    _SESSION_TOKEN = secrets.token_urlsafe(32)
    return _SESSION_TOKEN


def get_allowed_origins(port: Optional[int] = 8888) -> Set[str]:
    """Return the set of allowed origins for the given port."""
    if port:
        return {
            f"http://127.0.0.1:{port}",
            f"http://localhost:{port}",
            "http://127.0.0.1",
            "http://localhost",
        }
    return {
        "http://127.0.0.1",
        "http://localhost",
    }


def verify_origin(origin: Optional[str], port: Optional[int] = None) -> bool:
    """
    Validate that the incoming Origin header matches trusted local origins.
    Prevents Cross-Site Request Forgery and Cross-Site WebSocket Hijacking.
    """
    if not origin or not isinstance(origin, str):
        return False

    normalized = origin.strip().rstrip("/")
    if not normalized:
        return False

    try:
        parsed = urllib.parse.urlparse(normalized)
    except Exception:
        return False

    # Scheme must be http or https
    if parsed.scheme not in ("http", "https"):
        return False

    # Hostname must be strictly local loopback
    if parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        return False

    # If specific port is required, verify port match
    if port is not None:
        origin_port = parsed.port
        if origin_port is None:
            # If no port in origin string, check if normalized origin is in allowed origins
            return normalized in get_allowed_origins(port)
        return origin_port == port

    return True


def verify_session_token(token: Optional[str]) -> bool:
    """
    Constant-time comparison of the provided token against the active session token.
    Mitigates timing attacks.
    """
    if not token or not isinstance(token, str):
        return False
    return hmac.compare_digest(token, _SESSION_TOKEN)


def verify_websocket_handshake(websocket: WebSocket, token: Optional[str], port: Optional[int] = None) -> bool:
    """
    Combined CSWSH guard for WebSocket handshakes.
    Verifies both Origin header and cryptographic session token.
    """
    origin = websocket.headers.get("origin")
    check_port = port or websocket.url.port or int(os.environ.get("PORT", "8888"))
    if not verify_origin(origin, port=check_port):
        return False
    if not verify_session_token(token):
        return False
    return True
