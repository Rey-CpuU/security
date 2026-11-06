"""
Google Gemini Provider implementation for Account Pool Hub.
Supports Gemini API Keys and OAuth flow structure.
"""

from typing import Any, Dict, List, Tuple
import httpx

from gui.server import cred_store
from gui.server.providers.base_provider import BaseProvider, ProviderStatus

GEMINI_MODELS: List[Dict[str, Any]] = [
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "tier": "reasoning",
        "provider": "gemini",
        "context_window": 1000000,
        "description": "Google flagship multimodal reasoning model"
    },
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "tier": "fast",
        "provider": "gemini",
        "context_window": 1000000,
        "description": "Ultra-fast next-gen multimodal workhorse"
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "tier": "reasoning",
        "provider": "gemini",
        "context_window": 2000000,
        "description": "High capability deep context model"
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "tier": "fast",
        "provider": "gemini",
        "context_window": 1000000,
        "description": "Lightweight high-speed triage model"
    }
]


class GeminiProvider(BaseProvider):
    def __init__(self, strategy: str = "priority"):
        super().__init__(name="gemini", display_name="Google Gemini", strategy=strategy)

    def get_supported_models(self) -> List[Dict[str, Any]]:
        return GEMINI_MODELS

    async def verify_account(self, account_id: str) -> Tuple[bool, str]:
        """Perform a live probe request to Google Gemini API."""
        acc = self.get_account(account_id)
        if not acc:
            return False, f"Account '{account_id}' not found"

        secret = cred_store.get_active_secret(self.name, account_id)
        if not secret:
            self.mark_status(account_id, ProviderStatus.DISCONNECTED, "No credential found in keyring")
            return False, "No credential found in keyring"

        self.mark_status(account_id, ProviderStatus.CHECKING)

        url = "https://generativelanguage.googleapis.com/v1beta/models"
        params = {"key": secret}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                res = await client.get(url, params=params)

            if res.status_code == 200:
                self.mark_status(account_id, ProviderStatus.CONNECTED)
                return True, "Verified successfully"
            elif res.status_code in (400, 401, 403):
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
