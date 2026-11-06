"""
Base Provider & Account Pool Controller (ala 9router architecture).
Defines ProviderStatus, Account, AccountUsage, and the BaseProvider abstract class.
"""

from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from gui.server import cred_store


class ProviderStatus(str, Enum):
    CONNECTED = "CONNECTED"
    UNKNOWN = "UNKNOWN"
    CHECKING = "CHECKING"
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    EXPIRED = "EXPIRED"
    INVALID_CRED = "INVALID_CRED"
    DISCONNECTED = "DISCONNECTED"


class AccountUsage(BaseModel):
    requests: int = 0
    tokens: int = 0
    cost_usd: float = 0.0


class Account(BaseModel):
    id: str
    label: str
    priority: int = 1
    enabled: bool = True
    cooldown_until: Optional[float] = None
    usage: AccountUsage = Field(default_factory=AccountUsage)
    status: ProviderStatus = ProviderStatus.DISCONNECTED
    error_message: Optional[str] = None

    def is_available(self) -> bool:
        """Check if account is active, non-cooldown, and ready to serve."""
        if not self.enabled:
            return False
        if self.cooldown_until is not None and time.time() < self.cooldown_until:
            return False
        return self.status in (ProviderStatus.CONNECTED, ProviderStatus.UNKNOWN)


