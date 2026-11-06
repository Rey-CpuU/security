"""
Providers Module for 8-Bit Cyber Operations Office GUI.
Exposes ProviderStatus, BaseProvider, Account, and the singleton provider_manager.
"""

from gui.server.providers.base_provider import ProviderStatus, BaseProvider, Account, AccountUsage
from gui.server.providers.gemini_prov import GeminiProvider
from gui.server.providers.claude_prov import ClaudeProvider
from gui.server.providers.openai_prov import OpenAIProvider
from gui.server.providers.antigravity_prov import AntigravityProvider
from gui.server.providers.manager import ProviderManager, provider_manager

__all__ = [
    "ProviderStatus",
    "BaseProvider",
    "Account",
    "AccountUsage",
    "GeminiProvider",
    "ClaudeProvider",
    "OpenAIProvider",
    "AntigravityProvider",
    "ProviderManager",
    "provider_manager",
]
