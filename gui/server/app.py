"""
FastAPI Application Server for 8-Bit Cyber Operations Office GUI.
Provides RESTful management APIs, secure static asset hosting,
authenticated WebSocket real-time event streaming, Provider Hub,
and hardened LLM reverse proxy.
"""

import os
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gui.server.security import (
    verify_host,
    verify_origin,
    verify_session_token,
    verify_websocket_handshake,
    get_session_token,
    reset_session_token,
    create_ws_ticket,
    create_agent_proxy_token,
    is_agent_proxy_token
)
from gui.server.llm_proxy import proxy_router
from gui.server.providers import provider_manager, ProviderStatus
from gui.server.state import state_manager, sanitize_card_for_client
from gui.server.triage_bridge import run_triage

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="Security Team 8-Bit Cyber Operations Office",
    description="Local secure GUI for orchestrating multi-harness security agents & Provider Hub",
    version="2.0.0"
)

# Mount reverse proxy router
app.include_router(proxy_router)

# Mount static asset directory
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- Security Middleware (SEC-02 Host Check, Token Domain Separation, CSP) ---

@app.middleware("http")
async def security_guard_middleware(request: Request, call_next):
    # 1. Host Header Validation (SEC-02 Anti-DNS Rebinding)
    request_port = request.url.port or int(os.environ.get("PORT", "8888"))
    host = request.headers.get("host")
    if not verify_host(host, port=request_port):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Forbidden: Untrusted Host Header (Anti-DNS Rebinding)"}
        )

    # 2. Token Domain Separation (Boundary 1)
    # Agent Proxy Tokens are strictly forbidden on admin /api/* routes
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("authorization", "")
        token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.headers.get("x-agent-proxy-token", "")
        if is_agent_proxy_token(token):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Admin Route Restricted: Agent Proxy Token cannot access GUI Admin API"}
            )

    response = await call_next(request)

    # 3. Baseline Security Headers & CSP (Fase 0)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; font-src 'self'; "
        "connect-src 'self' ws: wss:; frame-ancestors 'none';"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


# --- Request Data Models ---

class CreateCardRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    assigned_agent: Optional[str] = None
    dry_run: Optional[bool] = None
    model: Optional[str] = None


class TriageRequest(BaseModel):
    query: str


class SettingsUpdateRequest(BaseModel):
    default_harness: Optional[str] = None
    dry_run_default: Optional[bool] = None
    max_parallel_agents: Optional[int] = None
    agent_models: Optional[Dict[str, Any]] = None
    providers: Optional[Dict[str, Any]] = None


class AddAccountRequest(BaseModel):
    id: str
    label: str
    priority: int = 1
    enabled: bool = True
    secret: Optional[str] = None


class SetStrategyRequest(BaseModel):
    strategy: str


