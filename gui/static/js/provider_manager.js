/**
 * AI Provider Hub & Account Pool Manager (Fase 1 UI Controller).
 * Coordinates provider card accordions, accounts priority management,
 * live credentials verification probe, and secure key input.
 */

class ProviderManagerUI {
  constructor(containerId) {
    this.container = typeof containerId === "string" ? document.getElementById(containerId) : containerId;
    this.providersData = {};
    this.modelsData = [];
    this._bindGlobalEvents();
  }

  _bindGlobalEvents() {
    // Listen for state sync updates from WebSocket
    window.addEventListener("office_state_sync", (e) => {
      if (e.detail && e.detail.providers) {
        this.providersData = e.detail.providers;
        this.modelsData = e.detail.models_catalog || [];
        this.render();
      }
    });
  }

  async load() {
    try {
      const res = await fetch("/api/providers");
      if (res.ok) {
        const data = await res.json();
        this.providersData = data.providers || {};
        this.modelsData = data.models || [];
        this.render();
      }
    } catch (e) {
      console.error("[ProviderManager] Error loading providers:", e);
    }
  }

  render() {
    if (!this.container) return;
    this.container.innerHTML = "";

    const providerOrder = ["anthropic", "openai", "gemini", "antigravity"];
    const displayNames = {
      anthropic: "Anthropic Claude",
      openai: "OpenAI / Codex",
      gemini: "Google Gemini",
      antigravity: "Antigravity Desktop (Local)"
    };

    providerOrder.forEach((provName) => {
      const provConfig = this.providersData[provName] || { strategy: "priority", accounts: [] };
      const card = this._createProviderCard(provName, displayNames[provName] || provName, provConfig);
      this.container.appendChild(card);
    });
  }

