"""
Hardened LLM Reverse Proxy (SEC-06, Boundary 2).
Provides a secure gateway for agents calling LLM APIs (/v1/proxy/*).
Features:
- Path allowlist: Only /v1/chat/completions, /v1/models, /v1/messages, /v1beta/models/*
- Header rebuilding: Drops all agent auth headers and query ?key=; injects active account key from cred_store
- Anti-SSRF: follow_redirects=False, upstream domain allowlist, DNS IP verification (rejects private/loopback/link-local)
- Token Domain Separation: Requires AGENT_PROXY_TOKEN; rejects GUI_SESSION_TOKEN
- Runtime Gating: Enforces model_id scope and CONNECTED provider status on every request
- Full SSE (Server-Sent Events) streaming support
"""

import ipaddress
import json
import re
import socket
import urllib.parse
from typing import Any, AsyncGenerator, Dict, List, Optional, Set, Tuple, Union
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
import httpx

from gui.server import cred_store, redactor
from gui.server.providers import provider_manager, ProviderStatus
from gui.server.security import (
    is_agent_proxy_token,
    verify_agent_proxy_token,
    verify_session_token,
    get_session_token,
)

proxy_router = APIRouter(prefix="/v1/proxy", tags=["LLM Reverse Proxy"])

ALLOWED_UPSTREAM_DOMAINS: Set[str] = {
    "api.anthropic.com",
    "api.openai.com",
    "generativelanguage.googleapis.com",
}

# Regex for allowed path patterns
ALLOWED_PATH_PATTERNS: List[re.Pattern] = [
    re.compile(r"^(?:/v1)?/chat/completions/?$"),
    re.compile(r"^(?:/v1)?/models/?$"),
    re.compile(r"^(?:/v1)?/messages/?$"),
    re.compile(r"^(?:/v1beta)?/models/?$"),
    re.compile(r"^(?:/v1beta)?/models/[A-Za-z0-9_.-]+:(?:generateContent|streamGenerateContent)/?$"),
]

MAX_REQUEST_BODY_BYTES = 10 * 1024 * 1024  # 10 MB


def is_ip_safe(ip: Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]) -> bool:
    """
    Check if an IP address is a safe public routable IP.
    Rejects private, loopback, link-local, reserved, multicast, or unspecified IPs.
    """
    if isinstance(ip, str):
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return False
    else:
        ip_obj = ip

    if (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_reserved
        or ip_obj.is_multicast
        or ip_obj.is_unspecified
    ):
        return False
    return True


