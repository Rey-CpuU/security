/**
 * 8-Bit Cyber Operations Office Canvas Engine.
 * Renders the 2D pixel-art office environment, workstations,
 * server racks, task dispenser desk, and agent animations.
 */

class OfficeCanvas {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    
    // Internal virtual resolution (crisp 640x480)
    this.width = 640;
    this.height = 480;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    this.tick = 0;
    this.selectedAgentId = "pentest";
    this.state = null;

    this._bindEvents();
    this._startLoop();
  }

  setState(newState) {
    this.state = newState;
  }

  _bindEvents() {
    this.canvas.addEventListener("click", (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      const mouseX = (e.clientX - rect.left) * scaleX;
      const mouseY = (e.clientY - rect.top) * scaleY;

      // Check if user clicked on an agent
      if (this.state && this.state.agents) {
        for (const [id, agent] of Object.entries(this.state.agents)) {
          const dx = mouseX - agent.pos.x;
          const dy = mouseY - agent.pos.y;
          if (Math.abs(dx) <= 24 && Math.abs(dy) <= 30) {
            this.selectedAgentId = id;
            if (window.retroAudio) window.retroAudio.playBleep(520, 0.05);
            if (window.terminalHud) window.terminalHud.selectAgent(id);
            const selectElem = document.getElementById("taskAgentSelect");
            if (selectElem) selectElem.value = id;
            return;
          }
        }
      }

      // Check if user clicked on task dispenser desk
      const dispenser = { x: 280, y: 320 };
      if (Math.abs(mouseX - dispenser.x) < 40 && Math.abs(mouseY - dispenser.y) < 30) {
        const titleInput = document.getElementById("taskTitleInput");
        if (titleInput) titleInput.focus();
        if (window.retroAudio) window.retroAudio.playBleep(660, 0.06);
      }
    });
  }

  _startLoop() {
    const render = () => {
      this.tick++;
      this._draw();
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  }

  _draw() {
    const ctx = this.ctx;
    ctx.imageSmoothingEnabled = false;

    // 1. Draw Office Floor Grid
    this._drawFloor(ctx);

    // 2. Draw Server Racks & Top Wall
    this._drawTopWall(ctx);

    // 3. Draw CISO Meeting Table
    this._drawMeetingArea(ctx);

    // 4. Draw 3 Agent Workstations
    this._drawWorkstation(ctx, 120, 140, "PENTEST LAB", "#ff3366");
    this._drawWorkstation(ctx, 280, 140, "APPSEC AUDIT", "#00f0ff");
    this._drawWorkstation(ctx, 440, 140, "DEVSECOPS OPS", "#00ff66");

    // 5. Draw Task Dispenser Station
    this._drawDispenserStation(ctx, 280, 320);

    // 6. Draw Agents with smooth walking interpolation
    if (this.state && this.state.agents) {
      for (const [id, agent] of Object.entries(this.state.agents)) {
        if (!agent.renderPos) {
          agent.renderPos = { x: agent.pos.x, y: agent.pos.y };
        }
        const targetX = agent.pos.x;
        const targetY = agent.pos.y;
        const dx = targetX - agent.renderPos.x;
        const dy = targetY - agent.renderPos.y;
        const dist = Math.hypot(dx, dy);
        if (dist > 2) {
          const speed = 4;
          agent.renderPos.x += (dx / dist) * Math.min(dist, speed);
          agent.renderPos.y += (dy / dist) * Math.min(dist, speed);
        } else {
          agent.renderPos.x = targetX;
          agent.renderPos.y = targetY;
        }

        const isSelected = (id === this.selectedAgentId);
        const displayAgent = Object.assign({}, agent, { pos: agent.renderPos });
        window.agentSpriteRenderer.drawAgent(ctx, displayAgent, this.tick, isSelected);
      }
    }
  }

  _drawFloor(ctx) {
    const tileSize = 32;
    for (let y = 0; y < this.height; y += tileSize) {
      for (let x = 0; x < this.width; x += tileSize) {
        const alt = ((x / tileSize) + (y / tileSize)) % 2 === 0;
        ctx.fillStyle = alt ? "#121520" : "#0e111a";
        ctx.fillRect(x, y, tileSize, tileSize);

        // Subtle tile grid lines
        ctx.strokeStyle = "#171c2b";
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, tileSize, tileSize);
      }
    }
  }

  _drawTopWall(ctx) {
    // Wall Header
    ctx.fillStyle = "#07090e";
    ctx.fillRect(0, 0, this.width, 42);
    ctx.fillStyle = "#1e2638";
    ctx.fillRect(0, 40, this.width, 3);

    // Server Racks on Left & Right
    this._drawServerRack(ctx, 20, 4);
    this._drawServerRack(ctx, 50, 4);
    this._drawServerRack(ctx, 560, 4);
    this._drawServerRack(ctx, 590, 4);
  }

  _drawServerRack(ctx, x, y) {
    ctx.fillStyle = "#161b26";
    ctx.fillRect(x, y, 24, 32);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, 24, 32);

    // Blinking LED status lights
    for (let row = 0; row < 4; row++) {
      const ledY = y + 4 + row * 7;
      const blink1 = Math.sin(this.tick * 0.1 + row) > 0;
      const blink2 = Math.cos(this.tick * 0.15 + row) > 0;

      ctx.fillStyle = blink1 ? "#00ff66" : "#003311";
      ctx.fillRect(x + 4, ledY, 3, 3);

      ctx.fillStyle = blink2 ? "#00f0ff" : "#002233";
      ctx.fillRect(x + 10, ledY, 3, 3);

      ctx.fillStyle = (this.tick % 40 < 20) ? "#ffb000" : "#332200";
      ctx.fillRect(x + 16, ledY, 3, 3);
    }
  }

  _drawMeetingArea(ctx) {
    const cx = 280;
    const cy = 20;

    // Display Monitor Banner
    ctx.fillStyle = "#141926";
    ctx.fillRect(cx - 70, cy - 12, 140, 20);
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 2;
    ctx.strokeRect(cx - 70, cy - 12, 140, 20);

    ctx.font = "8px 'PressStart2P', monospace";
    ctx.fillStyle = "#00f0ff";
    ctx.textAlign = "center";
    ctx.fillText("CISO OPERATIONS DECK", cx, cy + 1);
  }

  _drawWorkstation(ctx, x, y, label, accentColor) {
    // Desk surface
    ctx.fillStyle = "#222736";
    ctx.fillRect(x - 36, y - 8, 72, 34);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.strokeRect(x - 36, y - 8, 72, 34);

    // Accent line
    ctx.fillStyle = accentColor;
    ctx.fillRect(x - 34, y - 6, 68, 2);

    // Dual CRT Monitors
    this._drawMonitor(ctx, x - 22, y - 24, accentColor);
    this._drawMonitor(ctx, x + 10, y - 24, accentColor);

    // Keyboard & Mouse Pad
    ctx.fillStyle = "#11141c";
    ctx.fillRect(x - 14, y + 6, 28, 10);
    ctx.fillStyle = "#4c566a";
    ctx.fillRect(x + 18, y + 8, 6, 8);

    // Coffee mug
    ctx.fillStyle = "#eceff4";
    ctx.fillRect(x - 30, y + 8, 6, 7);

    // Desk Sign Label
    ctx.font = "6px 'PressStart2P', monospace";
    ctx.fillStyle = accentColor;
    ctx.textAlign = "center";
    ctx.fillText(label, x, y + 36);
  }

  _drawMonitor(ctx, mx, my, glowColor) {
    // Monitor Frame
    ctx.fillStyle = "#12151f";
    ctx.fillRect(mx, my, 22, 16);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 1;
    ctx.strokeRect(mx, my, 22, 16);

    // Stand
    ctx.fillStyle = "#222";
    ctx.fillRect(mx + 8, my + 16, 6, 4);

    // Screen with blinking code matrix
    ctx.fillStyle = "#050811";
    ctx.fillRect(mx + 2, my + 2, 18, 12);

    // Matrix lines
    ctx.fillStyle = glowColor;
    const scanOffset = (this.tick % 30) / 10;
    ctx.fillRect(mx + 4, my + 4 + scanOffset, 12, 1);
    ctx.fillRect(mx + 4, my + 7, 8, 1);
    ctx.fillRect(mx + 4, my + 10, 14, 1);
  }

  _drawDispenserStation(ctx, x, y) {
    // Dispenser Table
    ctx.fillStyle = "#2c2214";
    ctx.fillRect(x - 50, y - 10, 100, 36);
    ctx.strokeStyle = "#ffb000";
    ctx.lineWidth = 2;
    ctx.strokeRect(x - 50, y - 10, 100, 36);

    // Header Sign
    const flash = Math.sin(this.tick * 0.1) > 0;
    ctx.font = "7px 'PressStart2P', monospace";
    ctx.fillStyle = flash ? "#ffb000" : "#ffe066";
    ctx.textAlign = "center";
    ctx.fillText("TASK DISPENSER / INBOX", x, y - 16);

    // Tray Slot
    ctx.fillStyle = "#0d0a06";
    ctx.fillRect(x - 36, y, 72, 18);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 1;
    ctx.strokeRect(x - 36, y, 72, 18);

    // Draw stacked cards if items in queue
    const queueLen = (this.state && this.state.queue) ? this.state.queue.length : 0;
    if (queueLen > 0) {
      const cardCount = Math.min(queueLen, 5);
      for (let i = 0; i < cardCount; i++) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x - 20 + i * 4, y + 3 - i * 2, 28, 10);
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1;
        ctx.strokeRect(x - 20 + i * 4, y + 3 - i * 2, 28, 10);
      }
      ctx.font = "6px 'PressStart2P', monospace";
      ctx.fillStyle = "#ff3366";
      ctx.fillText(`${queueLen} QUEUED`, x, y + 36);
    } else {
      ctx.font = "6px 'PressStart2P', monospace";
      ctx.fillStyle = "#7b889b";
      ctx.fillText("READY FOR TASKS", x, y + 36);
    }
  }
}

// Initialized on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.officeCanvas = new OfficeCanvas("officeCanvas");
});
