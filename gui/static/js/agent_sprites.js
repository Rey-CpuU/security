/**
 * Procedural 8-Bit Pixel Character Sprite Renderer.
 * Generates crisp 16x20 retro pixel characters dynamically onto HTML5 Canvas.
 * Zero external sprite sheets or image files needed.
 */

class AgentSpriteRenderer {
  constructor() {
    this.pixelSize = 2; // 1 sprite pixel = 2 canvas pixels
  }

  drawAgent(ctx, agent, tick, isSelected = false) {
    const x = Math.round(agent.pos.x);
    const y = Math.round(agent.pos.y);
    const status = agent.status || "idle";
    const agentId = agent.id;

    ctx.save();
    ctx.translate(x, y);

    // 1. Draw Drop Shadow
    ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
    ctx.beginPath();
    ctx.ellipse(0, 8, 12, 5, 0, 0, Math.PI * 2);
    ctx.fill();

    // 2. Selection Indicator
    if (isSelected) {
      ctx.strokeStyle = "#00f0ff";
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 2]);
      ctx.strokeRect(-18, -28, 36, 42);
      ctx.setLineDash([]);
    }

    // 3. Animation Offsets
    let bobY = 0;
    let legOffset = 0;
    if (status === "idle") {
      bobY = Math.sin(tick * 0.08) > 0 ? 0 : 1;
    } else if (status === "walking") {
      bobY = Math.abs(Math.sin(tick * 0.25)) * 2;
      legOffset = Math.sin(tick * 0.25) > 0 ? 2 : -2;
    } else if (status === "working") {
      bobY = Math.sin(tick * 0.15) > 0 ? 0 : 1;
    } else if (status === "alert") {
      bobY = Math.sin(tick * 0.4) > 0 ? -3 : 0;
    }

    // 4. Draw Procedural Pixel Body
    this._renderPixelFigure(ctx, agentId, status, bobY, legOffset, tick);

    // 5. Draw Head Label / Name Tag
    ctx.font = "8px 'PressStart2P', monospace";
    ctx.textAlign = "center";
    ctx.fillStyle = agent.color || "#00ff66";
    ctx.fillText(agent.name, 0, -22 + bobY);

    // 6. Draw Status / Thought Bubble
    if (status === "alert") {
      this._drawAlertBubble(ctx, 0, -34 + bobY, tick);
    } else if (agent.current_thought && (status === "working" || status === "walking")) {
      this._drawThoughtBubble(ctx, 0, -32 + bobY, agent.current_thought);
    }

    ctx.restore();
  }

  _renderPixelFigure(ctx, agentId, status, bobY, legOffset, tick) {
    const p = this.pixelSize; // Scale multiplier (2px)

    // Palette per agent
    let hatColor = "#ff3366";
    let skinColor = "#ffd1a4";
    let clothesColor = "#222533";
    let accentColor = "#ff5577";

    if (agentId === "pentest") {
      hatColor = "#ff3366";    // Red bandana / hoodie
      clothesColor = "#1a1c23";
      accentColor = "#ff3366";
    } else if (agentId === "appsec") {
      hatColor = "#00f0ff";    // Cyan tech visor
      clothesColor = "#23334d";
      accentColor = "#00f0ff";
    } else if (agentId === "devsecops") {
      hatColor = "#00ff66";    // Green hardhat / goggles
      clothesColor = "#1b382b";
      accentColor = "#00ff66";
    }

    const drawPixel = (px, py, color) => {
      ctx.fillStyle = color;
      ctx.fillRect(px * p, py * p + bobY, p, p);
    };

    // --- LEGS / SHOES ---
    const legY = 2;
    drawPixel(-3, legY + legOffset, "#111");
    drawPixel(-2, legY + legOffset, "#111");
    drawPixel(1, legY - legOffset, "#111");
    drawPixel(2, legY - legOffset, "#111");

    // --- TORSO / CLOTHES ---
    for (let y = -4; y <= 1; y++) {
      for (let x = -3; x <= 3; x++) {
        drawPixel(x, y, clothesColor);
      }
    }
    // Accent stripe (badge/vest detail)
    drawPixel(0, -3, accentColor);
    drawPixel(0, -2, accentColor);

    // Hands / Working animation
    if (status === "working") {
      const handBob = Math.sin(tick * 0.3) > 0 ? 1 : 0;
      drawPixel(-4, -1 - handBob, skinColor);
      drawPixel(4, -1 + handBob, skinColor);
    } else {
      drawPixel(-4, 0, skinColor);
      drawPixel(4, 0, skinColor);
    }

    // --- HEAD / FACE ---
    for (let y = -8; y <= -5; y++) {
      for (let x = -3; x <= 3; x++) {
        drawPixel(x, y, skinColor);
      }
    }

    // Eyes / Glasses / Visor
    if (agentId === "pentest") {
      // Dark sunglasses
      drawPixel(-2, -6, "#000");
      drawPixel(-1, -6, "#000");
      drawPixel(1, -6, "#000");
      drawPixel(2, -6, "#000");
    } else if (agentId === "appsec") {
      // Glowing cyan visor
      drawPixel(-3, -6, "#00f0ff");
      drawPixel(-2, -6, "#00f0ff");
      drawPixel(-1, -6, "#00f0ff");
      drawPixel(0, -6, "#00f0ff");
      drawPixel(1, -6, "#00f0ff");
      drawPixel(2, -6, "#00f0ff");
    } else {
      // Green cyber goggles
      drawPixel(-2, -6, "#00ff66");
      drawPixel(2, -6, "#00ff66");
    }

    // --- HAT / HAIR ---
    for (let x = -3; x <= 3; x++) {
      drawPixel(x, -9, hatColor);
      drawPixel(x, -8, hatColor);
    }
  }

  _drawAlertBubble(ctx, x, y, tick) {
    const flash = Math.sin(tick * 0.3) > 0;
    ctx.fillStyle = flash ? "#ff3366" : "#ffffff";
    ctx.fillRect(x - 6, y - 8, 12, 12);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 1;
    ctx.strokeRect(x - 6, y - 8, 12, 12);

    ctx.fillStyle = flash ? "#ffffff" : "#ff3366";
    ctx.font = "9px 'PressStart2P', monospace";
    ctx.textAlign = "center";
    ctx.fillText("!", x, y + 2);
  }

  _drawThoughtBubble(ctx, x, y, text) {
    const snippet = text.length > 20 ? text.substring(0, 18) + ".." : text;
    ctx.font = "7px 'PressStart2P', monospace";
    const textWidth = ctx.measureText(snippet).width;
    const boxW = Math.max(textWidth + 12, 40);
    const boxH = 14;

    ctx.fillStyle = "#141721";
    ctx.fillRect(x - boxW / 2, y - boxH, boxW, boxH);
    ctx.strokeStyle = "#3b4252";
    ctx.lineWidth = 1;
    ctx.strokeRect(x - boxW / 2, y - boxH, boxW, boxH);

    ctx.fillStyle = "#eceff4";
    ctx.textAlign = "center";
    ctx.fillText(snippet, x, y - 4);
  }
}

window.agentSpriteRenderer = new AgentSpriteRenderer();
