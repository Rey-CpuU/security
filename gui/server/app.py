"""
FastAPI Application Server for 8-Bit Cyber Operations Office GUI.
Provides RESTful management APIs, secure static asset hosting,
and authenticated WebSocket real-time event streaming.
"""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gui.server.security import (
    verify_origin,
    verify_session_token,
    verify_websocket_handshake,
    get_session_token,
    reset_session_token
)
from gui.server.state import state_manager
from gui.server.triage_bridge import run_triage

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="Security Team 8-Bit Cyber Operations Office",
    description="Local secure GUI for orchestrating multi-harness security agents",
    version="1.0.0"
)

# Mount static asset directory
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateCardRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    assigned_agent: Optional[str] = None
    dry_run: Optional[bool] = None


class TriageRequest(BaseModel):
    query: str


class SettingsUpdateRequest(BaseModel):
    default_harness: Optional[str] = None
    dry_run_default: Optional[bool] = None
    max_parallel_agents: Optional[int] = None
    agent_models: Optional[Dict[str, Any]] = None


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
    # If origin is provided, strictly verify it
    if origin and not verify_origin(origin, port=request_port):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Untrusted Origin"
        )
    return {"token": get_session_token()}


@app.get("/api/state")
async def get_office_state():
    """
    Return complete office, agent, queue, and settings snapshot.
    """
    return state_manager.get_full_state()


@app.post("/api/cards")
async def create_card(card_req: CreateCardRequest):
    """
    Submit a task card for automated triage and office agent execution.
    """
    card = await state_manager.add_card(
        title=card_req.title,
        description=card_req.description or "",
        assigned_agent=card_req.assigned_agent,
        dry_run=card_req.dry_run
    )
    return card


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
    Update settings (models, dry-run safety default, concurrency limits).
    """
    payload = req.model_dump(exclude_unset=True)
    updated = state_manager.save_settings(payload)
    await state_manager.broadcast({
        "type": "state_sync",
        "data": state_manager.get_full_state()
    })
    return updated


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    Authenticated real-time WebSocket connection.
    Guards against Cross-Site WebSocket Hijacking (CSWSH) via Origin & Token validation.
    """
    request_port = websocket.url.port or int(os.environ.get("PORT", "8888"))
    # 1. Security Handshake Check
    origin = websocket.headers.get("origin")
    if not verify_origin(origin, port=request_port):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Untrusted Origin")
        return

    if not verify_session_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid Session Token")
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
                await state_manager.add_card(
                    title=card_data.get("title", ""),
                    description=card_data.get("description", ""),
                    assigned_agent=card_data.get("assigned_agent"),
                    dry_run=card_data.get("dry_run")
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