def verify_url_ssrf_safe(url: str) -> Tuple[bool, str]:
    """
    Verify upstream destination URL against domain allowlist and DNS-resolved IP checks.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in target URL"

        if parsed.scheme not in ("https", "http"):
            return False, f"Disallowed URL scheme '{parsed.scheme}'"

        # 1. Domain Allowlist Check
        if hostname.lower() not in ALLOWED_UPSTREAM_DOMAINS:
            return False, f"Target host '{hostname}' not in allowed upstream domains"

        # 2. DNS Resolution IP Check
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            if not is_ip_safe(ip_str):
                return False, f"Resolved IP {ip_str} is in private/disallowed address space (Anti-SSRF)"

        return True, "Safe"
    except Exception as e:
        return False, f"SSRF verification failed: {e}"


def is_path_allowed(path: str) -> bool:
    """Check if the normalized requested path is within the strict allowlist."""
    normalized = path.strip()
    if not normalized.startswith("/"):
        normalized = "/" + normalized

    # Strip /v1/proxy prefix if present
    if normalized.startswith("/v1/proxy"):
        normalized = normalized[len("/v1/proxy"):]
        if not normalized.startswith("/"):
            normalized = "/" + normalized

    # Strip /gemini prefix if present (e.g. /v1/proxy/gemini/v1beta/models)
    if normalized.startswith("/gemini"):
        normalized = normalized[len("/gemini"):]
        if not normalized.startswith("/"):
            normalized = "/" + normalized

    for pattern in ALLOWED_PATH_PATTERNS:
        if pattern.match(normalized):
            return True

    return False


def extract_and_verify_proxy_auth(request: Request) -> Dict[str, Any]:
    """
    Validate Agent Proxy Token domain separation (Boundary 1).
    Rejects missing tokens, GUI session tokens, and invalid/expired tokens.
    """
    auth_header = request.headers.get("authorization", "")
    proxy_token_header = request.headers.get("x-agent-proxy-token", "")

    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif proxy_token_header:
        token = proxy_token_header.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Agent Proxy Token in Authorization header"
        )

    # SEC-02 Token Domain Check: GUI Session Token cannot access proxy!
    if verify_session_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token Domain Mismatch: GUI Session Token cannot directly call Proxy"
        )

    meta = verify_agent_proxy_token(token)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired Agent Proxy Token"
        )

    return meta


@proxy_router.api_route("/{path:path}", methods=["GET", "POST"])
async def reverse_proxy_handler(path: str, request: Request):
    """
    Main dispatch endpoint for all LLM reverse proxy requests.
    Enforces path allowlist, token isolation, model gating, header rebuilding, and anti-SSRF.
    """
    normalized_path = "/" + path.lstrip("/")

    # Check and strip /gemini route prefix
    is_gemini_route = False
    if normalized_path.startswith("/gemini"):
        normalized_path = normalized_path[len("/gemini"):]
        if not normalized_path.startswith("/"):
            normalized_path = "/" + normalized_path
        is_gemini_route = True

    # 1. Path Allowlist Gate
    if not is_path_allowed(normalized_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Proxy path '{normalized_path}' blocked by security allowlist"
        )

    # 2. Token Domain & Agent Proxy Token Validation
    token_meta = extract_and_verify_proxy_auth(request)
    allowed_model_id = token_meta.get("allowed_model_id")

    # Read and inspect body if POST
    body_bytes = b""
    body_json: Dict[str, Any] = {}
    if request.method == "POST":
        body_bytes = await request.body()
        if len(body_bytes) > MAX_REQUEST_BODY_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body exceeds 10MB limit"
            )
        if body_bytes:
            try:
                body_json = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                pass

    # 3. Model Scope & Provider Runtime Status Check
    requested_model = body_json.get("model") or allowed_model_id
    if not requested_model:
        # Fallback to model in path e.g. /v1beta/models/{model}:generateContent
        if "/models/" in normalized_path:
            parts = normalized_path.split("/models/")[1].split(":")
            requested_model = parts[0]

    # Verify model matches agent proxy token allowance
    if requested_model and allowed_model_id and requested_model != allowed_model_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Model mismatch: requested '{requested_model}' but token is restricted to '{allowed_model_id}'"
        )

    target_model = requested_model or allowed_model_id
    prov = None
    if is_gemini_route or normalized_path.startswith("/v1beta"):
        prov = provider_manager.get_provider("gemini")
    if not prov and target_model:
        prov = provider_manager.resolve_provider_for_model(target_model)

    if not prov:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No provider found for model '{target_model}'"
        )

    if target_model:
        is_allowed, reason = provider_manager.can_dispatch_model(target_model)
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Model '{target_model}' not dispatchable: {reason}"
            )

    # 4. Resolve Active Account & Upstream Secret
    account = prov.get_active_account()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No available active accounts in provider '{prov.display_name}' pool"
        )

    secret = cred_store.get_active_secret(prov.name, account.id)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Credential missing from secure vault for account '{account.id}'"
        )

    # 5. Sanitize and rebuild query parameters (SEC-06: drop agent auth keys and query ?key=)
    clean_params = dict(request.query_params)
    clean_params.pop("key", None)
    clean_params.pop("apiKey", None)
    clean_params.pop("api_key", None)

    # 6. Determine Upstream Base URL and Rebuild Headers from Scratch
    upstream_url = ""
    rebuilt_headers = {
        "Content-Type": "application/json",
        "Accept": request.headers.get("accept", "application/json"),
        "User-Agent": "security-team-proxy/1.0"
    }

    # Ensure normalized_path starts with /v1 (or /v1beta)
    if not (normalized_path.startswith("/v1") or normalized_path.startswith("/v1beta")):
        normalized_path = "/v1" + normalized_path

    if prov.name == "anthropic":
        upstream_url = f"https://api.anthropic.com{normalized_path}"
        rebuilt_headers["x-api-key"] = secret
        rebuilt_headers["anthropic-version"] = "2023-06-01"

    elif prov.name == "openai":
        upstream_url = f"https://api.openai.com{normalized_path}"
        rebuilt_headers["Authorization"] = f"Bearer {secret}"

    elif prov.name == "gemini":
        upstream_url = f"https://generativelanguage.googleapis.com{normalized_path}"
        rebuilt_headers["x-goog-api-key"] = secret
        clean_params["key"] = secret

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Direct reverse proxy not supported for provider '{prov.name}'"
        )

    # 7. Anti-SSRF Verification
    safe, ssrf_err = verify_url_ssrf_safe(upstream_url)
    if not safe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SSRF Protection blocked request: {ssrf_err}"
        )

    # 8. Execute Upstream Request with follow_redirects=False & SSE Streaming
    is_stream = bool(body_json.get("stream"))

    try:
        client = httpx.AsyncClient(timeout=120.0, follow_redirects=False)

        if is_stream:
            req = client.build_request(
                method=request.method,
                url=upstream_url,
                params=clean_params,
                headers=rebuilt_headers,
                content=body_bytes
            )
            upstream_resp = await client.send(req, stream=True)

            # Trigger account failover/cooldown on upstream rate limit or auth rejection
            if upstream_resp.status_code == 429:
                retry_header = upstream_resp.headers.get("retry-after") or "60"
                try:
                    cooldown = float(retry_header)
                except ValueError:
                    cooldown = 60.0
                prov.set_cooldown(account.id, cooldown, reason="Upstream rate limit (HTTP 429)")
            elif upstream_resp.status_code in (401, 403):
                prov.mark_status(account.id, ProviderStatus.INVALID_CRED, error=f"Upstream returned HTTP {upstream_resp.status_code}")

            async def stream_generator() -> AsyncGenerator[bytes, None]:
                try:
                    async for chunk in upstream_resp.aiter_bytes():
                        # Redact chunk before forwarding to client
                        redacted_text = redactor.redact(chunk.decode("utf-8", errors="replace"))
                        yield redacted_text.encode("utf-8")
                finally:
                    await upstream_resp.aclose()
                    await client.aclose()

            return StreamingResponse(
                stream_generator(),
                status_code=upstream_resp.status_code,
                media_type="text/event-stream"
            )

        else:
            async with client:
                resp = await client.request(
                    method=request.method,
                    url=upstream_url,
                    params=clean_params,
                    headers=rebuilt_headers,
                    content=body_bytes
                )

            # Trigger account failover/cooldown on upstream rate limit or auth rejection
            if resp.status_code == 429:
                retry_header = resp.headers.get("retry-after") or "60"
                try:
                    cooldown = float(retry_header)
                except ValueError:
                    cooldown = 60.0
                prov.set_cooldown(account.id, cooldown, reason="Upstream rate limit (HTTP 429)")
            elif resp.status_code in (401, 403):
                prov.mark_status(account.id, ProviderStatus.INVALID_CRED, error=f"Upstream returned HTTP {resp.status_code}")

            # Redact response text to ensure upstream does not echo secrets
            redacted_body = redactor.redact(resp.text)
            response_media = resp.headers.get("content-type", "application/json")
            return Response(
                content=redacted_body,
                status_code=resp.status_code,
                media_type=response_media
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream provider connection error: {redactor.redact(str(e))}"
        )
