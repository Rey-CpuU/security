"""
Triage Bridge for 8-Bit Cyber Operations Office GUI.
Integrates directly with scripts/security_team_triage.py (v2.1.1) to classify tasks
and route them to the most suitable agent workstation.
"""

import os
import sys
from typing import Dict, Any, Optional

# Ensure repository root is on sys.path to import scripts package
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from scripts import security_team_triage as triage_module
except ImportError:
    # Fallback to direct import if running in standalone mode
    import security_team_triage as triage_module

# Mapping from triage role keys or names to MVP character IDs
MVP_ROLE_TO_AGENT: Dict[str, str] = {
    "pentest": "pentest",
    "red_team": "pentest",
    "threat_intel": "pentest",
    "web3": "pentest",
    "ai_red_team": "pentest",
    "appsec": "appsec",
    "dfir": "appsec",
    "ciso": "appsec",
    "devsecops": "devsecops",
    "blue_team": "devsecops",
}


def map_triage_to_agent_id(triage_result: Dict[str, Any]) -> str:
    """
    Resolve the recommended agent ID for Phase 1 MVP (pentest, appsec, devsecops).
    """
    # 1. Check all_matches role_key if available
    matches = triage_result.get("all_matches", [])
    if matches and isinstance(matches, list):
        top_match = matches[0]
        role_key = top_match.get("role_key", "").lower()
        if role_key in MVP_ROLE_TO_AGENT:
            return MVP_ROLE_TO_AGENT[role_key]

    # 2. Check primary_role string
    primary = str(triage_result.get("primary_role", "")).lower()
    if any(k in primary for k in ["pentest", "penetration", "red team", "exploit", "web3"]):
        return "pentest"
    if any(k in primary for k in ["appsec", "source code", "audit", "review", "patch"]):
        return "appsec"
    if any(k in primary for k in ["devsecops", "cloud", "container", "docker", "k8s", "kubernetes", "ci/cd", "blue team", "soc"]):
        return "devsecops"

    # Default fallback for general security tasks
    return "pentest"


def run_triage(query: str, top_k: int = 3, threshold: int = 1) -> Dict[str, Any]:
    """
    Execute triage analysis on the task query and format for GUI card dispatch.
    """
    if not query or not str(query).strip():
        query = "General cyber security inspection and hardening"

    raw_result = triage_module.triage(str(query), top_k=top_k, threshold=threshold)
    agent_id = map_triage_to_agent_id(raw_result)

    primary_role = raw_result.get("primary_role", "Security Specialist")
    primary_skills = raw_result.get("primary_skills", [])
    secondary_role = raw_result.get("secondary_role")
    secondary_skills = raw_result.get("secondary_skills", [])

    return {
        "query": query,
        "recommended_agent_id": agent_id,
        "recommended_role": primary_role,
        "primary_skills": primary_skills,
        "secondary_role": secondary_role,
        "secondary_skills": secondary_skills,
        "status": raw_result.get("status", "matched"),
        "raw_triage": raw_result
    }
