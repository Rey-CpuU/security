#!/usr/bin/env python3
"""
Security Team Triage Utility (Production Hardened)
Analyzes security tasks and recommends optimal roles, workflows, and sub-skills.
Part of the security-team skill ecosystem.
"""

import sys
import json
import re
import os
import argparse
import unicodedata
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output on Windows terminals to prevent UnicodeEncodeError with cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VERSION = "2.2.0"

ROLE_MAPPINGS = {
    "pentest": {
        "role": "Penetration Tester",
        "description": "Black-box/gray-box penetration testing of web, API, and network targets",
        "keywords": [
            r"pentest(?:ing)?", r"penetration\s+test(?:ing)?", r"burp", r"nmap", r"sqlmap",
            r"xss", r"sqli", r"ssrf", r"idor", r"bola", r"exploit(?:s|ation|ing)?", r"poc",
            r"bypass\s+waf", r"vulnerabilit(?:y|ies)", r"cve(?:s)?",
            r"sql\s+injection", r"jwt", r"oauth", r"csrf", r"session", r"bearer\s+token", r"auth"
        ],
        "default_secondary": "appsec",
        "recommended_skills": [
            "security-audit",
            "web-app-pentest",
            "api-security-testing",
            "network-pentest",
            "waf-bypass-techniques",
            "autonomous-pentest-scanner",
            "02-vulnerability-scanner",
            "03-exploit-development",
            "08-network-security",
            "17-mobile-security",
            "pentest-workflow",
            "pentest-quick-checklist"
        ]
    },
    "red_team": {
        "role": "Red Team",
        "description": "Adversary simulation, Active Directory abuse, stealth lateral movement, and C2 operations",
        "keywords": [
            r"red\s+team", r"active\s+directory", r"bloodhound", r"kerberoast(?:ing)?", r"dpapi",
            r"dcsync", r"lateral\s+movement", r"c2", r"privesc", r"adversary\s+simulation",
            r"14-red-team-ops"
        ],
        "default_secondary": "threat_intel",
        "recommended_skills": [
            "abusing-dpapi-for-credential-access",
            "exploiting-active-directory-with-bloodhound",
            "moving-laterally-with-netexec",
            "advanced-attack-chains",
            "ctf-kernel-exploitation",
            "03-exploit-development",
            "14-red-team-ops"
        ]
    },
    "appsec": {
        "role": "AppSec Engineer",
        "description": "Source code security review, SAST, threat modeling, and false-positive verification",
        "keywords": [
            r"code\s+review", r"source\s+audit", r"codebase", r"sast", r"semgrep", r"codeql",
            r"false\s+positive", r"patch(?:ing|es)?", r"invariant(?:s)?", r"secure\s+code",
            r"source\s+code"
        ],
        "default_secondary": "pentest",
        "recommended_skills": [
            "security-audit",
            "fp-check",
            "trailmark",
            "semgrep",
            "codeql",
            "entry-point-analyzer",
            "02-vulnerability-scanner",
            "c-review",
            "rust-review",
            "variant-analysis",
            "patching-bugs",
            "prove-patch",
            "vulnerability-triage-brocards"
        ]
    },
    "blue_team": {
        "role": "Blue Team / SOC Analyst",
        "description": "Threat detection engineering, SIEM/EDR log analysis, and system hardening",
        "keywords": [
            r"blue\s+team", r"soc", r"siem", r"splunk", r"sigma", r"yara", r"suricata",
            r"detect(?:ion|ing|s)?", r"monitor(?:ing)?", r"harden(?:ing)?", r"rules?", r"csoc"
        ],
        "default_secondary": "threat_intel",
        "recommended_skills": [
            "building-detection-rules-with-sigma",
            "yara-rule-authoring",
            "triaging-security-alerts-in-splunk",
            "detecting-living-off-the-land-attacks",
            "configuring-suricata-for-network-monitoring",
            "08-network-security",
            "11-csoc-automation",
            "12-log-analysis",
            "15-blue-team-defense"
        ]
    },
    "devsecops": {
        "role": "DevSecOps & Cloud Security",
        "description": "CI/CD pipeline security, container hardening, Kubernetes, IaC, and supply chain",
        "keywords": [
            r"devsecops", r"ci[/-]cd", r"github\s+actions", r"docker(?:file|-compose)?", r"container(?:s|ized|ization)?",
            r"kubernetes", r"k8s", r"supply\s+chain", r"sbom", r"terraform", r"gitleaks",
            r"cloud\s+security", r"jenkins", r"gitlab\s*ci", r"trivy", r"helm"
        ],
        "default_secondary": "appsec",
        "recommended_skills": [
            "supply-chain-risk-auditor",
            "container-hardening",
            "pod-access-control",
            "agentic-actions-auditor",
            "implementing-secrets-scanning-in-ci-cd",
            "10-cloud-security",
            "20-supply-chain-security",
            "cloud-security-automation"
        ]
    },
    "dfir": {
        "role": "DFIR Specialist",
        "description": "Digital forensics, breach triage, volatile memory analysis, and evidence timelines",
        "keywords": [
            r"dfir", r"forensics?", r"incident\s+response", r"breach(?:es|ed)?",
            r"compromis(?:e|ed|ing)?", r"volatility", r"kape", r"memory\s+dump", r"pcap",
            r"ransomware", r"hayabusa", r"webshell", r"timeline", r"artifact(?:s)?",
            r"artefak", r"kronologi", r"malware"
        ],
        "default_secondary": "blue_team",
        "recommended_skills": [
            "triaging-security-incident-with-ir-playbook",
            "triaging-windows-with-kape",
            "conducting-memory-forensics-with-volatility",
            "generating-forensic-timelines-with-hayabusa",
            "forensics-triage",
            "04-reverse-engineering",
            "05-malware-analysis",
            "07-incident-response",
            "12-log-analysis"
        ]
    },
    "threat_intel": {
        "role": "Threat Intelligence Analyst",
        "description": "Threat actor profiling, IOC pivot analysis, STIX/TAXII enrichment, and threat hunting",
        "keywords": [
            r"threat\s+intel(?:ligence)?", r"cti", r"ioc(?:s)?", r"mitre", r"att&ck",
            r"virustotal", r"threat\s+actor(?:s)?", r"actor(?:s)?", r"apt", r"hunting", r"misp"
        ],
        "default_secondary": "blue_team",
        "recommended_skills": [
            "threat-intelligence",
            "mapping-mitre-attack-techniques",
            "tracking-threat-actor-infrastructure",
            "hunting-for-beaconing-with-frequency-analysis",
            "threat-intel-fusion",
            "06-threat-hunting",
            "21-threat-intelligence"
        ]
    },
    "web3": {
        "role": "Web3 & Blockchain Security Auditor",
        "description": "Smart contract security audit, invariant fuzzing, DeFi economic flaw analysis, and on-chain incident tracing",
        "keywords": [
            r"solidity", r"smart\s+contract(?:s)?", r"web3", r"fizz", r"echidna", r"medusa",
            r"foundry", r"reentrancy", r"defi", r"flash\s+loan", r"on-chain", r"blockchain",
            r"(?:erc[-_]?\d+|erc20|erc721|tokenomics|crypto\s+token|token\s+contract|token\s+mint|token\s+burn)",
            r"wad", r"ray", r"0x[a-fA-F0-9]{40}\b", r"0x[a-fA-F0-9]{64}\b", r"[\w\-./\\]+\.sol\b"
        ],
        "default_secondary": "appsec",
        "recommended_skills": [
            "contract-auditor",
            "solidity-auditor",
            "fizz",
            "fizz-convert",
            "fizz-sync",
            "x-ray",
            "client-auditor",
            "exploit-investigator",
            "smart-contract-audit",
            "dimensional-analysis",
            "13-crypto-analysis"
        ]
    },
    "ai_redteam": {
        "role": "AI & LLM Red Teamer",
        "description": "AI/LLM application security, jailbreaking, prompt injection, and agentic tool safety",
        "keywords": [
            r"ai\s+red\s+team", r"prompt\s+injection", r"jailbreak(?:ing)?", r"llm(?:s)?",
            r"agentic", r"system\s+prompt", r"rag", r"tool\s+poisoning", r"excessive\s+agency",
            r"model\s+security", r"owasp\s+llm"
        ],
        "default_secondary": "appsec",
        "recommended_skills": [
            "ai-redteam",
            "16-ai-llm-security",
            "agentic-actions-auditor",
            "prompt-enhancement",
            "claude-mythos-emulation"
        ]
    },
    "governance": {
        "role": "Purple Team & CISO Governance Lead",
        "description": "Executive cyber-risk reporting, regulatory compliance (NIST/ISO/PCI), and post-pentest Shannon manifests",
        "keywords": [
            r"ciso", r"governance", r"compliance", r"nist", r"iso\s*27001", r"pci\s*dss",
            r"executive\s+report", r"board", r"purple\s+team", r"post-pentest",
            r"detection\s+defenses?", r"tune\s+defenses?", r"tabletop"
        ],
        "default_secondary": "appsec",
        "recommended_skills": [
            "cybersecurity-pro",
            "performing-purple-team-atomic-testing",
            "22-purple-team",
            "19-grc-compliance"
        ]
    }
}

