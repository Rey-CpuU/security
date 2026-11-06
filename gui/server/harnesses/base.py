"""
Abstract Base Harness Adapter for 8-Bit Cyber Operations Office GUI.
Defines common execution lifecycle, streaming contract, and dry-run simulation safety.
"""

import abc
import asyncio
import time
from typing import Dict, Any, Callable, Awaitable, Optional


class BaseHarnessAdapter(abc.ABC):
    """
    Abstract adapter for agent harness execution (Claude Code, OpenAI/Codex, Hermes, etc.).
    """

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def execute_task(
        self,
        card: Dict[str, Any],
        agent: Dict[str, Any],
        settings: Dict[str, Any],
        on_log_chunk: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> Dict[str, Any]:
        """
        Execute or simulate a task card assigned to an agent.
        Logs and thoughts must be streamed via on_log_chunk.
        """
        pass

    async def run_dry_run_simulation(
        self,
        card: Dict[str, Any],
        agent: Dict[str, Any],
        settings: Dict[str, Any],
        on_log_chunk: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> Dict[str, Any]:
        """
        High-fidelity dry-run simulation.
        Generates realistic 8-bit thought streams and tool previews without invoking
        any live shell processes or consuming external API quotas.
        """
        card_id = card.get("id", "card-unknown")
        agent_id = agent.get("id", "agent-unknown")
        agent_name = agent.get("name", "Operative")
        agent_role = agent.get("role", "Security Specialist")
        assigned_model = agent.get("model") or settings.get("agent_models", {}).get(agent_id, "default-model")
        skills = card.get("recommended_skills", ["security-audit"])
        title = card.get("title", "")
        desc = card.get("description", "")

        async def emit(msg_type: str, content: str, pause: float = 0.6):
            chunk = {
                "card_id": card_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "type": msg_type,
                "content": content,
                "timestamp": time.time()
            }
            await on_log_chunk(chunk)
            if pause > 0:
                await asyncio.sleep(pause)

        # Step 1: Agent acknowledgment
        await emit("status", f"[{agent_name} / {agent_role}] Activated using model [{assigned_model}] (DRY-RUN MODE).", 0.4)
        await emit("thought", f"Analyzing objective: '{title}'. Scope constraints verified.", 0.6)

        # Step 2: Skill selection & plan formulation
        skills_str = ", ".join(skills[:3]) if skills else "general-recon"
        await emit("thought", f"Selected execution skill set: [{skills_str}]. Formulating invariant test plan...", 0.7)

        # Step 3: Tool simulation preview
        if "pentest" in agent_id:
            await emit("tool_call", "Simulating nmap port scan & HTTP security header probe on target scope...", 0.7)
            await emit("output", "PORT    STATE SERVICE REASON\n80/tcp  open  http    syn-ack\n443/tcp open  https   syn-ack\nStrict-Transport-Security: missing\nX-Frame-Options: SAMEORIGIN", 0.7)
            await emit("thought", "HSTS header missing. Testing potential parameter injection points...", 0.6)
            await emit("alert", "Vulnerability candidate identified: Missing HSTS & Weak Session Cookie flags (Simulated).", 0.7)
        elif "appsec" in agent_id:
            await emit("tool_call", "Running Semgrep pattern scan for insecure deserialization & tainted input sinks...", 0.7)
            await emit("output", "Scanning repository files...\n[RULE: python.insecure-yaml-load] 0 matches\n[RULE: generic.missing-csrf-token] 1 candidate warning at auth_handler.py:42", 0.7)
            await emit("thought", "Validating invariant: verifying if CSRF token validation can be bypassed...", 0.6)
            await emit("alert", "Code review finding: CSRF token validation missing on state-changing POST endpoint.", 0.7)
        else: # devsecops
            await emit("tool_call", "Running Trivy container scan & GitHub Actions workflow linter...", 0.7)
            await emit("output", "Dockerfile inspection:\n- Base image: alpine:3.18 (OK)\n- Running as non-root user 'appuser': PASS\n- Secrets scanning via gitleaks: CLEAN", 0.7)
            await emit("thought", "Pipeline hardening review complete. Recommending pinned SHA digests for actions.", 0.6)

        # Step 4: Summary & Completion
        summary = f"Dry-run simulation complete for '{title}'. All guardrails validated. Skills tested: {', '.join(skills[:4])}."
        await emit("status", f"Task finished with status SUCCESS (Preview). Report logged to office terminal.", 0.4)

        return {
            "card_id": card_id,
            "agent_id": agent_id,
            "status": "completed",
            "execution_mode": "dry_run",
            "summary": summary,
            "findings": [
                {"title": f"Dry-Run Assessment: {title}", "severity": "MEDIUM", "agent": agent_name}
            ]
        }