# --- Core Web & Auth Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve index.html with securely injected active session token.
    """
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        return HTMLResponse("<h3>index.html not found</h3>", status_code=404)

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject ephemeral session token into client page
    token = get_session_token()
    content = content.replace("__SESSION_TOKEN__", token)
    return HTMLResponse(content)


@app.get("/api/auth/token")
async def get_auth_token(request: Request):
    """
    Provide session token only to verified local browser origins.
    """
    origin = request.headers.get("origin")
    request_port = request.url.port or int(os.environ.get("PORT", "8888"))
    if origin and not verify_origin(origin, port=request_port):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Untrusted Origin"
        )
    return {"token": get_session_token()}


@app.post("/api/auth/ws-ticket")
async def issue_ws_ticket(request: Request):
    """
    SEC-11: Issue a single-use cryptographically random ticket for WebSocket handshake.
    TTL is 30 seconds.
    """
    origin = request.headers.get("origin")
    request_port = request.url.port or int(os.environ.get("PORT", "8888"))
    if origin and not verify_origin(origin, port=request_port):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Untrusted Origin"
        )

    # Validate GUI Session Token (strict check: missing token is rejected)
    token = request.headers.get("x-security-team-token") or request.query_params.get("token")
    if not token or not verify_session_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid GUI Session Token"
        )

    ticket = create_ws_ticket(ttl_seconds=30)
    return {"ticket": ticket, "expires_in": 30}


@app.get("/api/state")
async def get_office_state():
    """
    Return complete office, agent, queue, settings, and provider pool snapshot.
    """
    return state_manager.get_full_state()


# --- Task Card Dispatch & Gating (SEC-01) ---

@app.post("/api/cards")
async def create_card(card_req: CreateCardRequest):
    """
    Submit a task card for automated triage and office agent execution.
    Enforces SEC-01 Backend Dispatch Gating against provider & model connection status.
    """
    # 1. Resolve agent
    resolved_agent = card_req.assigned_agent
    if not resolved_agent or resolved_agent == "auto" or resolved_agent not in state_manager.agents:
        query_text = f"{card_req.title}. {card_req.description}".strip()
        triage_info = run_triage(query_text)
        resolved_agent = triage_info["recommended_agent_id"]

    # 2. Resolve model
    target_model = card_req.model or state_manager.settings.get("agent_models", {}).get(
        resolved_agent, "claude-3-7-sonnet-20250219"
    )

    # 3. SEC-01 Dispatch Gating Check
    can_dispatch, reason = provider_manager.can_dispatch_model(target_model)
    if not can_dispatch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Dispatch rejected by model gating: {reason}"
        )

    # 4. Generate scoped Agent Proxy Token
    card_id = f"card-{uuid.uuid4().hex[:8]}"
    proxy_token = create_agent_proxy_token(
        agent_id=resolved_agent,
        card_id=card_id,
        allowed_model_id=target_model,
        ttl_seconds=3600
    )

    # 5. Add card to queue with matching card_id
    card = await state_manager.add_card(
        title=card_req.title,
        description=card_req.description or "",
        assigned_agent=resolved_agent,
        dry_run=card_req.dry_run,
        model=target_model,
        agent_proxy_token=proxy_token,
        card_id=card_id
    )
    return sanitize_card_for_client(card)


@app.post("/api/cards/{card_id}/cancel")
async def cancel_card(card_id: str):
    """
    Cancel an active or queued task card.
    """
    success = await state_manager.cancel_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Card '{card_id}' not found")
    return {"status": "ok", "card_id": card_id}


@app.post("/api/triage")
async def triage_task(req: TriageRequest):
    """
    Run triage classifier and return recommended agent & required skills.
    """
    result = run_triage(req.query)
    return result


@app.get("/api/settings")
async def get_settings():
    """
    Fetch current user settings.
    """
    return state_manager.settings


@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    """
    Update settings (models, dry-run safety default, concurrency limits, providers).
    """
    payload = req.model_dump(exclude_unset=True)
    updated = state_manager.save_settings(payload)
    await state_manager.broadcast({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })
    return updated


# --- Provider Hub Management APIs (Fase 1) ---

@app.get("/api/providers")
async def list_providers():
    """List all registered providers, account pools, and models catalog."""
    return {
        "providers": provider_manager.to_dict(),
        "models": provider_manager.get_all_models()
    }


@app.post("/api/providers/{provider_name}/accounts")
async def add_provider_account(provider_name: str, req: AddAccountRequest):
    """Add or update an account in a provider pool and store secret in keyring."""
    prov = provider_manager.get_provider(provider_name)
    if not prov:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    acc = prov.add_account(
        account_id=req.id,
        label=req.label,
        priority=req.priority,
        enabled=req.enabled,
        secret=req.secret
    )

    state_manager.save_settings({"providers": provider_manager.to_dict()})
    await state_manager.broadcast({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })

    return acc.model_dump(exclude={"error_message"})


@app.delete("/api/providers/{provider_name}/accounts/{account_id}")
async def remove_provider_account(provider_name: str, account_id: str):
    """Remove an account and delete its secret from OS Credential Manager."""
    prov = provider_manager.get_provider(provider_name)
    if not prov:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    removed = prov.remove_account(account_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{account_id}' not found in provider '{provider_name}'"
        )

    state_manager.save_settings({"providers": provider_manager.to_dict()})
    await state_manager.broadcast({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })

    return {"status": "ok", "deleted": account_id}


@app.post("/api/providers/{provider_name}/accounts/{account_id}/verify")
async def verify_provider_account(provider_name: str, account_id: str):
    """Trigger a live probe verification for an account."""
    prov = provider_manager.get_provider(provider_name)
    if not prov:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    acc = prov.get_account(account_id)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{account_id}' not found"
        )

    success, message = await prov.verify_account(account_id)
    state_manager.save_settings({"providers": provider_manager.to_dict()})
    await state_manager.broadcast({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })

    return {
        "success": success,
        "message": message,
        "status": acc.status.value
    }


@app.post("/api/providers/{provider_name}/strategy")
async def set_provider_strategy(provider_name: str, req: SetStrategyRequest):
    """Update account routing strategy (priority | round-robin | least-used)."""
    prov = provider_manager.get_provider(provider_name)
    if not prov:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    prov.strategy = req.strategy
    state_manager.save_settings({"providers": provider_manager.to_dict()})
    return {"status": "ok", "strategy": prov.strategy}


# --- Authenticated WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    ticket: Optional[str] = Query(None)
):
    """
    Authenticated real-time WebSocket connection.
    Guards against CSWSH via Origin check and ticket/token authentication.
    """
    request_port = websocket.url.port or int(os.environ.get("PORT", "8888"))

    # 1. Security Handshake Check (SEC-11 & CSWSH)
    if not verify_websocket_handshake(websocket, token=token, ticket=ticket, port=request_port):
        origin = websocket.headers.get("origin")
        if not verify_origin(origin, port=request_port):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Untrusted Origin")
        else:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid Session Token or Ticket")
        return

    # 2. Accept and Register Connection
    await websocket.accept()

    async def send_callback(message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    state_manager.register_subscriber(send_callback)

    # Send initial full state sync
    await websocket.send_json({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("action") or data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "dispatch_card":
                card_data = data.get("card", {})
                assigned_agent = card_data.get("assigned_agent")
                if not assigned_agent or assigned_agent == "auto" or assigned_agent not in state_manager.agents:
                    query_text = f"{card_data.get('title', '')}. {card_data.get('description', '')}".strip()
                    triage_info = run_triage(query_text)
                    assigned_agent = triage_info["recommended_agent_id"]

                target_model = card_data.get("model") or state_manager.settings.get("agent_models", {}).get(
                    assigned_agent, "claude-3-7-sonnet-20250219"
                )

                can_dispatch, reason = provider_manager.can_dispatch_model(target_model)
                if not can_dispatch:
                    await websocket.send_json({
                        "type": "dispatch_rejected",
                        "error": f"Model gating rejected: {reason}"
                    })
                    continue

                card_id = f"card-{uuid.uuid4().hex[:8]}"
                proxy_token = create_agent_proxy_token(
                    agent_id=assigned_agent,
                    card_id=card_id,
                    allowed_model_id=target_model
                )

                await state_manager.add_card(
                    title=card_data.get("title", ""),
                    description=card_data.get("description", ""),
                    assigned_agent=assigned_agent,
                    dry_run=card_data.get("dry_run"),
                    model=target_model,
                    agent_proxy_token=proxy_token,
                    card_id=card_id
                )

            elif msg_type == "cancel_card":
                card_id = data.get("card_id")
                if card_id:
                    await state_manager.cancel_card(card_id)

            elif msg_type == "update_settings":
                settings_update = data.get("settings", {})
                state_manager.save_settings(settings_update)
                await state_manager.broadcast({
                    "type": "state_sync",
                    "data": state_manager.get_full_state()
                })

    except WebSocketDisconnect:
        pass
    finally:
        state_manager.unregister_subscriber(send_callback)
