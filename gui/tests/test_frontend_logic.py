"""
Frontend Assets & Integration Logic Unit Tests for 8-Bit Cyber Operations Office GUI.
Verifies HTML structure, static assets integrity, bundled fonts, offline readiness, and triage mappings.
"""

import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GUI_DIR = os.path.join(REPO_ROOT, "gui")
STATIC_DIR = os.path.join(GUI_DIR, "static")


class TestFrontendLogic(unittest.TestCase):
    """Test suite validating frontend assets and structural integrity."""

    def test_static_files_exist(self):
        """All required CSS, JS, and bundled pixel font files must exist locally for 100% offline usage."""
        expected_files = [
            os.path.join(STATIC_DIR, "index.html"),
            os.path.join(STATIC_DIR, "css", "retro_8bit.css"),
            os.path.join(STATIC_DIR, "css", "layout.css"),
            os.path.join(STATIC_DIR, "fonts", "press_start_2p.woff"),
            os.path.join(STATIC_DIR, "fonts", "press_start_2p.ttf"),
            os.path.join(STATIC_DIR, "js", "audio_synth.js"),
            os.path.join(STATIC_DIR, "js", "agent_sprites.js"),
            os.path.join(STATIC_DIR, "js", "office_canvas.js"),
            os.path.join(STATIC_DIR, "js", "task_cards.js"),
            os.path.join(STATIC_DIR, "js", "terminal_hud.js"),
            os.path.join(STATIC_DIR, "js", "websocket_client.js"),
        ]
        for f in expected_files:
            self.assertTrue(os.path.isfile(f), f"Expected file missing: {f}")
            self.assertGreater(os.path.getsize(f), 0, f"File should not be empty: {f}")

    def test_font_face_declared_in_css(self):
        """retro_8bit.css must declare @font-face for PressStart2P referencing local font files."""
        css_file = os.path.join(STATIC_DIR, "css", "retro_8bit.css")
        with open(css_file, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn("@font-face", css)
        self.assertIn("PressStart2P", css)
        self.assertIn("/static/fonts/press_start_2p.woff", css)
        self.assertIn("/static/fonts/press_start_2p.ttf", css)

    def test_index_html_structure(self):
        """index.html must contain all essential office canvas, HUD, and modal elements."""
        index_file = os.path.join(STATIC_DIR, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()

        # Session token injection placeholder
        self.assertIn('name="session-token"', html)
        self.assertIn('__SESSION_TOKEN__', html)

        # CRT Scanlines & Visuals
        self.assertIn('class="crt-overlay"', html)
        self.assertIn('id="officeCanvas"', html)

        # Dispatcher Form
        self.assertIn('id="taskTitleInput"', html)
        self.assertIn('id="taskDescInput"', html)
        self.assertIn('id="taskAgentSelect"', html)
        self.assertIn('id="dryRunCheckbox"', html)
        self.assertIn('id="dispatchTaskBtn"', html)

        # Queue & Terminal
        self.assertIn('id="queueListContainer"', html)
        self.assertIn('id="terminalScreen"', html)

        # Settings Modal
        self.assertIn('id="settingsModalOverlay"', html)
        self.assertIn('id="modelPentest"', html)
        self.assertIn('id="modelAppsec"', html)
        self.assertIn('id="modelDevsecops"', html)

        # Script tags present
        for js_name in [
            "audio_synth.js",
            "agent_sprites.js",
            "office_canvas.js",
            "task_cards.js",
            "terminal_hud.js",
            "websocket_client.js"
        ]:
            self.assertIn(f"/static/js/{js_name}", html)

    def test_zero_external_cdn_dependency(self):
        """index.html, retro_8bit.css, and layout.css must NOT load external fonts or CDN scripts."""
        files_to_check = [
            os.path.join(STATIC_DIR, "index.html"),
            os.path.join(STATIC_DIR, "css", "retro_8bit.css"),
            os.path.join(STATIC_DIR, "css", "layout.css"),
        ]
        external_patterns = [
            r"https?://fonts\.googleapis\.com",
            r"https?://cdnjs\.cloudflare\.com",
            r"https?://cdn\.jsdelivr\.net",
            r"https?://unpkg\.com"
        ]

        for file_path in files_to_check:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in external_patterns:
                    self.assertIsNone(
                        re.search(pattern, content, re.IGNORECASE),
                        f"External CDN dependency detected in {file_path}: {pattern}"
                    )

    def test_audio_synth_methods(self):
        """audio_synth.js must contain Web Audio API oscillator synthesis methods."""
        audio_file = os.path.join(STATIC_DIR, "js", "audio_synth.js")
        with open(audio_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("createOscillator", content)
        self.assertIn("playCoin", content)
        self.assertIn("playAlert", content)
        self.assertIn("playBleep", content)
        self.assertIn("playTypewriter", content)
        self.assertIn("playSuccess", content)

    def test_procedural_sprites_3_mvp_agents(self):
        """agent_sprites.js must implement distinct procedural styling for pentest, appsec, devsecops."""
        sprites_file = os.path.join(STATIC_DIR, "js", "agent_sprites.js")
        with open(sprites_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("pentest", content)
        self.assertIn("appsec", content)
        self.assertIn("devsecops", content)
        self.assertIn("idle", content)
        self.assertIn("walking", content)
        self.assertIn("working", content)
        self.assertIn("alert", content)

    def test_websocket_client_dynamic_host(self):
        """websocket_client.js must use dynamic loc.host rather than hardcoded 8888."""
        ws_file = os.path.join(STATIC_DIR, "js", "websocket_client.js")
        with open(ws_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("CONNECTED (${loc.host})", content)
        self.assertNotIn("CONNECTED (127.0.0.1:8888)", content)

    def test_canvas_smooth_interpolation_and_click_select(self):
        """office_canvas.js must implement smooth movement interpolation and sync taskAgentSelect."""
        canvas_file = os.path.join(STATIC_DIR, "js", "office_canvas.js")
        with open(canvas_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("renderPos", content)
        self.assertIn("taskAgentSelect", content)


if __name__ == "__main__":
    unittest.main()
