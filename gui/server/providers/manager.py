"""
Central Provider & Account Pool Manager (Plan 3.1 & 5.1).
Coordinates all AI providers, models catalog, status gating, and settings persistence.
"""

from typing import Any, Dict, List, Optional, Tuple

from gui.server.providers.base_provider import BaseProvider, ProviderStatus, Account
from gui.server.providers.gemini_prov import GeminiProvider
from gui.server.providers.claude_prov import ClaudeProvider
from gui.server.providers.openai_prov import OpenAIProvider
from gui.server.providers.antigravity_prov import AntigravityProvider


class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {
            "gemini": GeminiProvider(),
            "anthropic": ClaudeProvider(),
            "openai": OpenAIProvider(),
            "antigravity": AntigravityProvider()
        }

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get provider by key name (case-insensitive)."""
        if not name:
            return None
        return self.providers.get(name.lower().strip())

    def resolve_provider_for_model(self, model_id: str) -> Optional[BaseProvider]:
        """Find the matching provider for a model ID."""
        if not model_id:
            return None
        m = model_id.lower().strip()

        # 1. Exact catalog match
        for prov in self.providers.values():
            for supported in prov.get_supported_models():
                if supported["id"].lower() == m:
                    return prov

        # 2. Substring & prefix heuristics (Antigravity checked first to avoid hijacking by sub-model names)
        if "antigravity" in m:
            return self.providers.get("antigravity")
        elif "claude" in m or "anthropic" in m:
            return self.providers.get("anthropic")
        elif "gemini" in m or "google" in m:
            return self.providers.get("gemini")
        elif "gpt" in m or m.startswith("o1") or m.startswith("o3") or "openai" in m or "codex" in m:
            return self.providers.get("openai")

        return None

    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        Return the catalog of all models across all providers,
        annotated with live provider status and dispatch availability.
        """
        models_catalog: List[Dict[str, Any]] = []
        for prov_name, prov in self.providers.items():
            agg_status = prov.get_aggregate_status()
            for m in prov.get_supported_models():
                model_copy = dict(m)
                model_copy["provider_status"] = agg_status.value
                model_copy["is_available"] = (agg_status == ProviderStatus.CONNECTED) or (
                    prov_name == "antigravity" and agg_status == ProviderStatus.UNKNOWN
                )
                if not model_copy["is_available"]:
                    model_copy["disabled_reason"] = f"Provider '{prov.display_name}' is {agg_status.value}"
                else:
                    model_copy["disabled_reason"] = None
                models_catalog.append(model_copy)
        return models_catalog

    def can_dispatch_model(self, model_id: str, allow_unknown_antigravity: bool = True) -> Tuple[bool, str]:
        """
        Validate whether a model can be dispatched (SEC-01 Gating).
        Returns (is_allowed, reason).
        """
        prov = self.resolve_provider_for_model(model_id)
        if not prov:
            return False, f"Unsupported model '{model_id}': No provider registered."

        status = prov.get_aggregate_status()

        if status == ProviderStatus.CONNECTED:
            return True, "Provider connected"

        if prov.name == "antigravity" and status == ProviderStatus.UNKNOWN and allow_unknown_antigravity:
            return True, "Antigravity local session detected (UNKNOWN status permitted with confirmation)"

        return False, f"Model '{model_id}' cannot be dispatched: Provider '{prov.display_name}' is {status.value}."

    def load_from_settings(self, providers_settings: Dict[str, Any]) -> None:
        """Hydrate provider strategies and accounts from settings dictionary."""
        if not providers_settings or not isinstance(providers_settings, dict):
            return

        for prov_key, config in providers_settings.items():
            prov = self.get_provider(prov_key)
            if not prov or not isinstance(config, dict):
                continue

            if "strategy" in config:
                prov.strategy = config["strategy"]

            if "accounts" in config and isinstance(config["accounts"], list):
                prov.accounts = []
                for acc_raw in config["accounts"]:
                    if isinstance(acc_raw, dict) and "id" in acc_raw:
                        acc = Account.model_validate(acc_raw)
                        prov.accounts.append(acc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all providers to dictionary for settings.json."""
        return {name: prov.to_dict() for name, prov in self.providers.items()}


# Global singleton provider manager instance
provider_manager = ProviderManager()