  _createProviderCard(provName, displayName, config) {
    const card = document.createElement("div");
    card.className = "pixel-box provider-card";
    card.setAttribute("data-provider", provName);

    // Compute aggregate status
    const accounts = config.accounts || [];
    let aggStatus = "DISCONNECTED";
    let aggColor = "badge-red";

    const hasConnected = accounts.some(a => a.status === "CONNECTED" && a.enabled);
    const hasUnknown = accounts.some(a => a.status === "UNKNOWN" && a.enabled);

    if (hasConnected) {
      aggStatus = "CONNECTED";
      aggColor = "badge-green";
    } else if (hasUnknown) {
      aggStatus = "UNKNOWN";
      aggColor = "badge-amber";
    }

    card.innerHTML = `
      <div class="provider-header">
        <span class="provider-name">${displayName}</span>
        <span class="pixel-badge ${aggColor}" id="status-badge-${provName}">${aggStatus}</span>
        <div class="provider-strategy-selector">
          <label style="font-size: 8px; color: var(--text-dim);">STRATEGY:</label>
          <select class="pixel-select strategy-select" data-provider="${provName}" style="padding: 2px 4px; font-size: 8px; width: auto;">
            <option value="priority" ${config.strategy === "priority" ? "selected" : ""}>PRIORITY</option>
            <option value="round-robin" ${config.strategy === "round-robin" ? "selected" : ""}>ROUND-ROBIN</option>
            <option value="least-used" ${config.strategy === "least-used" ? "selected" : ""}>LEAST-USED</option>
          </select>
        </div>
      </div>

      <div class="account-list" id="account-list-${provName}">
        ${accounts.length === 0 ? `<div style="font-size: 8px; color: #7b889b; padding: 6px;">NO ACCOUNTS IN POOL. ADD ONE BELOW.</div>` : ""}
      </div>

      <div class="provider-actions">
        <button class="pixel-btn pixel-btn-primary add-account-btn" data-provider="${provName}" style="font-size: 8px; padding: 4px 8px;">
          + ADD ACCOUNT
        </button>
      </div>
    `;

    // Strategy change handler
    const strategySelect = card.querySelector(".strategy-select");
    strategySelect.addEventListener("change", async (e) => {
      const newStrategy = e.target.value;
      try {
        await fetch(`/api/providers/${provName}/strategy`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ strategy: newStrategy })
        });
        if (window.retroAudio) window.retroAudio.playBleep(480, 0.04);
      } catch (err) {}
    });

    // Add Account button handler
    const addBtn = card.querySelector(".add-account-btn");
    addBtn.addEventListener("click", () => this._showAddAccountModal(provName, displayName));

    // Render accounts
    const accountList = card.querySelector(`#account-list-${provName}`);
    accounts.forEach((acc) => {
      const accRow = this._createAccountRow(provName, acc);
      accountList.appendChild(accRow);
    });

    return card;
  }

  _createAccountRow(provName, acc) {
    const row = document.createElement("div");
    row.className = "account-item";

    let badgeClass = "badge-red";
    if (acc.status === "CONNECTED") badgeClass = "badge-green";
    else if (acc.status === "UNKNOWN") badgeClass = "badge-amber";
    else if (acc.status === "RATE_LIMITED") badgeClass = "badge-purple";

    row.innerHTML = `
      <div class="account-info">
        <span class="account-label">${acc.label || acc.id}</span>
        <span class="account-meta">P:${acc.priority} | ID: ${acc.id}</span>
      </div>
      <span class="pixel-badge ${badgeClass}" style="font-size: 7px;">${acc.status}</span>
      <div class="account-actions">
        <button class="pixel-btn verify-acc-btn" data-provider="${provName}" data-acc="${acc.id}" style="padding: 2px 6px; font-size: 7px;">
          VERIFY
        </button>
        <button class="pixel-btn pixel-btn-danger delete-acc-btn" data-provider="${provName}" data-acc="${acc.id}" style="padding: 2px 5px; font-size: 7px;">
          DEL
        </button>
      </div>
    `;

    // Verify handler
    const verifyBtn = row.querySelector(".verify-acc-btn");
    verifyBtn.addEventListener("click", async () => {
      verifyBtn.textContent = "PROBING...";
      try {
        const res = await fetch(`/api/providers/${provName}/accounts/${acc.id}/verify`, { method: "POST" });
        const result = await res.json();
        if (result.success) {
          if (window.retroAudio) window.retroAudio.playSuccess();
        } else {
          if (window.retroAudio) window.retroAudio.playAlert();
        }
        await this.load();
        if (window.modelDropdown) {
          const freshModels = await fetch("/api/providers").then(r => r.json());
          window.modelDropdown.setModels(freshModels.models);
        }
      } catch (err) {
        verifyBtn.textContent = "VERIFY";
      }
    });

    // Delete handler
    const deleteBtn = row.querySelector(".delete-acc-btn");
    deleteBtn.addEventListener("click", async () => {
      if (confirm(`Remove account '${acc.id}' and delete key from Windows Credential Manager?`)) {
        try {
          await fetch(`/api/providers/${provName}/accounts/${acc.id}`, { method: "DELETE" });
          if (window.retroAudio) window.retroAudio.playBleep(300, 0.08);
          await this.load();
        } catch (err) {}
      }
    });

    return row;
  }

  _showAddAccountModal(provName, displayName) {
    const modal = document.createElement("div");
    modal.className = "modal-overlay active";
    modal.style.zIndex = "10002";

    modal.innerHTML = `
      <div class="pixel-box" style="width: 360px; padding: 16px; background: var(--bg-panel);">
        <div class="section-header" style="margin-bottom: 12px;">
          <span>+ ADD ${displayName.toUpperCase()} ACCOUNT</span>
        </div>

        <div class="task-form-group">
          <label class="form-label">Account ID (Slug)</label>
          <input type="text" id="newAccId" class="pixel-input" placeholder="e.g. work-main" required>
        </div>

        <div class="task-form-group">
          <label class="form-label">Account Label</label>
          <input type="text" id="newAccLabel" class="pixel-input" placeholder="e.g. Production Key" required>
        </div>

        <div class="task-form-group">
          <label class="form-label">Priority (1 = Highest)</label>
          <input type="number" id="newAccPriority" min="1" max="10" value="1" class="pixel-input">
        </div>

        <div class="task-form-group">
          <label class="form-label">API Key / Token</label>
          <input type="password" id="newAccSecret" class="pixel-input" placeholder="Stored in Windows Credential Manager" autocomplete="off">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px;">
          <button class="pixel-btn" id="cancelAddAccBtn">CANCEL</button>
          <button class="pixel-btn pixel-btn-primary" id="saveAddAccBtn">SAVE ACCOUNT</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector("#cancelAddAccBtn").addEventListener("click", () => {
      document.body.removeChild(modal);
    });

    modal.querySelector("#saveAddAccBtn").addEventListener("click", async () => {
      const id = modal.querySelector("#newAccId").value.trim();
      const label = modal.querySelector("#newAccLabel").value.trim() || id;
      const priority = parseInt(modal.querySelector("#newAccPriority").value) || 1;
      const secret = modal.querySelector("#newAccSecret").value.trim();

      if (!id) {
        alert("Account ID is required.");
        return;
      }

      try {
        const res = await fetch(`/api/providers/${provName}/accounts`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: id,
            label: label,
            priority: priority,
            enabled: true,
            secret: secret || null
          })
        });

        if (res.ok) {
          if (window.retroAudio) window.retroAudio.playSuccess();
          document.body.removeChild(modal);
          await this.load();
        } else {
          const err = await res.json();
          alert(`Failed to add account: ${err.detail || 'Unknown error'}`);
        }
      } catch (e) {
        console.error("Error saving account:", e);
      }
    });
  }
}

window.ProviderManagerUI = ProviderManagerUI;
