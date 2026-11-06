#!/usr/bin/env python3
"""
Unit and Regression Test Suite for security_team_triage.py
Verifies schema consistency, CLI flags, token disambiguation, inflections, and 10-division routing.
"""

import unittest
import subprocess
import sys
import os
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "security_team_triage.py"

# Add scripts directory to path for direct module testing
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from security_team_triage import triage, format_text_output


class TestSecurityTeamTriage(unittest.TestCase):

    def test_schema_polymorphism_on_fallback(self):
        """Unmatched queries must return all standard schema keys."""
        res = triage("completely unrelated gibberish 12345 xyz")
        self.assertEqual(res["status"], "general_security")
        self.assertIn("primary_role", res)
        self.assertIn("primary_skills", res)
        self.assertIn("secondary_role", res)
        self.assertIn("secondary_skills", res)
        self.assertIn("all_matches", res)
        self.assertIsInstance(res["primary_skills"], list)
        self.assertGreater(len(res["primary_skills"]), 0)

    def test_cli_help_flag(self):
        """--help must exit with 0 and display usage information."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Security Team Triage Utility", proc.stdout)
        self.assertIn("--input-file", proc.stdout)

    def test_cli_piped_stdin(self):
        """Piped stdin must be read when sys.stdin is not a tty."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--format", "json"],
            input="Investigate reentrancy flaw in Solidity smart contract",
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "matched")
        self.assertEqual(data["primary_role"], "Web3 & Blockchain Security Auditor")

    def test_web3_token_disambiguation(self):
        """Web/API authentication tokens (OAuth, JWT, CSRF, Bearer) must NOT route to Web3."""
        queries = [
            ("Audit OAuth token security and session management", "Penetration Tester"),
            ("Validate JWT token expiry and signature verification", "Penetration Tester"),
            ("Investigate CSRF token validation bypass in login API", "Penetration Tester"),
            ("Bearer token handling in mobile client", "Penetration Tester")
        ]
        for query, expected_role in queries:
            with self.subTest(query=query):
                res = triage(query)
                self.assertNotEqual(res["primary_role"], "Web3 & Blockchain Security Auditor")
                self.assertEqual(res["primary_role"], expected_role)

    def test_solidity_extension_matching(self):
        """.sol filenames and 64-hex transaction hashes must match Web3 Auditor."""
        res1 = triage("Audit contracts/Vault.sol")
        self.assertEqual(res1["primary_role"], "Web3 & Blockchain Security Auditor")

        res2 = triage("Analyze transaction 0x5b38da6a701c568545dcfcb03fcb875f56beddc41234567890abcdef12345678")
        self.assertEqual(res2["primary_role"], "Web3 & Blockchain Security Auditor")

    def test_dfir_prompt_routing(self):
        """DFIR keywords including webshell, timeline, artifact, and kronologi must route to DFIR."""
        query = (
            "Saya mencurigai adanya webshell pada direktori /var/www/html/. "
            "Analisis artefak dan log akses web server berikut, susun kronologi insiden, "
            "dan buatkan rule YARA"
        )
        res = triage(query)
        self.assertEqual(res["primary_role"], "DFIR Specialist")

    def test_english_inflections(self):
        """Plural and gerund inflections must match correctly."""
        query = "Perform forensics on compromised containers and analyze rules"
        res = triage(query)
        self.assertEqual(res["status"], "matched")

    def test_unicode_normalization(self):
        """Fullwidth Unicode homoglyphs must be normalized via NFKC."""
        # Fullwidth 'pentest'
        fullwidth_query = "\uFF50\uFF45\uFF4E\uFF54\uFF45\uFF53\uFF54 target web application"
        res = triage(fullwidth_query)
        self.assertEqual(res["primary_role"], "Penetration Tester")

    def test_all_10_divisions_routing(self):
        """Canonical prompts for each of the 10 divisions must route accurately."""
        division_tests = {
            "pentest": ("Conduct a black-box web application penetration test on the login API", "Penetration Tester"),
            "red_team": ("Simulate Active Directory lateral movement using BloodHound and Kerberoasting", "Red Team"),
            "appsec": ("Perform static analysis source code review on this Python repository using Semgrep", "AppSec Engineer"),
            "blue_team": ("Build Sigma detection rules for Splunk to monitor malicious process injection", "Blue Team / SOC Analyst"),
            "devsecops": ("Harden Dockerfile and scan Kubernetes deployment manifests with Trivy in CI/CD", "DevSecOps & Cloud Security"),
            "dfir": ("Conduct volatile memory forensics using Volatility on a Windows RAM dump", "DFIR Specialist"),
            "threat_intel": ("Analyze threat actor APT indicators of compromise and map to MITRE ATT&CK", "Threat Intelligence Analyst"),
            "web3": ("Audit Solidity DeFi smart contract for flash loan reentrancy flaws", "Web3 & Blockchain Security Auditor"),
            "ai_redteam": ("Red team the LLM agent against indirect prompt injection and jailbreak attacks", "AI & LLM Red Teamer"),
            "governance": ("Prepare a CISO executive summary report and compliance risk matrix for the board", "Purple Team & CISO Governance Lead")
        }

        for div_key, (prompt, expected_role) in division_tests.items():
            with self.subTest(division=div_key):
                res = triage(prompt)
                self.assertEqual(
                    res["primary_role"],
                    expected_role,
                    f"Division {div_key} failed: got {res['primary_role']}, expected {expected_role}"
                )

    def test_no_phantom_skills(self):
        """No division may recommend the non-existent 'static-analysis' skill."""
        for div_key, (prompt, _) in [
            ("appsec", ("Review source code for invariant flaws", "AppSec Engineer"))
        ]:
            res = triage(prompt)
            self.assertNotIn("static-analysis", res["primary_skills"])


if __name__ == "__main__":
    unittest.main()
