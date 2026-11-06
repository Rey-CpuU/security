r"""
Antigravity Desktop Mailbox Delegator & Session Probe (SEC-07, Plan 2.7).
Manages secure hardened IPC mailbox communication with Antigravity Desktop via scratch/tasks/.
Features:
- Strict path traversal defense: filename regex ^[a-zA-Z0-9_-]+\.json$
- Atomic file write via temp files (.tmp_[uuid]) and os.replace
- Pydantic TaskPayloadSchema validation with 1MB size limit
- Local process / session environment probe
"""

import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError

from gui.server.providers.base_provider import BaseProvider, ProviderStatus, Account

FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]+\.json$")
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1 MB


class TaskPayloadSchema(BaseModel):
    task_id: str
    card_id: str
    title: str
    description: Optional[str] = ""
    agent_id: str
    model: str
    dry_run: bool = True
    context: Dict[str, Any] = Field(default_factory=dict)


ANTIGRAVITY_MODELS: List[Dict[str, Any]] = [
    {
        "id": "antigravity-gemini-2.5-pro",
        "name": "Antigravity (Gemini 2.5 Pro Session)",
        "tier": "reasoning",
        "provider": "antigravity",
        "context_window": 1000000,
        "description": "Delegated to active local Antigravity session"
    },
    {
        "id": "antigravity-claude-3-7-sonnet",
        "name": "Antigravity (Claude 3.7 Sonnet Session)",
        "tier": "reasoning",
        "provider": "antigravity",
        "context_window": 200000,
        "description": "Delegated to active local Antigravity session"
    }
]


class AntigravityProvider(BaseProvider):
    def __init__(self, tasks_dir: Optional[str] = None, strategy: str = "priority"):
        super().__init__(name="antigravity", display_name="Antigravity Desktop", strategy=strategy)
        if tasks_dir:
            self.tasks_dir = os.path.abspath(tasks_dir)
        else:
            # Default to scratch/tasks
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            self.tasks_dir = os.path.join(repo_root, "scratch", "tasks")

        # Initialize default local session account
        default_acc = Account(
            id="local-session",
            label="Local Antigravity Session",
            priority=1,
            enabled=True,
            status=ProviderStatus.UNKNOWN
        )
        self.accounts = [default_acc]

    def get_supported_models(self) -> List[Dict[str, Any]]:
        return ANTIGRAVITY_MODELS

    async def verify_account(self, account_id: str) -> Tuple[bool, str]:
        """
        Probe for active Antigravity session and mailbox accessibility.
        Returns UNKNOWN (best-effort) or CONNECTED if active session environment detected.
        """
        acc = self.get_account(account_id)
        if not acc:
            return False, f"Account '{account_id}' not found"

        # Check for Antigravity directory or environment
        antigravity_home = os.path.expanduser(r"~\.gemini\antigravity")
        has_antigravity_dir = os.path.isdir(antigravity_home)

        try:
            os.makedirs(self.tasks_dir, exist_ok=True)
            test_probe = os.path.join(self.tasks_dir, f".probe_{uuid.uuid4().hex[:6]}.tmp")
            with open(test_probe, "w", encoding="utf-8") as f:
                f.write("probe")
            os.remove(test_probe)
            can_write_mailbox = True
        except Exception:
            can_write_mailbox = False

        if has_antigravity_dir and can_write_mailbox:
            self.mark_status(account_id, ProviderStatus.UNKNOWN, "Local Antigravity detected (session confirmation required)")
            return True, "Local Antigravity session reachable (Status: UNKNOWN)"
        elif can_write_mailbox:
            self.mark_status(account_id, ProviderStatus.UNKNOWN, "Mailbox writable, session status UNKNOWN")
            return True, "Mailbox writable (Status: UNKNOWN)"
        else:
            self.mark_status(account_id, ProviderStatus.DISCONNECTED, "Mailbox not writable")
            return False, "Cannot access tasks mailbox"

    def delegate_task(self, filename: str, payload_dict: Dict[str, Any]) -> str:
        """
        Atomically write a validated task payload to scratch/tasks/.
        Strictly enforces path traversal protection and Pydantic schema validation.
        """
        if not filename or not FILENAME_REGEX.match(filename):
            raise ValueError(f"Invalid task filename '{filename}'. Must match ^[a-zA-Z0-9_-]+\\.json$ (Path traversal blocked).")

        if "/" in filename or "\\" in filename or ".." in filename:
            raise ValueError("Path traversal sequences rejected.")

        # Validate Schema
        try:
            validated = TaskPayloadSchema.model_validate(payload_dict)
        except ValidationError as e:
            raise ValueError(f"Task payload schema validation failed: {e}") from e

        json_bytes = validated.model_dump_json(indent=2).encode("utf-8")
        if len(json_bytes) > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload size ({len(json_bytes)} bytes) exceeds 1MB limit.")

        os.makedirs(self.tasks_dir, exist_ok=True)

        target_path = os.path.join(self.tasks_dir, filename)
        temp_path = os.path.join(self.tasks_dir, f".tmp_{uuid.uuid4().hex}.json")

        try:
            with open(temp_path, "wb") as f:
                f.write(json_bytes)
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename / replace
            os.replace(temp_path, target_path)
            return target_path
        except Exception as e:
            if os.path.isfile(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            raise IOError(f"Failed to atomically write task file '{filename}': {e}") from e