# Precompile regexes for optimal throughput
COMPILED_PATTERNS = {}
for role_key, data in ROLE_MAPPINGS.items():
    compiled_list = []
    for kw in data["keywords"]:
        pattern_str = r"\b" + kw if not kw.startswith(r"\b") and not kw.startswith(r"[\w") else kw
        if not pattern_str.endswith(r"\b"):
            pattern_str = pattern_str + r"\b"
        compiled_list.append((kw, re.compile(pattern_str, re.IGNORECASE)))
    COMPILED_PATTERNS[role_key] = compiled_list


def triage(text: str, top_k: int = 2, threshold: int = 1) -> Dict[str, Any]:
    if not isinstance(text, str):
        text = str(text or "")

    # Normalize Unicode characters (NFKC) to defeat homoglyph and fullwidth evasion
    normalized_text = unicodedata.normalize("NFKC", text)
    lower_text = normalized_text.lower()

    matches = {}

    for key, data in ROLE_MAPPINGS.items():
        score = 0
        matched_kw = []
        for kw_str, compiled_rx in COMPILED_PATTERNS[key]:
            if compiled_rx.search(lower_text):
                score += 1
                matched_kw.append(kw_str)
        if score >= threshold:
            matches[key] = {
                "role_key": key,
                "role": data["role"],
                "score": score,
                "matched_keywords": matched_kw,
                "recommended_skills": data["recommended_skills"],
                "default_secondary": data.get("default_secondary")
            }

    # If no specific matches, default to Lead Pentest + AppSec fallback with consistent schema
    if not matches:
        return {
            "status": "general_security",
            "primary_role": "Penetration Tester & AppSec Engineer",
            "primary_skills": ["security-audit", "web-app-pentest", "fp-check", "02-vulnerability-scanner"],
            "secondary_role": None,
            "secondary_skills": [],
            "all_matches": []
        }

    sorted_matches = sorted(matches.values(), key=lambda x: x["score"], reverse=True)
    primary = sorted_matches[0]

    # Resolve secondary role: use 2nd matched division if available; otherwise use default paired division
    if len(sorted_matches) > 1:
        secondary = sorted_matches[1]
        secondary_role = secondary["role"]
        secondary_skills = secondary["recommended_skills"]
    elif primary.get("default_secondary") and primary["default_secondary"] in ROLE_MAPPINGS:
        sec_data = ROLE_MAPPINGS[primary["default_secondary"]]
        secondary_role = sec_data["role"]
        secondary_skills = sec_data["recommended_skills"]
    else:
        secondary_role = None
        secondary_skills = []

    return {
        "status": "matched",
        "primary_role": primary["role"],
        "primary_skills": primary["recommended_skills"],
        "secondary_role": secondary_role,
        "secondary_skills": secondary_skills,
        "all_matches": sorted_matches[:top_k]
    }


