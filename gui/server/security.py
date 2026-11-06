"""
Security Guard Layer for 8-Bit Cyber Operations Office GUI.
Enforces strict localhost binding, Host header validation (SEC-02),
Cross-Site WebSocket Hijacking (CSWSH) protection, Origin validation,
ticket-based WebSocket authentication (SEC-11), and token domain separation
(GUI Session Token vs Agent Proxy Token).
"""

import hmac
import os
import secrets
import time
import urllib.parse
from typing import Optional, Set, Dict, Any
from fastapi import WebSocket

from gui.server.redactor import register_secret

# Ephemeral cryptographic session token generated upon server startup
_SESSION_TOKEN: str = secrets.token_urlsafe(32)
register_secret(_SESSION_TOKEN)

# Default allowed localhost origins
DEFAULT_ALLOWED_ORIGINS: Set[str] = {
    "http://127.0.0.1:8888",
    "http://localhost:8888",
    "http://127.0.0.1",
    "http://localhost",
}

# Single-use WebSocket tickets: ticket -> expires_at (SEC-11)
_WS_TICKETS: Dict[str, float] = {}

# Agent proxy tokens: token -> metadata (Boundary 1)
# metadata: {"agent_id": str, "card_id": str, "allowed_model_id": str, "exp": float}
_AGENT_PROXY_TOKENS: Dict[str, Dict[str, Any]] = {}


def get_session_token() -> str:
    """Return the active ephemeral GUI session token."""
    global _SESSION_TOKEN
    return _SESSION_TOKEN


def reset_session_token() -> str:
    """Generate and return a new session token (useful for test resets)."""
    global _SESSION_TOKEN
    _SESSION_TOKEN = secrets.token_urlsafe(32)
    register_secret(_SESSION_TOKEN)
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


def verify_host(host_header: Optional[str], port: Optional[int] = None) -> bool:
    """
    Validate that the incoming Host header matches trusted local loopback addresses (SEC-02).
    Protects against DNS Rebinding and Host Header Injection.
    """
    if not host_header or not isinstance(host_header, str):
        return False

    host_str = host_header.strip().lower()

    # IPv6 format e.g. [::1]:8888 or [::1]
    if host_str.startswith("["):
        idx = host_str.find("]")
        if idx == -1:
            return False
        hostname = host_str[1:idx]
        port_part = host_str[idx + 1 :]
        if port_part.startswith(":"):
            port_part = port_part[1:]
        else:
            port_part = None
    else:
        parts = host_str.split(":")
        hostname = parts[0]
        port_part = parts[1] if len(parts) > 1 else None

    # Hostname must be strictly local loopback (or testserver during TestClient execution)
    if hostname not in ("127.0.0.1", "localhost", "::1", "testserver"):
        return False

    # If port is specified and host header has a port, they must match
    if port is not None and port_part is not None:
        try:
            if int(port_part) != port:
                return False
        except ValueError:
            return False

    return True


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
    Constant-time comparison of the provided token against the active GUI session token.
    Mitigates timing attacks.
    """
    if not token or not isinstance(token, str):
        return False
    return hmac.compare_digest(token, _SESSION_TOKEN)


# --- SEC-11: Ticket-Based WebSocket Authentication ---

def create_ws_ticket(ttl_seconds: int = 30) -> str:
    """
    Generate a single-use cryptographically random ticket for WebSocket handshake.
    TTL is 30 seconds. Ticket is burned upon single use.
    """
    ticket = f"wst_{secrets.token_urlsafe(24)}"
    _WS_TICKETS[ticket] = time.time() + ttl_seconds
    register_secret(ticket)
    return ticket


def verify_and_consume_ws_ticket(ticket: Optional[str]) -> bool:
    """
    Verify and burn a single-use WebSocket ticket.
    """
    if not ticket or not isinstance(ticket, str):
        return False

    # Clean expired tickets opportunistically
    now = time.time()
    expired = [t for t, exp in _WS_TICKETS.items() if now > exp]
    for t in expired:
        _WS_TICKETS.pop(t, None)

    # Strictly atomic single-use consumption
    exp = _WS_TICKETS.pop(ticket, None)
    if exp is not None:
        return now <= exp

    return False


def verify_websocket_handshake(
    websocket: WebSocket,
    token: Optional[str] = None,
    ticket: Optional[str] = None,
    port: Optional[int] = None
) -> bool:
    """
    Combined CSWSH guard for WebSocket handshakes.
    Verifies Origin header and single-use ticket (or session token for legacy compatibility).
    """
    origin = websocket.headers.get("origin")
    check_port = port or websocket.url.port or int(os.environ.get("PORT", "8888"))
    if not verify_origin(origin, port=check_port):
        return False

    # Check ticket first (SEC-11)
    if ticket and verify_and_consume_ws_ticket(ticket):
        return True

    # If token param passed ticket or session token
    if token:
        if verify_and_consume_ws_ticket(token):
            return True
        if verify_session_token(token):
            return True

    return False


# --- Boundary 1: Token Domain Separation (GUI Session vs Agent Proxy) ---

def create_agent_proxy_token(
    agent_id: str,
    card_id: str,
    allowed_model_id: str,
    ttl_seconds: int = 3600
) -> str:
    """
    Generate a scoped Agent Proxy Token bound strictly to (agent_id, card_id, allowed_model_id).
    This token is ONLY valid on /v1/proxy/* routes.
    """
    token = f"apt_{secrets.token_urlsafe(32)}"
    _AGENT_PROXY_TOKENS[token] = {
        "agent_id": agent_id,
        "card_id": card_id,
        "allowed_model_id": allowed_model_id,
        "exp": time.time() + ttl_seconds
    }
    register_secret(token)
    return token


def verify_agent_proxy_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Verify an Agent Proxy Token and return its bound metadata if valid and non-expired.
    """
    if not token or not isinstance(token, str):
        return None

    # Clean expired tokens opportunistically
    now = time.time()
    meta = _AGENT_PROXY_TOKENS.get(token)
    if not meta:
        return None

    if now > meta["exp"]:
        _AGENT_PROXY_TOKENS.pop(token, None)
        return None

    return meta


def is_agent_proxy_token(token: Optional[str]) -> bool:
    """
    Check if a token string represents an agent proxy token format or registered proxy token.
    """
    if not token or not isinstance(token, str):
        return False
    if token.startswith("apt_"):
        return True
    return token in _AGENT_PROXY_TOKENS


def revoke_agent_proxy_token(token: str) -> None:
    """Revoke an agent proxy token when task finishes."""
    _AGENT_PROXY_TOKENS.pop(token, None)


def reset_tokens_for_tests() -> None:
    """Reset all tokens and tickets (for unit tests)."""
    _WS_TICKETS.clear()
    _AGENT_PROXY_TOKENS.clear()
    reset_session_token()
