"""
Unit Tests for Fase 0: Security & Storage Foundation (SEC-01, SEC-02, SEC-04, SEC-06, SEC-08, SEC-11).
Verifies:
- Windows Credential Manager integration (keyring) & no plaintext fallback
- Dual redaction engine (regex patterns + exact secret memory substrings)
- Host header validation & baseline CSP headers
- Token domain separation (GUI session token vs Agent proxy token)
- Ticket-based WebSocket authentication (burn on single use)
- Backend dispatch gating in POST /api/cards (HTTP 403 on disconnected model)
- LLM Reverse Proxy path allowlist and Anti-SSRF DNS resolution check
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from gui.server import cred_store, redactor, security
from gui.server.app import app
from gui.server.llm_proxy import is_path_allowed, is_ip_safe, verify_url_ssrf_safe
from gui.server.providers import provider_manager, ProviderStatus
from gui.server.state import state_manager


class TestFase0Security(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        security.reset_tokens_for_tests()
        self.session_token = security.get_session_token()
        redactor.clear_registered_secrets()

    # --- 1. Credential Store (SEC-04, LOG-11) ---

    def test_credential_store_crud(self):
        """Persistent keyring operations with target formatting."""
        if not cred_store.is_available():
            self.skipTest("Keyring backend not available on this platform")

        provider = "testprov"
        account_id = "acc-unit-1"
        secret = "test-secret-key-xyz-9876543210"

        # 1. Format target check
        target = cred_store.format_target(provider, account_id)
        self.assertEqual(target, "security-team-gui:testprov:acc-unit-1")

        # 2. Store credential
        saved = cred_store.set_credential(provider, account_id, secret)
        self.assertTrue(saved)

        # 3. Retrieve credential
        retrieved = cred_store.get_credential(provider, account_id)
        self.assertEqual(retrieved, secret)

        # 4. Redactor registration sync check
        self.assertIn(secret, redactor.get_registered_secrets())

        # 5. Active secret check
        active = cred_store.get_active_secret(provider, account_id)
        self.assertEqual(active, secret)

        # 6. Delete credential
        deleted = cred_store.delete_credential(provider, account_id)
        self.assertTrue(deleted)
        self.assertIsNone(cred_store.get_credential(provider, account_id))

    def test_credential_store_in_memory_access_tokens(self):
        """Short-lived access tokens stored strictly in RAM."""
        provider = "gemini"
        account_id = "oauth-work"
        access_token = "ya29.temporary-access-token-12345"

        cred_store.set_access_token(provider, account_id, access_token, expires_in_sec=10)
        got = cred_store.get_access_token(provider, account_id)
        self.assertEqual(got, access_token)

        # Should prefer access token over keyring
        active = cred_store.get_active_secret(provider, account_id)
        self.assertEqual(active, access_token)

    # --- 2. Dual Redaction Engine (SEC-08) ---

    def test_redactor_regex_and_exact_masking(self):
        """Dual redaction masks regex patterns and exact in-memory secrets."""
        # Regex patterns
        anthropic_key = "sk-ant-api03-abcdef1234567890abcdef123456"
        openai_key = "sk-proj-12345678901234567890abcdef"
        gemini_key = "AIzaSyDa-1234567890abcdef1234567890ab"
        bearer_token = "Bearer secret-token-value-1234567890"

        raw_log = f"Keys: Anthropic={anthropic_key}, OpenAI={openai_key}, Google={gemini_key}, Auth={bearer_token}"
        redacted = redactor.redact(raw_log)

        self.assertNotIn(anthropic_key, redacted)
        self.assertNotIn(openai_key, redacted)
        self.assertNotIn(gemini_key, redacted)
        self.assertIn("[REDACTED_API_KEY]", redacted)

        # Exact secret substring redaction
        custom_secret = "CorpSpecialVaultToken9999"
        redactor.register_secret(custom_secret)

        raw_error = f"Upstream error: failed with {custom_secret} at endpoint"
        redacted_error = redactor.redact(raw_error)
        self.assertNotIn(custom_secret, redacted_error)
        self.assertIn("[REDACTED_SECRET]", redacted_error)

    def test_redactor_recursive_object(self):
        """Redact objects recursively across dicts and lists."""
        secret = "secret-token-1234567890"
        redactor.register_secret(secret)

        nested = {
            "user": "tester",
            "keys": [secret, f"Bearer {secret}"],
            "meta": {"token": secret}
        }
        cleaned = redactor.redact_object(nested)
        self.assertEqual(cleaned["user"], "tester")
        self.assertEqual(cleaned["keys"][0], "[REDACTED_SECRET]")
        self.assertEqual(cleaned["meta"]["token"], "[REDACTED_SECRET]")

    # --- 3. Host Validation & CSP (SEC-02) ---

    def test_host_header_rejection(self):
        """Untrusted Host headers are rejected with HTTP 403 (Anti-DNS Rebinding)."""
        res_evil = self.client.get("/api/state", headers={"Host": "evil-attacker.com"})
        self.assertEqual(res_evil.status_code, 403)
        self.assertIn("Untrusted Host Header", res_evil.json()["detail"])

        res_good = self.client.get("/api/state", headers={"Host": "127.0.0.1:8888"})
        self.assertEqual(res_good.status_code, 200)

    def test_baseline_csp_and_security_headers(self):
        """Baseline CSP and framing protection headers present on all responses."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Content-Security-Policy", res.headers)
        csp = res.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")

    # --- 4. Ticket-Based WebSocket Authentication (SEC-11) ---

    def test_ticket_based_websocket_lifecycle(self):
        """WebSocket ticket is single-use: succeeds on first connection and burns on use."""
        # 1. Issue Ticket
        res_ticket = self.client.post(
            "/api/auth/ws-ticket",
            headers={"Origin": "http://127.0.0.1:8888", "X-Security-Team-Token": self.session_token}
        )
        self.assertEqual(res_ticket.status_code, 200)
        data = res_ticket.json()
        self.assertIn("ticket", data)
        ticket = data["ticket"]

        # 2. First WS Connection with Ticket -> SUCCESS
        with self.client.websocket_connect(
            f"/ws?ticket={ticket}",
            headers={"Origin": "http://127.0.0.1:8888"}
        ) as ws:
            msg = ws.receive_json()
            self.assertEqual(msg.get("type"), "state_sync")

        # 3. Second WS Connection with SAME Ticket -> REJECTED (Burned on use)
        from starlette.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect) as cm:
            with self.client.websocket_connect(
                f"/ws?ticket={ticket}",
                headers={"Origin": "http://127.0.0.1:8888"}
            ):
                pass
        self.assertEqual(cm.exception.code, 1008)

    # --- 5. Token Domain Separation (Boundary 1) ---

    def test_token_domain_isolation(self):
        """Agent Proxy Token cannot access Admin /api/*; GUI Session Token cannot access Proxy."""
        agent_token = security.create_agent_proxy_token(
            agent_id="pentest",
            card_id="card-test-1",
            allowed_model_id="claude-3-7-sonnet-20250219"
        )

        # Agent token trying to call admin /api/settings -> 403 Forbidden
        res_admin = self.client.get(
            "/api/settings",
            headers={"Authorization": f"Bearer {agent_token}"}
        )
        self.assertEqual(res_admin.status_code, 403)
        self.assertIn("Admin Route Restricted", res_admin.json()["detail"])

        # GUI session token trying to call /v1/proxy/* -> 403 Forbidden
        res_proxy = self.client.post(
            "/v1/proxy/chat/completions",
            headers={"Authorization": f"Bearer {self.session_token}"},
            json={"model": "claude-3-7-sonnet-20250219", "messages": []}
        )
        self.assertEqual(res_proxy.status_code, 403)
        self.assertIn("Token Domain Mismatch", res_proxy.json()["detail"])

    # --- 6. Backend Dispatch Gating (SEC-01) ---

    def test_backend_dispatch_gating_http_403(self):
        """POST /api/cards rejects tasks for disconnected models with HTTP 403."""
        # DevSecOps is configured with gpt-4o, and OpenAI currently has no accounts (DISCONNECTED)
        res_bad = self.client.post(
            "/api/cards",
            json={
                "title": "Cloud infrastructure audit",
                "assigned_agent": "devsecops",
                "model": "gpt-4o"
            }
        )
        self.assertEqual(res_bad.status_code, 403)
        self.assertIn("model gating", res_bad.json()["detail"].lower())

        # Rex (pentest) uses Claude, which has a CONNECTED account -> 200 OK
        res_good = self.client.post(
            "/api/cards",
            json={
                "title": "Penetration test on web API",
                "assigned_agent": "pentest",
                "model": "claude-3-7-sonnet-20250219"
            }
        )
        self.assertEqual(res_good.status_code, 200)

    # --- 7. Proxy Path Allowlist & Anti-SSRF (SEC-06) ---

    def test_proxy_path_allowlist(self):
        """Proxy allowlist permits only completions, models, and messages; blocks admin/billing."""
        self.assertTrue(is_path_allowed("/v1/chat/completions"))
        self.assertTrue(is_path_allowed("/v1/models"))
        self.assertTrue(is_path_allowed("/v1/messages"))
        self.assertTrue(is_path_allowed("/v1beta/models"))
        self.assertTrue(is_path_allowed("/v1beta/models/gemini-2.5-pro:generateContent"))

        self.assertFalse(is_path_allowed("/v1/files"))
        self.assertFalse(is_path_allowed("/v1/fine_tuning"))
        self.assertFalse(is_path_allowed("/v1/organizations"))
        self.assertFalse(is_path_allowed("/billing"))
        self.assertFalse(is_path_allowed("/admin"))

    def test_proxy_anti_ssrf_and_dns_check(self):
        """Anti-SSRF rejects loopback, RFC1918 private, link-local, and unauthorized domains."""
        # Public allowed host
        safe, _ = verify_url_ssrf_safe("https://api.openai.com/v1/models")
        self.assertTrue(safe)

        # Loopback URL
        safe, err = verify_url_ssrf_safe("http://127.0.0.1:8888/v1/chat/completions")
        self.assertFalse(safe)

        # Unauthorized domain
        safe, err = verify_url_ssrf_safe("https://attacker-domain.com/v1/chat/completions")
        self.assertFalse(safe)
        self.assertIn("not in allowed upstream domains", err)

        # Private IP check
        self.assertFalse(is_ip_safe("127.0.0.1"))
        self.assertFalse(is_ip_safe("10.0.0.1"))
        self.assertFalse(is_ip_safe("192.168.1.1"))
        self.assertFalse(is_ip_safe("169.254.169.254"))
        self.assertFalse(is_ip_safe("::1"))
        self.assertTrue(is_ip_safe("8.8.8.8"))

    def test_ws_ticket_unauthenticated_rejected(self):
        """POST /api/auth/ws-ticket strictly rejects anonymous calls and invalid session tokens with HTTP 401."""
        # 1. Anonymous request without token -> 401
        res_anon = self.client.post("/api/auth/ws-ticket")
        self.assertEqual(res_anon.status_code, 401)
        self.assertIn("Missing or invalid GUI Session Token", res_anon.json()["detail"])

        # 2. Invalid session token -> 401
        res_bad = self.client.post(
            "/api/auth/ws-ticket",
            headers={"X-Security-Team-Token": "bad-session-token-xyz"}
        )
        self.assertEqual(res_bad.status_code, 401)
        self.assertIn("Missing or invalid GUI Session Token", res_bad.json()["detail"])

    def test_in_memory_token_deleted_when_keyring_empty(self):
        """delete_credential successfully clears in-memory access tokens even if not in keyring."""
        provider = "gemini"
        account_id = "oauth-inmem-purge-test"
        cred_store.set_access_token(provider, account_id, "ya29.purge-test-token-12345")
        self.assertIsNotNone(cred_store.get_access_token(provider, account_id))

        # Delete credential
        deleted = cred_store.delete_credential(provider, account_id)
        self.assertTrue(deleted)
        self.assertIsNone(cred_store.get_access_token(provider, account_id))

    def test_gemini_proxy_routing_and_allowlist(self):
        """Proxy allowlist and router allow /gemini/* and /v1beta/models/* paths."""
        self.assertTrue(is_path_allowed("/gemini/v1beta/models"))
        self.assertTrue(is_path_allowed("/v1/proxy/gemini/v1beta/models"))
        self.assertTrue(is_path_allowed("/v1/proxy/gemini/v1beta/models/gemini-2.0-flash:generateContent"))

    def test_card_id_matches_proxy_token_binding(self):
        """Card ID generated by dispatch matches the bound card_id in the agent proxy token."""
        res = self.client.post(
            "/api/cards",
            json={
                "title": "Token binding consistency test",
                "assigned_agent": "pentest",
                "model": "claude-3-7-sonnet-20250219"
            }
        )
        self.assertEqual(res.status_code, 200)
        card = res.json()
        card_id = card["id"]

        # Card response must NOT leak agent_proxy_token to the client
        self.assertNotIn("agent_proxy_token", card)

        # Internal card store has the matching bound proxy token
        internal_card = state_manager.cards.get(card_id)
        self.assertIsNotNone(internal_card)
        proxy_token = internal_card.get("agent_proxy_token")
        self.assertIsNotNone(proxy_token)
        meta = security.verify_agent_proxy_token(proxy_token)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["card_id"], card_id)
        self.assertEqual(meta["allowed_model_id"], "claude-3-7-sonnet-20250219")

    def test_canary_secret_not_leaked(self):
        """Secrets are not leaked into GET /api/state, GET /api/settings, or card listings."""
        canary_secret = "CANARY_SECRET_SUPER_CONFIDENTIAL_123456"
        cred_store.set_credential("gemini", "canary-acc", canary_secret)

        # 1. State snapshot does not leak canary
        res_state = self.client.get("/api/state")
        self.assertEqual(res_state.status_code, 200)
        self.assertNotIn(canary_secret, res_state.text)

        # 2. Settings does not leak canary
        res_settings = self.client.get("/api/settings")
        self.assertEqual(res_settings.status_code, 200)
        self.assertNotIn(canary_secret, res_settings.text)

        # 3. Clean up
        cred_store.delete_credential("gemini", "canary-acc")

    def test_antigravity_heuristic_order(self):
        """Models with 'antigravity' in name resolve to AntigravityProvider even if containing claude/gemini."""
        prov = provider_manager.resolve_provider_for_model("antigravity-claude-session-custom")
        self.assertIsNotNone(prov)
        self.assertEqual(prov.name, "antigravity")

        prov2 = provider_manager.resolve_provider_for_model("antigravity-gemini-session-custom")
        self.assertIsNotNone(prov2)
        self.assertEqual(prov2.name, "antigravity")


if __name__ == "__main__":
    unittest.main()
