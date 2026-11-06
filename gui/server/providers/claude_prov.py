"""
Anthropic Claude Provider implementation for Account Pool Hub.
Supports Anthropic API Keys and Claude 3.5/3.7 models.
"""

from typing import Any, Dict, List, Tuple
import httpx

from gui.server import cred_store
from gui.server.providers.base_provider import BaseProvider, ProviderStatus

CLAUDE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "claude-3-7-sonnet-20250219",
        "name": "Claude 3.7 Sonnet (Hybrid)",
        "tier": "reasoning",
        "provider": "anthropic",
        "context_window": 200000,
        "description": "Anthropic flagship hybrid reasoning & coding model"
    },
    {
        "id": "claude-3-5-sonnet-20241022",
        "name": "Claude 3.5 Sonnet",
        "tier": "reasoning",
        "provider": "anthropic",
        "context_window": 200000,
        "description": "High intelligence code and security review model"
    },
    {
        "id": "claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku",
        "tier": "fast",
        "provider": "anthropic",
        "context_window": 200000,
        "description": "Lightning-fast lightweight operative model"
    }
]


class ClaudeProvider(BaseProvider):
    def __init__(self, strategy: str = "priority"):
        super().__init__(name="anthropic", display_name="Anthropic Claude", strategy=strategy)

    def get_supported_models(self) -> List[Dict[str, Any]]:
        return CLAUDE_MODELS

    async def verify_account(self, account_id: str) -> Tuple[bool, str]:
        """Perform a live probe request to Anthropic API."""
        acc = self.get_account(account_id)
        if not acc:
            return False, f"Account '{account_id}' not found"

        secret = cred_store.get_active_secret(self.name, account_id)
        if not secret:
            self.mark_status(account_id, ProviderStatus.DISCONNECTED, "No credential found in keyring")
            return False, "No credential found in keyring"

        self.mark_status(account_id, ProviderStatus.CHECKING)

        url = "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": secret,
            "anthropic-version": "2023-06-01"
        }

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
