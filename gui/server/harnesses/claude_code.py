"""
Claude Code CLI Adapter for 8-Bit Cyber Operations Office GUI.
Interfaces with `claude -p "<prompt>" --output-format stream-json`.
Defaults to high-fidelity Dry-Run simulation unless explicitly toggled to Live mode.
Enforces timeout limits, cwd isolation, non-interactive stdin, and process cleanup.
"""

import asyncio
import json
import os
import shutil
import time
from typing import Dict, Any, Callable, Awaitable, Optional

from gui.server.harnesses.base import BaseHarnessAdapter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class ClaudeCodeAdapter(BaseHarnessAdapter):
    """
    Adapter executing tasks via the Claude Code CLI tool.
    """

    def __init__(self):
        super().__init__(name="claude_code")

    def _find_claude_binary(self) -> Optional[str]:
        """Locate the claude executable in PATH."""
        for name in ["claude", "claude.cmd", "claude.exe"]:
            path = shutil.which(name)
            if path:
                return path
        # Common npm/local bin paths on Windows
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            os.path.expanduser("~/.local/bin/claude.exe"),
            os.path.join(local_app_data, "npm", "claude.cmd"),
            os.path.join(local_app_data, "Programs", "claude", "claude.exe")
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    async def execute_task(
        self,
        card: Dict[str, Any],
        agent: Dict[str, Any],
        settings: Dict[str, Any],
        on_log_chunk: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> Dict[str, Any]:
        """
        Execute card. Respects the dry_run flag.
        """
        dry_run = card.get("dry_run", settings.get("dry_run_default", True))

        if dry_run:
            return await self.run_dry_run_simulation(card, agent, settings, on_log_chunk)

        # Live Execution Path
        claude_bin = self._find_claude_binary()
        card_id = card.get("id", "card-unknown")
        agent_id = agent.get("id", "agent-unknown")
        agent_name = agent.get("name", "Operative")
        title = card.get("title", "")
        desc = card.get("description", "")
        model = agent.get("model") or settings.get("agent_models", {}).get(agent_id)
        timeout_seconds = int(settings.get("execution_timeout_seconds", 180))

        async def emit(msg_type: str, content: str):
            await on_log_chunk({
                "card_id": card_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "type": msg_type,
                "content": content,
                "timestamp": time.time()
            })

        if not claude_bin:
            await emit("alert", "Warning: 'claude' CLI binary was not found in system PATH. Reverting to safe dry-run mode.")
            return await self.run_dry_run_simulation(card, agent, settings, on_log_chunk)

        # Assemble prompt for Claude Code
        prompt = (
            f"You are operating as {agent.get('role', 'Security Specialist')} ({agent_name}).\n"
            f"Objective: {title}\n"
            f"Details: {desc}\n"
            f"Recommended Skills: {', '.join(card.get('recommended_skills', []))}\n"
            f"Provide concise, actionable security findings and execution steps."
        )

        cmd = [claude_bin, "-p", prompt, "--output-format", "stream-json"]
        if model and "claude" in model.lower():
            cmd.extend(["--model", model])

        await emit("status", f"Initiating Live Claude Code CLI session (binary: {os.path.basename(claude_bin)}, model: {model or 'default'})...")

        proc = None
        try:
            # Run locked in repository root with non-interactive stdin
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=REPO_ROOT
            )

            full_output = []

            async def _stream_reader():
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue

                    try:
                        event = json.loads(line_str)
                        text = event.get("text") or event.get("content") or line_str
                        await emit("thought", str(text))
                        full_output.append(str(text))
                    except Exception:
                        await emit("thought", line_str)
                        full_output.append(line_str)

                await proc.wait()

            await asyncio.wait_for(_stream_reader(), timeout=timeout_seconds)
            exit_code = proc.returncode

            if exit_code == 0:
                await emit("status", "Live task execution completed successfully.")
                return {
                    "card_id": card_id,
                    "agent_id": agent_id,
                    "status": "completed",
                    "execution_mode": "live",
                    "summary": f"Completed live execution: {title}",
                    "findings": [{"title": title, "severity": "INFO", "agent": agent_name}]
                }
            else:
                stderr_data = await proc.stderr.read()
                err_msg = stderr_data.decode("utf-8", errors="replace").strip()
                await emit("alert", f"Claude Code exited with error code {exit_code}: {err_msg[:200]}")
                return {
                    "card_id": card_id,
                    "agent_id": agent_id,
                    "status": "failed",
                    "execution_mode": "live",
                    "summary": f"Live task execution failed with code {exit_code}",
                    "error": err_msg
                }

        except asyncio.TimeoutError:
            await emit("alert", f"Execution timed out after {timeout_seconds}s. Subprocess terminated.")
            return {
                "card_id": card_id,
                "agent_id": agent_id,
                "status": "failed",
                "execution_mode": "live",
                "error": f"Execution timed out after {timeout_seconds}s"
            }
        except Exception as e:
            await emit("alert", f"Exception during live execution: {str(e)}")
            return {
                "card_id": card_id,
                "agent_id": agent_id,
                "status": "failed",
                "execution_mode": "live",
                "error": str(e)
            }
        finally:
            if proc and proc.returncode is None:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
