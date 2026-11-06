"""
Security & Server Unit Tests for 8-Bit Cyber Operations Office GUI.
Verifies Origin verification, dynamic port handling, session token anti-CSWSH gates,
dry-run safety, timeout guards, queue concurrency limits, agent fidelity, and API endpoints.
"""

import asyncio
import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from gui.server import security
from gui.server.app import app
from gui.server.harnesses.claude_code import ClaudeCodeAdapter
from gui.server.state import OfficeStateManager, state_manager


class TestServerSecurity(unittest.TestCase):
    """Test suite for server security and guardrails."""

    def setUp(self):
        self.token = security.get_session_token()
        self.client = TestClient(app)

    def test_origin_verification_allowed(self):
        """Allowed localhost origins must pass verification."""
        self.assertTrue(security.verify_origin("http://127.0.0.1:8888", port=8888))
        self.assertTrue(security.verify_origin("http://localhost:8888", port=8888))
        self.assertTrue(security.verify_origin("http://127.0.0.1:8888/", port=8888))
        self.assertTrue(security.verify_origin("http://127.0.0.1:8888", port=None))

    def test_origin_verification_rejected(self):
        """External or untrusted origins must be strictly rejected (Anti-CSWSH)."""
        self.assertFalse(security.verify_origin("http://malicious-attacker.com", port=8888))
        self.assertFalse(security.verify_origin("https://evil.org", port=8888))
        self.assertFalse(security.verify_origin("http://localhost:9999", port=8888))
        self.assertFalse(security.verify_origin(None, port=8888))
        self.assertFalse(security.verify_origin("", port=8888))

    def test_origin_verification_custom_port(self):
        """Custom port binding must validate against the active port."""
        self.assertTrue(security.verify_origin("http://127.0.0.1:9000", port=9000))
        self.assertTrue(security.verify_origin("http://localhost:9000", port=9000))
        self.assertFalse(security.verify_origin("http://127.0.0.1:9000", port=8888))
        self.assertFalse(security.verify_origin("http://evil-attacker.com:9000", port=9000))

    def test_session_token_validation(self):
        """Valid session token passes constant-time comparison, invalid fails."""
        self.assertTrue(security.verify_session_token(self.token))
        self.assertFalse(security.verify_session_token("invalid-fake-token"))
        self.assertFalse(security.verify_session_token(""))
        self.assertFalse(security.verify_session_token(None))

    def test_token_reset_rotates_session(self):
        """Token rotation invalidates prior token."""
        old_token = security.get_session_token()
        new_token = security.reset_session_token()
        self.assertNotEqual(old_token, new_token)
        self.assertTrue(security.verify_session_token(new_token))
        self.assertFalse(security.verify_session_token(old_token))

    def test_auth_token_endpoint_origin_check(self):
        """GET /api/auth/token rejects external origins and serves trusted localhost."""
        res_bad = self.client.get("/api/auth/token", headers={"Origin": "http://attacker.com"})
        self.assertEqual(res_bad.status_code, 403)

        res_good = self.client.get("/api/auth/token", headers={"Origin": "http://127.0.0.1:8888"})
        self.assertEqual(res_good.status_code, 200)
        data = res_good.json()
        self.assertIn("token", data)
        self.assertTrue(security.verify_session_token(data["token"]))

    def test_dry_run_safety_harness(self):
        """Dry-run harness execution must generate structured simulation logs without live commands."""
        adapter = ClaudeCodeAdapter()
        card = {
            "id": "test-card-001",
            "title": "Audit Dockerfile and Kubernetes manifests",
            "description": "Check root containers and secret exposures",
            "recommended_skills": ["container-hardening", "pod-access-control"],
            "dry_run": True
        }
        agent = {
            "id": "devsecops",
            "name": "Gears",
            "role": "DevSecOps & Cloud Security",
            "model": "gpt-4o"
        }
        settings = {"dry_run_default": True}

        chunks_received = []

        async def log_collector(chunk):
            chunks_received.append(chunk)

        result = asyncio.run(adapter.execute_task(card, agent, settings, log_collector))

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "dry_run")
        self.assertTrue(len(chunks_received) >= 4)
        types = [c["type"] for c in chunks_received]
        self.assertIn("thought", types)
        self.assertIn("tool_call", types)
        self.assertIn("output", types)

    def test_api_state_and_cards(self):
        """API /api/state and /api/cards endpoint validation."""
        res_state = self.client.get("/api/state")
        self.assertEqual(res_state.status_code, 200)
        state_data = res_state.json()
        self.assertIn("agents", state_data)
        self.assertIn("pentest", state_data["agents"])
        self.assertIn("appsec", state_data["agents"])
        self.assertIn("devsecops", state_data["agents"])

        card_payload = {
            "title": "Perform penetration test on web payment gateway",
            "description": "SQL injection and IDOR testing on checkout",
            "dry_run": True
        }
        res_card = self.client.post("/api/cards", json=card_payload)
        self.assertEqual(res_card.status_code, 200)
        card_res = res_card.json()
        self.assertIn("id", card_res)
        self.assertEqual(card_res["assigned_agent"], "pentest")
        self.assertTrue(card_res["dry_run"])

    def test_api_triage_bridge(self):
        """API /api/triage endpoint validation."""
        res = self.client.post("/api/triage", json={"query": "Static code analysis with Semgrep and CodeQL"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["recommended_agent_id"], "appsec")
        self.assertIn("primary_skills", data)

    def test_settings_deep_update_preserves_custom_models(self):
        """Updating one agent model must not erase custom_models_list or other agent models."""
        sm = OfficeStateManager()
        original_models = sm.settings.get("agent_models", {}).get("custom_models_list", [])
        self.assertTrue(len(original_models) > 0, "Initial custom_models_list should not be empty")

        sm.save_settings({"agent_models": {"pentest": "custom-claude-test-model"}})

        updated = sm.settings.get("agent_models", {})
        self.assertEqual(updated.get("pentest"), "custom-claude-test-model")
        self.assertIn("custom_models_list", updated, "custom_models_list must be preserved after update")
        self.assertEqual(updated["custom_models_list"], original_models)

    def test_agent_assignment_fidelity_no_stealing(self):
        """When an agent is busy, newly queued tasks assigned to them must wait and NOT be stolen."""
        async def _test():
            sm = OfficeStateManager()
            sm.agents["pentest"]["status"] = "working"

            card = await sm.add_card("Exploit PoC test", assigned_agent="pentest")
            await asyncio.sleep(0.05)

            card_record = sm.cards[card["id"]]
            self.assertEqual(card_record["assigned_agent"], "pentest")
            self.assertEqual(card_record["status"], "queued")
            # AppSec and DevSecOps must not have taken it
            self.assertNotEqual(sm.agents["appsec"].get("current_card_id"), card["id"])
            self.assertNotEqual(sm.agents["devsecops"].get("current_card_id"), card["id"])

        asyncio.run(_test())

    def test_fifo_queue_concurrency_limit(self):
        """Burst dispatch must enforce max_parallel=2 workers without race conditions."""
        async def _test():
            sm = OfficeStateManager()
            sm.max_parallel = 2

            for i in range(5):
                agent = ["pentest", "appsec", "devsecops"][i % 3]
                await sm.add_card(f"Burst Task {i}", assigned_agent=agent)

            await asyncio.sleep(0.1)

            active_workers = sum(1 for a in sm.agents.values() if a["status"] in ["walking", "working", "alert"])
            self.assertLessEqual(active_workers, 2)
            self.assertEqual(active_workers, 2)
            self.assertEqual(len(sm.card_queue), 3)

        asyncio.run(_test())

    def test_cancel_card_cleans_up_agent(self):
        """Cancelling a card must reset agent to idle and trigger waiting cards."""
        async def _test():
            sm = OfficeStateManager()
            c1 = await sm.add_card("Task to cancel", assigned_agent="pentest")
            await asyncio.sleep(0.05)

            success = await sm.cancel_card(c1["id"])
            self.assertTrue(success)
            self.assertEqual(sm.cards[c1["id"]]["status"], "cancelled")
            self.assertEqual(sm.agents["pentest"]["status"], "idle")
            self.assertIsNone(sm.agents["pentest"]["current_card_id"])

        asyncio.run(_test())

    def test_websocket_handshake_success(self):
        """WebSocket connection with valid origin and session token succeeds."""
        with self.client.websocket_connect(
            f"/ws?token={self.token}",
            headers={"Origin": "http://127.0.0.1:8888"}
        ) as ws:
            initial_msg = ws.receive_json()
            self.assertEqual(initial_msg.get("type"), "state_sync")
            self.assertIn("agents", initial_msg.get("data", {}))

    def test_websocket_handshake_rejected_untrusted_origin(self):
        """WebSocket connection from untrusted origin is closed with 1008 policy violation."""
        from starlette.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect) as cm:
            with self.client.websocket_connect(
                f"/ws?token={self.token}",
                headers={"Origin": "http://evil-attacker.com"}
            ):
                pass
        self.assertEqual(cm.exception.code, 1008)

    def test_websocket_handshake_rejected_invalid_token(self):
        """WebSocket connection with invalid token is closed with 1008 policy violation."""
        from starlette.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect) as cm:
            with self.client.websocket_connect(
                "/ws?token=bogus_token",
                headers={"Origin": "http://127.0.0.1:8888"}
            ):
                pass
        self.assertEqual(cm.exception.code, 1008)


if __name__ == "__main__":
    unittest.main()