class BaseProvider(ABC):
    """
    Abstract Base Class for an AI Provider with an Account Pool.
    """

    def __init__(self, name: str, display_name: str, strategy: str = "priority"):
        self.name: str = name.lower()
        self.display_name: str = display_name
        self.strategy: str = strategy  # "priority" | "round-robin" | "least-used"
        self.accounts: List[Account] = []
        self._rr_index: int = 0

    def get_account(self, account_id: str) -> Optional[Account]:
        """Find an account by id."""
        for acc in self.accounts:
            if acc.id == account_id:
                return acc
        return None

    def get_available_accounts(self) -> List[Account]:
        """Return all accounts that are currently enabled and not on cooldown."""
        now = time.time()
        available = []
        for acc in self.accounts:
            if not acc.enabled:
                continue
            if acc.cooldown_until is not None and now < acc.cooldown_until:
                continue
            # If cooldown passed, clear it
            if acc.cooldown_until is not None and now >= acc.cooldown_until:
                acc.cooldown_until = None
                if acc.status == ProviderStatus.RATE_LIMITED:
                    acc.status = ProviderStatus.CONNECTED
            if acc.status in (ProviderStatus.CONNECTED, ProviderStatus.UNKNOWN):
                available.append(acc)
        return available

    def get_active_account(self) -> Optional[Account]:
        """
        Select the next active account according to the configured routing strategy:
        - 'priority': lowest priority integer first (1 is highest priority)
        - 'least-used': lowest cost_usd first
        - 'round-robin': cyclic rotation
        """
        available = self.get_available_accounts()
        if not available:
            return None

        if self.strategy == "priority":
            available.sort(key=lambda a: (a.priority, a.usage.requests))
            return available[0]

        elif self.strategy == "least-used":
            available.sort(key=lambda a: (a.usage.cost_usd, a.usage.tokens))
            return available[0]

        elif self.strategy == "round-robin":
            idx = self._rr_index % len(available)
            self._rr_index = (self._rr_index + 1) % len(available)
            return available[idx]

        # Default fallback to priority
        available.sort(key=lambda a: a.priority)
        return available[0]

    def add_account(
        self,
        account_id: str,
        label: str,
        priority: int = 1,
        enabled: bool = True,
        secret: Optional[str] = None
    ) -> Account:
        """Add or update an account in the pool and securely store secret in keyring."""
        existing = self.get_account(account_id)
        if existing:
            existing.label = label
            existing.priority = priority
            existing.enabled = enabled
            acc = existing
        else:
            acc = Account(
                id=account_id,
                label=label,
                priority=priority,
                enabled=enabled,
                status=ProviderStatus.CHECKING
            )
            self.accounts.append(acc)

        if secret:
            cred_store.set_credential(self.name, account_id, secret)
            acc.status = ProviderStatus.CONNECTED

        return acc

    def remove_account(self, account_id: str) -> bool:
        """Remove account from pool and delete secret from Windows Credential Manager."""
        acc = self.get_account(account_id)
        if not acc:
            return False

        self.accounts = [a for a in self.accounts if a.id != account_id]
        try:
            cred_store.delete_credential(self.name, account_id)
        except Exception:
            pass
        return True

    def set_cooldown(self, account_id: str, cooldown_seconds: float, reason: str = "Rate limited (429)") -> None:
        """Put account on temporary cooldown (e.g. HTTP 429)."""
        acc = self.get_account(account_id)
        if acc:
            acc.cooldown_until = time.time() + cooldown_seconds
            acc.status = ProviderStatus.RATE_LIMITED
            acc.error_message = reason

    def mark_status(self, account_id: str, status: ProviderStatus, error: Optional[str] = None) -> None:
        """Update account status and optional error message."""
        acc = self.get_account(account_id)
        if acc:
            acc.status = status
            acc.error_message = error

    def get_aggregate_status(self) -> ProviderStatus:
        """
        Aggregate status across all accounts in this provider:
        - If at least 1 account is CONNECTED and available -> CONNECTED
        - If at least 1 account is UNKNOWN and available -> UNKNOWN
        - If accounts exist and all are RATE_LIMITED -> RATE_LIMITED
        - If accounts exist and all are QUOTA_EXHAUSTED -> QUOTA_EXHAUSTED
        - If accounts exist and all are INVALID_CRED -> INVALID_CRED
        - If no accounts or none enabled -> DISCONNECTED
        """
        if not self.accounts:
            return ProviderStatus.DISCONNECTED

        enabled_accounts = [a for a in self.accounts if a.enabled]
        if not enabled_accounts:
            return ProviderStatus.DISCONNECTED

        now = time.time()
        for a in enabled_accounts:
            # Check if active and not in cooldown
            if a.cooldown_until and now >= a.cooldown_until:
                a.cooldown_until = None
                if a.status == ProviderStatus.RATE_LIMITED:
                    a.status = ProviderStatus.CONNECTED

            if a.status == ProviderStatus.CONNECTED and (a.cooldown_until is None or now >= a.cooldown_until):
                return ProviderStatus.CONNECTED

        # Check for UNKNOWN (e.g. Antigravity local detection)
        if any(a.status == ProviderStatus.UNKNOWN for a in enabled_accounts):
            return ProviderStatus.UNKNOWN

        # Check for CHECKING
        if any(a.status == ProviderStatus.CHECKING for a in enabled_accounts):
            return ProviderStatus.CHECKING

        # Check for RATE_LIMITED
        if any(a.status == ProviderStatus.RATE_LIMITED for a in enabled_accounts):
            return ProviderStatus.RATE_LIMITED

        # Check for QUOTA_EXHAUSTED
        if any(a.status == ProviderStatus.QUOTA_EXHAUSTED for a in enabled_accounts):
            return ProviderStatus.QUOTA_EXHAUSTED

        # Check for INVALID_CRED
        if any(a.status == ProviderStatus.INVALID_CRED for a in enabled_accounts):
            return ProviderStatus.INVALID_CRED

        return ProviderStatus.DISCONNECTED

    @abstractmethod
    async def verify_account(self, account_id: str) -> Tuple[bool, str]:
        """Perform a live verification probe for the specified account."""
        pass

    @abstractmethod
    def get_supported_models(self) -> List[Dict[str, Any]]:
        """Return list of supported models with tiers and capabilities."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize provider config (excluding secrets) for settings.json."""
        return {
            "strategy": self.strategy,
            "accounts": [a.model_dump(exclude={"error_message"}) for a in self.accounts]
        }
