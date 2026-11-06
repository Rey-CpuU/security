/**
 * Secure WebSocket Client for 8-Bit Cyber Operations Office GUI.
 * Manages authenticated duplex streaming with session token & Anti-CSWSH guards.
 */

class OfficeWebSocketClient {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 20;
    this.token = this._resolveSessionToken();
    this.statusDot = document.getElementById("connectionStatusDot");
    this.statusText = document.getElementById("connectionStatusText");

    this._connect();
  }

  _resolveSessionToken() {
    // 1. Check window global injected by server
    if (window.__SESSION_TOKEN && window.__SESSION_TOKEN !== "__SESSION_TOKEN__") {
      return window.__SESSION_TOKEN;
    }
    // 2. Check meta tag
    const meta = document.querySelector('meta[name="session-token"]');
    if (meta && meta.content && meta.content !== "__SESSION_TOKEN__") {
      return meta.content;
    }
    // 3. Check URL query params
    const params = new URLSearchParams(window.location.search);
    if (params.get("token")) {
      return params.get("token");
    }
    return "";
  }

  async _ensureToken() {
    if (!this.token) {
      try {
        const res = await fetch("/api/auth/token");
        if (res.ok) {
          const data = await res.json();
          this.token = data.token;
        }
      } catch (e) {
        console.warn("Could not fetch session token:", e);
      }
    }
    return this.token;
  }

  async _connect() {
    await this._ensureToken();

    const loc = window.location;
    const protocol = loc.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${loc.host}/ws?token=${encodeURIComponent(this.token)}`;

    this._updateUIStatus("CONNECTING...", "#ffb000");

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this._updateUIStatus(`CONNECTED (${loc.host})`, "#00ff66");
        console.log("[WS] Authenticated connection established.");

        // Start ping heartbeat
        if (this.pingInterval) clearInterval(this.pingInterval);
        this.pingInterval = setInterval(() => {
          if (this.isConnected) this.send({ type: "ping" });
        }, 25000);
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this._handleMessage(msg);
        } catch (e) {
          console.error("[WS] Error parsing JSON event:", e);
        }
      };

      this.ws.onclose = (event) => {
        this.isConnected = false;
        this._updateUIStatus("DISCONNECTED", "#ff3366");
        console.warn(`[WS] Connection closed (code: ${event.code}, reason: ${event.reason})`);
        this._scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        this.isConnected = false;
        console.error("[WS] Socket error:", err);
      };

    } catch (e) {
      this._scheduleReconnect();
    }
  }

  _scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
      console.log(`[WS] Reconnecting in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts})...`);
      setTimeout(() => this._connect(), delay);
    }
  }

  _updateUIStatus(text, color) {
    if (this.statusText) this.statusText.textContent = text;
    if (this.statusDot) {
      this.statusDot.style.background = color;
      this.statusDot.style.boxShadow = `0 0 6px ${color}`;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  _handleMessage(msg) {
    const type = msg.type;

    // SFX playback
    if (msg.sfx && window.retroAudio) {
      if (msg.sfx === "coin") window.retroAudio.playCoin();
      else if (msg.sfx === "alert") window.retroAudio.playAlert();
      else if (msg.sfx === "typewriter") window.retroAudio.playTypewriter();
      else if (msg.sfx === "success") window.retroAudio.playSuccess();
      else if (msg.sfx === "bleep") window.retroAudio.playBleep();
    }

    if (type === "state_sync") {
      const data = msg.data;
      if (window.officeCanvas) window.officeCanvas.setState(data);
      if (window.taskCardsManager) window.taskCardsManager.updateCards(data.cards, data.queue);
      if (window.terminalHud) window.terminalHud.updateState(data);

      const workerBadge = document.getElementById("activeWorkersBadge");
      if (workerBadge) {
        workerBadge.textContent = `ACTIVE: ${data.active_workers_count || 0} / ${data.settings?.max_parallel_agents || 2}`;
      }

    } else if (type === "terminal_log") {
      if (window.terminalHud) {
        window.terminalHud.appendLogChunk(msg.chunk);
      }

    } else if (type === "agent_moved") {
      if (window.officeCanvas && window.officeCanvas.state && window.officeCanvas.state.agents) {
        const agent = window.officeCanvas.state.agents[msg.agent_id];
        if (agent) {
          agent.pos = msg.pos;
          agent.status = msg.status;
          agent.current_thought = msg.thought;
        }
      }

    } else if (type === "card_added" || type === "card_pickup" || type === "card_completed" || type === "card_cancelled") {
      // Periodic or next sync will reflect card state
      // If full card included, update queue
      if (msg.card && window.taskCardsManager) {
        // Optimistic refresh
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.wsClient = new OfficeWebSocketClient();
});
