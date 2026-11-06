/**
 * Task Card Dispatcher & Queue Manager.
 * Orchestrates task card creation, autonomous triage recommendations,
 * card list rendering, and task cancellation.
 */

class TaskCardsManager {
  constructor() {
    this.cards = [];
    this.queue = [];
    this.selectedCardId = null;

    this.titleInput = document.getElementById("taskTitleInput");
    this.descInput = document.getElementById("taskDescInput");
    this.agentSelect = document.getElementById("taskAgentSelect");
    this.dryRunCheckbox = document.getElementById("dryRunCheckbox");
    this.dispatchBtn = document.getElementById("dispatchTaskBtn");
    this.triagePreviewBadge = document.getElementById("triagePreviewBadge");
    this.queueContainer = document.getElementById("queueListContainer");

    this._bindEvents();
  }

  _bindEvents() {
    if (this.dispatchBtn) {
      this.dispatchBtn.addEventListener("click", () => this.dispatchCard());
    }

    if (this.titleInput) {
      // Debounced triage preview as user types
      let debounceTimer = null;
      this.titleInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => this.previewTriage(), 400);
      });

      this.titleInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.dispatchCard();
        }
      });
    }
  }

  async previewTriage() {
    const text = (this.titleInput ? this.titleInput.value : "").trim();
    if (!text || text.length < 4) {
      if (this.triagePreviewBadge) {
        this.triagePreviewBadge.textContent = "AUTONOMOUS TRIAGE: READY";
        this.triagePreviewBadge.className = "pixel-badge badge-green";
      }
      return;
    }

    try {
      const res = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
      });
      if (res.ok) {
        const data = await res.json();
        const role = data.recommended_role || "Security Specialist";
        const agent = data.recommended_agent_id ? data.recommended_agent_id.toUpperCase() : "AUTO";
        if (this.triagePreviewBadge) {
          this.triagePreviewBadge.textContent = `ROUTE: ${agent} (${role})`;
          this.triagePreviewBadge.className = "pixel-badge badge-cyan";
        }
        if (window.terminalHud) {
          window.terminalHud.updateTriageView(data);
        }
      }
    } catch (e) {}
  }

  async dispatchCard() {
    const title = (this.titleInput ? this.titleInput.value : "").trim();
    const desc = (this.descInput ? this.descInput.value : "").trim();
    const assignedAgent = this.agentSelect ? this.agentSelect.value : "auto";
    const dryRun = this.dryRunCheckbox ? this.dryRunCheckbox.checked : true;

    if (!title) {
      if (this.titleInput) {
        this.titleInput.style.borderColor = "#ff3366";
        setTimeout(() => { this.titleInput.style.borderColor = ""; }, 1000);
      }
      return;
    }

    if (window.retroAudio) {
      window.retroAudio.playCoin();
    }

    const selectedModel = (window.modelDropdown && typeof window.modelDropdown.getValue === "function") 
      ? window.modelDropdown.getValue() 
      : null;

    const payload = {
      title: title,
      description: desc,
      assigned_agent: assignedAgent === "auto" ? null : assignedAgent,
      dry_run: dryRun,
      model: selectedModel || undefined
    };

    // Use WebSocket client if connected, otherwise fallback to REST
    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send({
        action: "dispatch_card",
        card: payload
      });
    } else {
      try {
        const res = await fetch("/api/cards", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) {
          const err = await res.json();
          if (window.retroAudio) window.retroAudio.playAlert();
          alert(`Dispatch Rejected: ${err.detail || 'Model gating blocked'}`);
          return;
        }
      } catch (e) {
        console.error("Failed to post card:", e);
      }
    }

    // Reset inputs
    if (this.titleInput) this.titleInput.value = "";
    if (this.descInput) this.descInput.value = "";
    if (this.triagePreviewBadge) {
      this.triagePreviewBadge.textContent = "AUTONOMOUS TRIAGE: READY";
      this.triagePreviewBadge.className = "pixel-badge badge-green";
    }
  }

  updateCards(cards, queue) {
    this.cards = cards || [];
    this.queue = queue || [];
    this.renderQueue();
  }

  renderQueue() {
    if (!this.queueContainer) return;
    this.queueContainer.innerHTML = "";

    if (this.cards.length === 0) {
      this.queueContainer.innerHTML = `<div style="color: #7b889b; font-size: 8px; text-align: center; padding: 12px;">NO ACTIVE TASK CARDS. DISPATCH ONE ABOVE.</div>`;
      return;
    }

    // Sort: running first, queued second, completed/failed last
    const sorted = [...this.cards].sort((a, b) => {
      const order = { running: 0, assigned: 1, queued: 2, alert: 3, completed: 4, failed: 5, cancelled: 6 };
      return (order[a.status] || 9) - (order[b.status] || 9);
    });

    sorted.forEach((card) => {
      const div = document.createElement("div");
      div.className = "task-card-item";
      if (card.id === this.selectedCardId) {
        div.style.borderColor = "var(--neon-cyan)";
      }

      let badgeClass = "badge-amber";
      if (card.status === "running") badgeClass = "badge-green";
      else if (card.status === "completed") badgeClass = "badge-cyan";
      else if (card.status === "failed") badgeClass = "badge-red";
      else if (card.status === "cancelled") badgeClass = "badge-purple";

      const modeBadge = card.dry_run ? `<span class="pixel-badge badge-green">DRY-RUN</span>` : `<span class="pixel-badge badge-red">LIVE</span>`;
      const agentLabel = card.assigned_agent ? card.assigned_agent.toUpperCase() : "TRIAGING";

      div.innerHTML = `
        <div class="card-item-header">
          <span class="card-title">${this._escape(card.title)}</span>
          <span class="pixel-badge ${badgeClass}">${card.status}</span>
        </div>
        <div class="card-meta">
          <span>OPERATIVE: ${agentLabel}</span>
          ${modeBadge}
          ${card.status === "running" || card.status === "queued" ? 
            `<button class="pixel-btn pixel-btn-danger" style="padding: 2px 5px; font-size: 7px; margin-left: auto;" onclick="window.taskCardsManager.cancelCard('${card.id}', event)">STOP</button>` 
            : ""}
        </div>
      `;

      div.addEventListener("click", () => {
        this.selectedCardId = card.id;
        if (window.retroAudio) window.retroAudio.playBleep(480, 0.04);
        this.renderQueue();
        if (window.terminalHud) {
          window.terminalHud.displayCardLogs(card);
        }
      });

      this.queueContainer.appendChild(div);
    });
  }

  async cancelCard(cardId, event) {
    if (event) event.stopPropagation();
    if (window.retroAudio) window.retroAudio.playBleep(300, 0.08);

    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send({
        action: "cancel_card",
        card_id: cardId
      });
    } else {
      try {
        await fetch(`/api/cards/${cardId}/cancel`, { method: "POST" });
      } catch (e) {}
    }
  }

  _escape(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.taskCardsManager = new TaskCardsManager();
});
