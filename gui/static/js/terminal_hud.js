/**
 * Retro CRT Terminal HUD & Agent Inspector.
 * Renders real-time thought streams, tool calls, triage reports,
 * and agent specifications in authentic phosphor green styling.
 */

class TerminalHud {
  constructor() {
    this.screen = document.getElementById("terminalScreen");
    this.tabButtons = document.querySelectorAll(".tab-btn");
    this.currentTab = "terminal";
    this.autoScroll = true;
    this.selectedAgentId = "pentest";
    this.latestState = null;

    this._bindTabs();
  }

  _bindTabs() {
    this.tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.getAttribute("data-tab");
        this.switchTab(tab);
        if (window.retroAudio) window.retroAudio.playBleep(580, 0.04);
      });
    });
  }

  switchTab(tabName) {
    this.currentTab = tabName;
    this.tabButtons.forEach((b) => {
      if (b.getAttribute("data-tab") === tabName) {
        b.classList.add("active");
      } else {
        b.classList.remove("active");
      }
    });

    if (tabName === "terminal") {
      this.renderTerminalView();
    } else if (tabName === "triage") {
      this.renderTriageView();
    } else if (tabName === "agent") {
      this.renderAgentSpecsView();
    }
  }

  appendLogChunk(chunk) {
    if (!this.screen) return;

    const timeStr = new Date(chunk.timestamp ? chunk.timestamp * 1000 : Date.now()).toLocaleTimeString();
    const type = chunk.type || "thought";
    const agentName = chunk.agent_name || chunk.agent_id || "SYSTEM";
    let cssClass = "log-thought";

    if (type === "tool_call") cssClass = "log-tool";
    else if (type === "output") cssClass = "log-output";
    else if (type === "alert") cssClass = "log-alert";
    else if (type === "status") cssClass = "log-status";

    const line = document.createElement("div");
    line.className = cssClass;
    line.innerHTML = `[${timeStr}] [${agentName.toUpperCase()}] &gt; ${this._escape(chunk.content)}`;

    if (this.currentTab === "terminal") {
      this.screen.appendChild(line);
      if (this.autoScroll) {
        this.screen.scrollTop = this.screen.scrollHeight;
      }
    }
  }

  displayCardLogs(card) {
    this.switchTab("terminal");
    if (!this.screen) return;
    this.screen.innerHTML = "";

    const header = document.createElement("div");
    header.style.color = "var(--neon-cyan)";
    header.style.marginBottom = "8px";
    header.innerHTML = `=== LOG AUDIT: [${card.id}] "${this._escape(card.title)}" ===\nMODE: ${card.dry_run ? "DRY-RUN (SIMULATED)" : "LIVE"} | AGENT: ${card.assigned_agent || "AUTO"}`;
    this.screen.appendChild(header);

    if (card.logs && card.logs.length > 0) {
      card.logs.forEach((log) => this.appendLogChunk(log));
    } else {
      const empty = document.createElement("div");
      empty.style.color = "var(--text-dim)";
      empty.textContent = "No log stream recorded for this card yet.";
      this.screen.appendChild(empty);
    }
  }

  updateTriageView(triageData) {
    this.lastTriageData = triageData;
    if (this.currentTab === "triage") {
      this.renderTriageView();
    }
  }

  renderTriageView() {
    if (!this.screen) return;
    this.screen.innerHTML = "";

    const data = this.lastTriageData;
    if (!data) {
      this.screen.innerHTML = `<div style="color: #7b889b;">NO TRIAGE DATA RECORDED YET. TYPE A TASK IN THE DISPATCHER FORM TO RUN REAL-TIME TRIAGE.</div>`;
      return;
    }

    const html = `
<div style="color: var(--neon-cyan); margin-bottom: 8px;">🛡️ SECURITY TEAM TRIAGE REPORT (v2.1.1)</div>
<div style="color: #fff;">Query: "${this._escape(data.query)}"</div>
<div style="color: var(--neon-green); margin-top: 6px;">Lead Role: ${data.recommended_role}</div>
${data.secondary_role ? `<div style="color: var(--neon-amber);">Support Role: ${data.secondary_role}</div>` : ""}

<div style="color: var(--neon-cyan); margin-top: 10px;">📦 Primary Skills Activated:</div>
${(data.primary_skills || []).map(s => `<div style="color: #eceff4; padding-left: 12px;">• ${s}</div>`).join("")}

${data.secondary_skills && data.secondary_skills.length > 0 ? `
<div style="color: var(--neon-amber); margin-top: 8px;">🤝 Supporting Skills:</div>
${data.secondary_skills.map(s => `<div style="color: #eceff4; padding-left: 12px;">• ${s}</div>`).join("")}
` : ""}
`;
    this.screen.innerHTML = html;
  }

  selectAgent(agentId) {
    this.selectedAgentId = agentId;
    this.switchTab("agent");
  }

  renderAgentSpecsView() {
    if (!this.screen) return;
    this.screen.innerHTML = "";

    const state = this.latestState || (window.officeCanvas ? window.officeCanvas.state : null);
    if (!state || !state.agents) {
      this.screen.innerHTML = `<div style="color: #7b889b;">AWAITING OFFICE AGENT TELEMETRY...</div>`;
      return;
    }

    const agent = state.agents[this.selectedAgentId] || Object.values(state.agents)[0];
    if (!agent) return;

    const html = `
<div style="color: ${agent.color}; font-size: 11px; margin-bottom: 6px;">[OPERATIVE PROFILE: ${agent.name.toUpperCase()}]</div>
<div style="color: #eceff4; line-height: 1.6;">
  <div>ROLE        : ${agent.role}</div>
  <div>TITLE       : ${agent.title}</div>
  <div>STATUS      : <span style="color: var(--neon-green); font-weight: bold;">${agent.status.toUpperCase()}</span></div>
  <div>ACTIVE MODEL: <span style="color: var(--neon-amber);">${agent.model || "Default"}</span></div>
  <div>HARNESS     : ${agent.harness}</div>
  <div>DESK COORD  : (${agent.desk.x}, ${agent.desk.y})</div>
  <div style="margin-top: 8px; color: var(--neon-cyan);">CURRENT THOUGHT:</div>
  <div style="color: #88c0d0; padding-left: 10px; font-style: italic;">"${this._escape(agent.current_thought || 'Standing by.')}"</div>
</div>
<div style="margin-top: 14px;">
  <button class="pixel-btn pixel-btn-primary" onclick="window.settingsModal.open()">CONFIGURE AGENT MODEL</button>
</div>
`;
    this.screen.innerHTML = html;
  }

  renderTerminalView() {
    // If empty, put default system message
    if (!this.screen || this.screen.children.length === 0) {
      this.screen.innerHTML = `<div style="color: var(--neon-green);">[8-BIT CYBER OFFICE HUD INITIALIZED. AWAITING HARNESS STREAM...]</div>`;
    }
  }

  updateState(state) {
    this.latestState = state;
    if (this.currentTab === "agent") {
      this.renderAgentSpecsView();
    }
  }

  clear() {
    if (this.screen) this.screen.innerHTML = "";
  }

  _escape(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.terminalHud = new TerminalHud();
});