def format_text_output(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("🛡️  SECURITY TEAM TRIAGE REPORT")
    lines.append("=" * 60)
    lines.append(f"Status        : {result.get('status', 'unknown').upper()}")
    lines.append(f"Lead Role     : {result.get('primary_role')}")
    if result.get("secondary_role"):
        lines.append(f"Support Role  : {result.get('secondary_role')}")
    lines.append("-" * 60)
    lines.append("📦 Primary Skills to Activate:")
    for skill in result.get("primary_skills", []):
        lines.append(f"  • {skill}")
    if result.get("secondary_skills"):
        lines.append("\n🤝 Supporting Skills:")
        for skill in result.get("secondary_skills", []):
            lines.append(f"  • {skill}")
    if result.get("all_matches"):
        lines.append("-" * 60)
        lines.append("📊 Division Match Details:")
        for m in result.get("all_matches", []):
            kws = ", ".join(m.get("matched_keywords", []))
            lines.append(f"  [{m.get('role')}] Score: {m.get('score')} | Keywords: {kws}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Security Team Triage Utility: Analyzes security tasks and recommends optimal roles and sub-skills."
    )
    parser.add_argument(
        "positional_query",
        nargs="*",
        help="Security task query or objective (can be multiple words)"
    )
    parser.add_argument(
        "-q", "--query",
        dest="flag_query",
        type=str,
        default=None,
        help="Explicit security task query string"
    )
    parser.add_argument(
        "-f", "--input-file",
        dest="input_file",
        type=str,
        default=None,
        help="Path to file containing prompt, logs, or codebase snippet to triage"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format: json (default) or text (human-readable)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=2,
        help="Maximum number of matched divisions to return in all_matches (default: 2)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=1,
        help="Minimum keyword match score required for a division (default: 1)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"security_team_triage {VERSION}"
    )

    args = parser.parse_args()

    # Determine input source
    query_text = ""
    if args.input_file:
        if not os.path.exists(args.input_file):
            sys.stderr.write(f"Error: Input file '{args.input_file}' not found.\n")
            sys.exit(1)
        try:
            with open(args.input_file, "r", encoding="utf-8", errors="replace") as f:
                query_text = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading file '{args.input_file}': {e}\n")
            sys.exit(1)
    elif args.flag_query:
        query_text = args.flag_query
    elif args.positional_query:
        query_text = " ".join(args.positional_query)
    elif not sys.stdin.isatty():
        # Read from piped stdin
        query_text = sys.stdin.read()
    else:
        query_text = "Perform a web application penetration test and code review"

    result = triage(query_text, top_k=args.top_k, threshold=args.threshold)

    if args.format == "text":
        print(format_text_output(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
