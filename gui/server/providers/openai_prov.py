"""
OpenAI Provider implementation for Account Pool Hub.
Supports OpenAI API Keys and GPT-4o / reasoning models.
"""

from typing import Any, Dict, List, Tuple
import httpx

from gui.server import cred_store
from gui.server.providers.base_provider import BaseProvider, ProviderStatus

OPENAI_MODELS: List[Dict[str, Any]] = [
    {
        "id": "gpt-4o",
        "name": "GPT-4o (Omni)",
        "tier": "reasoning",
        "provider": "openai",
        "context_window": 128000,
        "description": "OpenAI flagship versatile reasoning model"
    },
    {
        "id": "gpt-4.5-preview",
        "name": "GPT-4.5 Preview",
        "tier": "reasoning",
        "provider": "openai",
        "context_window": 128000,
        "description": "Massive scale advanced reasoning model"
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "tier": "fast",
        "provider": "openai",
        "context_window": 128000,
        "description": "Cost-efficient lightweight operational model"
    },
    {
        "id": "o3-mini",
        "name": "o3-mini (Reasoning)",
        "tier": "reasoning",
        "provider": "openai",
        "context_window": 200000,
        "description": "Specialized high-speed STEM & logic reasoning"
    },
    {
        "id": "o1",
        "name": "o1 (Deep Reasoning)",
        "tier": "reasoning",
        "provider": "openai",
        "context_window": 200000,
        "description": "Deep thinking autonomous problem solving model"
    }
]


class OpenAIProvider(BaseProvider):
    def __init__(self, strategy: str = "priority"):
        super().__init__(name="openai", display_name="OpenAI / Codex", strategy=strategy)

    def get_supported_models(self) -> List[Dict[str, Any]]:
        return OPENAI_MODELS

    async def verify_account(self, account_id: str) -> Tuple[bool, str]:
        """Perform a live probe request to OpenAI API."""
        acc = self.get_account(account_id)
        if not acc:
            return False, f"Account '{account_id}' not found"

        secret = cred_store.get_active_secret(self.name, account_id)
        if not secret:
            self.mark_status(account_id, ProviderStatus.DISCONNECTED, "No credential found in keyring")
            return False, "No credential found in keyring"

        self.mark_status(account_id, ProviderStatus.CHECKING)

        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {secret}"}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                res = await client.get(url, headers=headers)

            if res.status_code == 200:
                self.mark_status(account_id, ProviderStatus.CONNECTED)
                return True, "Verified successfully"
            elif res.status_code in (401, 403):
                msg = f"Invalid API Key (HTTP {res.status_code})"
                self.mark_status(account_id, ProviderStatus.INVALID_CRED, msg)
                return False, msg
            elif res.status_code == 429:
                msg = "Rate limited (HTTP 429)"
                self.mark_status(account_id, ProviderStatus.RATE_LIMITED, msg)
                return False, msg
            else:
                msg = f"Upstream error HTTP {res.status_code}"
                self.mark_status(account_id, ProviderStatus.CHECKING, msg)
                return False, msg

        except Exception as e:
            msg = f"Connection error: {str(e)}"
            self.mark_status(account_id, ProviderStatus.CHECKING, msg)
            return False, msg
