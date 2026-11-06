"""
Unit Tests for Fase 1: Account Pool & Provider Engine (ala 9router Architecture).
Verifies:
- Priority routing and failover on 429 rate limit cooldown
- Round-Robin and Least-Used routing strategies
- Aggregate status resolution across multiple accounts
- Antigravity mailbox security: path traversal defense, atomic write, and Pydantic schema validation
- Provider Hub REST management endpoints
"""

import os
import shutil
import sys
import tempfile
import time
import unittest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from gui.server.app import app
from gui.server.providers import (
    provider_manager,
    ProviderStatus,
    GeminiProvider,
    ClaudeProvider,
    AntigravityProvider,
    Account,
    AccountUsage,
)


class TestAccountPool(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # --- 1. Account Pool Routing & Failover ---

    def test_priority_routing_and_failover_on_429(self):
        """Account pool selects priority 1, and automatically fails over to priority 2 on cooldown."""
        prov = GeminiProvider(strategy="priority")
        acc1 = Account(
            id="gem-primary",
            label="Primary Work Key",
            priority=1,
            enabled=True,
            status=ProviderStatus.CONNECTED
        )
        acc2 = Account(
            id="gem-backup",
            label="Backup Key",
            priority=2,
            enabled=True,
            status=ProviderStatus.CONNECTED
        )
        prov.accounts = [acc1, acc2]

        # 1. Normal state -> selects acc1 (priority 1)
        active = prov.get_active_account()
        self.assertIsNotNone(active)
        self.assertEqual(active.id, "gem-primary")

        # 2. Trigger 429 cooldown on acc1 for 60 seconds
        prov.set_cooldown("gem-primary", cooldown_seconds=60)
        self.assertEqual(acc1.status, ProviderStatus.RATE_LIMITED)
        self.assertFalse(acc1.is_available())

        # 3. Automatic failover -> selects acc2 (priority 2)
        active_after_failover = prov.get_active_account()
        self.assertIsNotNone(active_after_failover)
        self.assertEqual(active_after_failover.id, "gem-backup")

        # 4. If acc2 also enters cooldown -> no active accounts, provider aggregate status is RATE_LIMITED
        prov.set_cooldown("gem-backup", cooldown_seconds=60)
        self.assertIsNone(prov.get_active_account())
        self.assertEqual(prov.get_aggregate_status(), ProviderStatus.RATE_LIMITED)

    def test_round_robin_and_least_used_strategies(self):
        """Round-robin rotates through accounts, least-used picks lowest USD cost."""
        # 1. Round-Robin
        prov_rr = ClaudeProvider(strategy="round-robin")
        acc_a = Account(id="a", label="A", priority=1, enabled=True, status=ProviderStatus.CONNECTED)
        acc_b = Account(id="b", label="B", priority=1, enabled=True, status=ProviderStatus.CONNECTED)
        prov_rr.accounts = [acc_a, acc_b]

        pick1 = prov_rr.get_active_account()
        pick2 = prov_rr.get_active_account()
        pick3 = prov_rr.get_active_account()
        self.assertEqual(pick1.id, "a")
        self.assertEqual(pick2.id, "b")
        self.assertEqual(pick3.id, "a")

        # 2. Least-Used
        prov_lu = ClaudeProvider(strategy="least-used")
        acc_cheap = Account(
            id="cheap",
            label="Cheap",
            priority=1,
            enabled=True,
            status=ProviderStatus.CONNECTED,
            usage=AccountUsage(requests=5, tokens=1000, cost_usd=0.01)
        )
        acc_expensive = Account(
            id="expensive",
            label="Expensive",
            priority=1,
            enabled=True,
            status=ProviderStatus.CONNECTED,
            usage=AccountUsage(requests=50, tokens=100000, cost_usd=2.50)
        )
        prov_lu.accounts = [acc_expensive, acc_cheap]
        best = prov_lu.get_active_account()
        self.assertEqual(best.id, "cheap")

    def test_aggregate_status_resolution(self):
        """Aggregate status accurately reflects active, disconnected, or error states."""
        prov = GeminiProvider()
        self.assertEqual(prov.get_aggregate_status(), ProviderStatus.DISCONNECTED)

        acc = Account(id="test", label="Test", enabled=False, status=ProviderStatus.CONNECTED)
        prov.accounts = [acc]
        self.assertEqual(prov.get_aggregate_status(), ProviderStatus.DISCONNECTED)

        acc.enabled = True
        self.assertEqual(prov.get_aggregate_status(), ProviderStatus.CONNECTED)

        acc.status = ProviderStatus.INVALID_CRED
        self.assertEqual(prov.get_aggregate_status(), ProviderStatus.INVALID_CRED)

    # --- 2. Antigravity Mailbox Security (SEC-07, Plan 2.7) ---

    def test_antigravity_mailbox_path_traversal_protection(self):
        """Mailbox delegator strictly rejects path traversal sequences."""
        temp_dir = tempfile.mkdtemp(prefix="test_mailbox_")
        try:
            prov = AntigravityProvider(tasks_dir=temp_dir)
            valid_payload = {
                "task_id": "t-100",
                "card_id": "c-100",
                "title": "Analyze malware binary",
                "description": "Decompile and check imports",
                "agent_id": "pentest",
                "model": "antigravity-gemini-2.5-pro",
                "dry_run": True,
                "context": {}
            }

            # Valid filename
            task_file = prov.delegate_task("task_100.json", valid_payload)
            self.assertTrue(os.path.isfile(task_file))

            # Path traversal: ../
            with self.assertRaises(ValueError):
                prov.delegate_task("../escape.json", valid_payload)

            # Path traversal: sub/dir
            with self.assertRaises(ValueError):
                prov.delegate_task("sub/dir.json", valid_payload)

            # Invalid extensions
            with self.assertRaises(ValueError):
                prov.delegate_task("malicious.exe", valid_payload)

            # Invalid characters
            with self.assertRaises(ValueError):
                prov.delegate_task("task;bad.json", valid_payload)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_antigravity_mailbox_atomic_write_and_schema(self):
        """Task writing is atomic and validates Pydantic schema."""
        temp_dir = tempfile.mkdtemp(prefix="test_mailbox_atomic_")
        try:
            prov = AntigravityProvider(tasks_dir=temp_dir)

            # Incomplete payload (missing required field 'agent_id')
            bad_payload = {
                "task_id": "t-1",
                "card_id": "c-1",
                "title": "Incomplete task"
            }
            with self.assertRaises(ValueError) as cm:
                prov.delegate_task("invalid_task.json", bad_payload)
            self.assertIn("schema validation failed", str(cm.exception).lower())

            # Verify no partial or tmp files remained
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 0)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # --- 3. Provider Hub REST Management APIs ---

    def test_provider_hub_rest_api_lifecycle(self):
        """REST APIs for listing, adding, verifying, and deleting accounts."""
        # 1. GET /api/providers
        res_list = self.client.get("/api/providers")
        self.assertEqual(res_list.status_code, 200)
        data = res_list.json()
        self.assertIn("providers", data)
        self.assertIn("models", data)
        self.assertTrue(len(data["models"]) >= 10)

        # 2. POST /api/providers/gemini/accounts
        account_id = "unit-test-gem-account"
        res_add = self.client.post(
            "/api/providers/gemini/accounts",
            json={
                "id": account_id,
                "label": "Unit Test Account",
                "priority": 1,
                "enabled": True,
                "secret": "test-key-abc-1234567890"
            }
        )
        self.assertEqual(res_add.status_code, 200)
        acc_data = res_add.json()
        self.assertEqual(acc_data["id"], account_id)

        # 3. POST /api/providers/gemini/strategy
        res_strat = self.client.post(
            "/api/providers/gemini/strategy",
            json={"strategy": "round-robin"}
        )
        self.assertEqual(res_strat.status_code, 200)
        self.assertEqual(res_strat.json()["strategy"], "round-robin")

        # 4. DELETE /api/providers/gemini/accounts/{id}
        res_del = self.client.delete(f"/api/providers/gemini/accounts/{account_id}")
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json()["deleted"], account_id)

    def test_provider_status_triggers_on_429_and_401(self):
        """Provider account status changes to RATE_LIMITED on 429 and INVALID_CRED on 401."""
        prov = GeminiProvider()
        acc = Account(id="probe-acc", label="Probe Account", priority=1, enabled=True, status=ProviderStatus.CONNECTED)
        prov.accounts = [acc]

        # 1. 429 trigger
        prov.set_cooldown(acc.id, cooldown_seconds=45, reason="HTTP 429 Rate limited")
        self.assertEqual(acc.status, ProviderStatus.RATE_LIMITED)
        self.assertIsNotNone(acc.cooldown_until)
        self.assertFalse(acc.is_available())

        # 2. 401 invalid cred trigger
        prov.mark_status(acc.id, ProviderStatus.INVALID_CRED, error="HTTP 401 Invalid Key")
        self.assertEqual(acc.status, ProviderStatus.INVALID_CRED)
        self.assertFalse(acc.is_available())


if __name__ == "__main__":
    unittest.main()
