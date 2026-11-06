/**
 * 8-Bit ARIA Compliant Custom Combobox & Model Gating Dropdown.
 * Enforces keyboard navigation, live status gating, grayed-out disabled models
 * with lock icons & tooltips, and inline "Connect" action triggers.
 */

class RetroCustomDropdown {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === "string" ? document.getElementById(containerId) : containerId;
    this.options = options;
    this.models = [];
    this.selectedModelId = options.initialValue || null;
    this.isOpen = false;
    this.focusedIndex = -1;
    this.onChange = options.onChange || null;

    if (this.container) {
      this._initDOM();
      this._bindEvents();
    }
  }

  _initDOM() {
    this.container.classList.add("pixel-combobox-wrapper");
    this.container.innerHTML = `
      <div class="pixel-combobox" role="combobox" aria-haspopup="listbox" aria-expanded="false" tabindex="0">
        <div class="pixel-combobox-trigger">
          <span class="combobox-status-dot"></span>
          <span class="combobox-selected-text">SELECT AI MODEL...</span>
          <span class="combobox-caret">&#9660;</span>
        </div>
        <div class="pixel-combobox-dropdown" role="listbox" tabindex="-1">
          <!-- Options rendered dynamically -->
        </div>
      </div>
    `;

    this.combobox = this.container.querySelector(".pixel-combobox");
    this.trigger = this.container.querySelector(".pixel-combobox-trigger");
    this.selectedText = this.container.querySelector(".combobox-selected-text");
    this.statusDot = this.container.querySelector(".combobox-status-dot");
    this.dropdown = this.container.querySelector(".pixel-combobox-dropdown");
  }

  _bindEvents() {
    this.trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      this.toggle();
    });

    this.combobox.addEventListener("keydown", (e) => this._handleKeyDown(e));

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (!this.container.contains(e.target) && this.isOpen) {
        this.close();
      }
    });
  }

  setModels(modelsList) {
    this.models = modelsList || [];
    this.render();
  }

  render() {
    if (!this.dropdown) return;
    this.dropdown.innerHTML = "";

    if (this.models.length === 0) {
      this.dropdown.innerHTML = `<div class="pixel-option disabled" style="padding: 10px; font-size: 8px;">NO MODELS REGISTERED</div>`;
      return;
    }

    this.models.forEach((m, idx) => {
      const opt = document.createElement("div");
      opt.className = "pixel-option";
      opt.setAttribute("role", "option");
      opt.setAttribute("data-id", m.id);
      opt.setAttribute("tabindex", "-1");

      const isAvailable = m.is_available !== false;
      const isSelected = m.id === this.selectedModelId;

      if (isSelected) {
        opt.classList.add("selected");
        opt.setAttribute("aria-selected", "true");
      } else {
        opt.setAttribute("aria-selected", "false");
      }

      if (!isAvailable) {
        opt.classList.add("disabled");
        opt.setAttribute("aria-disabled", "true");
      }

      // Status indicator color
      let dotColor = "#00ff66";
      if (!isAvailable) {
        dotColor = m.provider_status === "RATE_LIMITED" ? "#ffb000" : "#ff3366";
      }

      const lockBadge = !isAvailable ? `<span class="pixel-lock-badge" title="${m.disabled_reason || 'Model unavailable'}">🔒</span>` : "";
      const reasonTooltip = !isAvailable && m.disabled_reason ? `<span class="pixel-option-tooltip">${m.disabled_reason}</span>` : "";
      
      const connectBtn = !isAvailable ? `
        <button class="pixel-btn pixel-btn-connect" title="Configure provider" data-provider="${m.provider || ''}">CONNECT</button>
      ` : "";

      opt.innerHTML = `
        <div class="option-main-row">
          <span class="option-dot" style="background: ${dotColor};"></span>
          <span class="option-name">${m.name || m.id}</span>
          <span class="pixel-badge badge-tier">${m.tier || 'standard'}</span>
          ${lockBadge}
          ${connectBtn}
        </div>
        ${reasonTooltip}
      `;

      // Connect button click handler
      const btn = opt.querySelector(".pixel-btn-connect");
      if (btn) {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          this.close();
          if (window.settingsModal && typeof window.settingsModal.openProviderTab === "function") {
            window.settingsModal.openProviderTab(m.provider);
          } else if (window.settingsModal) {
            window.settingsModal.open();
          }
        });
      }

      // Option click selection
      opt.addEventListener("click", (e) => {
        if (!isAvailable) {
          // Play reject bleep
          if (window.retroAudio) window.retroAudio.playBleep(240, 0.08);
          return;
        }
        this.selectModel(m.id);
      });

      this.dropdown.appendChild(opt);
    });

    this._updateTriggerDisplay();
  }

  selectModel(modelId) {
    const model = this.models.find(m => m.id === modelId);
    if (!model) return;

    if (model.is_available === false) {
      return;
    }

    this.selectedModelId = modelId;
    this._updateTriggerDisplay();
    this.close();

    if (window.retroAudio) {
      window.retroAudio.playBleep(520, 0.04);
    }

    if (typeof this.onChange === "function") {
      this.onChange(modelId, model);
    }
  }

  _updateTriggerDisplay() {
    const model = this.models.find(m => m.id === this.selectedModelId);
    if (model) {
      this.selectedText.textContent = `${model.name || model.id}`;
      const isAvailable = model.is_available !== false;
      this.statusDot.style.background = isAvailable ? "#00ff66" : "#ff3366";
      this.statusDot.style.boxShadow = `0 0 4px ${isAvailable ? "#00ff66" : "#ff3366"}`;
    } else if (this.selectedModelId) {
      this.selectedText.textContent = this.selectedModelId;
      this.statusDot.style.background = "#00ff66";
    } else {
      this.selectedText.textContent = "SELECT AI MODEL...";
      this.statusDot.style.background = "#7b889b";
    }
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    this.isOpen = true;
    this.combobox.setAttribute("aria-expanded", "true");
    this.dropdown.classList.add("open");
    this.focusedIndex = this.models.findIndex(m => m.id === this.selectedModelId);
    if (this.focusedIndex < 0) this.focusedIndex = 0;
    this._highlightFocusedOption();
    if (window.retroAudio) window.retroAudio.playBleep(440, 0.02);
  }

  close() {
    this.isOpen = false;
    this.combobox.setAttribute("aria-expanded", "false");
    this.dropdown.classList.remove("open");
  }

  _handleKeyDown(e) {
    if (!this.isOpen && (e.key === "Enter" || e.key === " " || e.key === "ArrowDown")) {
      e.preventDefault();
      this.open();
      return;
    }

    if (!this.isOpen) return;

    if (e.key === "Escape" || e.key === "Tab") {
      this.close();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      this._moveFocus(1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      this._moveFocus(-1);
    } else if (e.key === "Home") {
      e.preventDefault();
      this.focusedIndex = 0;
      this._highlightFocusedOption();
    } else if (e.key === "End") {
      e.preventDefault();
      this.focusedIndex = this.models.length - 1;
      this._highlightFocusedOption();
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (this.focusedIndex >= 0 && this.focusedIndex < this.models.length) {
        const targetModel = this.models[this.focusedIndex];
        if (targetModel.is_available !== false) {
          this.selectModel(targetModel.id);
        } else {
          if (window.retroAudio) window.retroAudio.playBleep(240, 0.08);
        }
      }
    }
  }

  _moveFocus(delta) {
    if (this.models.length === 0) return;
    this.focusedIndex = (this.focusedIndex + delta + this.models.length) % this.models.length;
    this._highlightFocusedOption();
  }

  _highlightFocusedOption() {
    const options = this.dropdown.querySelectorAll(".pixel-option");
    options.forEach((opt, idx) => {
      if (idx === this.focusedIndex) {
        opt.classList.add("focused");
        opt.scrollIntoView({ block: "nearest" });
      } else {
        opt.classList.remove("focused");
      }
    });
  }

  getValue() {
    return this.selectedModelId;
  }

  setValue(modelId) {
    this.selectedModelId = modelId;
    this._updateTriggerDisplay();
  }
}

window.RetroCustomDropdown = RetroCustomDropdown;
