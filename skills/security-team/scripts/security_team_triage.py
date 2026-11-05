#!/usr/bin/env python3
"""
Security Team Triage Utility
Analyzes security tasks and recommends optimal roles, workflows, and sub-skills.
"""

import sys
import json
import re

ROLE_MAPPINGS = {
    "pentest": {
        "role": "Penetration Tester",
        "description": "Black-box/gray-box penetration testing of web, API, and network targets",
        "keywords": [r"pentest", r"penetration test", r"burp", r"nmap", r"sqlmap", r"xss", r"sqli", r"ssrf", r"idor", r"bola", r"exploit", r"poc", r"bypass waf"],
        "recommended_skills": [
            "security-audit",
            "web-app-pentest",
            "api-security-testing",
            "network-pentest",
            "waf-bypass-techniques",
            "autonomous-pentest-scanner",
            "pentest-workflow",
            "pentest-quick-checklist"
        ]
    },
    "web3": {
        "role": "Web3 & Blockchain Security Auditor",
        "description": "Smart contract security audit, invariant fuzzing, DeFi economic flaw analysis, and on-chain incident tracing",
        "keywords": [r"solidity", r"smart contract", r"web3", r"fizz", r"echidna", r"medusa", r"foundry", r"reentrancy", r"defi", r"flash loan", r"on-chain", r"blockchain", r"token", r"wad", r"ray", r"0x[a-fA-F0-9]{40}"],
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
            "dimensional-analysis"
        ]
    },
    "ai_redteam": {
        "role": "AI & LLM Red Teamer",
        "description": "AI/LLM application security, jailbreaking, prompt injection, and agentic tool safety",
        "keywords": [r"ai red team", r"prompt injection", r"jailbreak", r"llm", r"agentic", r"system prompt", r"rag", r"tool poisoning", r"excessive agency", r"model security", r"owasp llm"],
        "recommended_skills": [
            "ai-redteam",
            "16-ai-llm-security",
            "agentic-actions-auditor",
            "prompt-enhancement",
            "claude-mythos-emulation"
        ]
    },
    "appsec": {
        "role": "AppSec Engineer",
        "description": "Source code security review, SAST, threat modeling, and false-positive verification",
        "keywords": [r"code review", r"source audit", r"codebase", r"sast", r"semgrep", r"codeql", r"false positive", r"patch", r"invariant", r"secure code"],
        "recommended_skills": [
            "security-audit",
            "fp-check",
            "trailmark",
            "static-analysis",
            "c-review",
            "rust-review",
            "variant-analysis",
            "patching-bugs",
            "prove-patch",
            "vulnerability-triage-brocards"
        ]
    },
    "red_team": {
        "role": "Red Team",
        "description": "Adversary simulation, Active Directory abuse, stealth lateral movement, and C2 operations",
        "keywords": [r"red team", r"active directory", r"bloodhound", r"kerberoast", r"dpapi", r"dcsync", r"lateral movement", r"c2", r"privesc", r"adversary simulation", r"14-red-team-ops"],
        "recommended_skills": [
            "abusing-dpapi-for-credential-access",
            "exploiting-active-directory-with-bloodhound",
            "moving-laterally-with-netexec",
            "advanced-attack-chains",
            "ctf-kernel-exploitation",
            "14-red-team-ops"
        ]
    },
    "blue_team": {
        "role": "Blue Team / SOC Analyst",
        "description": "Threat detection engineering, SIEM/EDR log analysis, and system hardening",
        "keywords": [r"blue team", r"soc", r"siem", r"splunk", r"sigma", r"yara", r"suricata", r"detect", r"monitor", r"harden", r"rule", r"csoc"],
        "recommended_skills": [
            "building-detection-rules-with-sigma",
            "yara-rule-authoring",
            "triaging-security-alerts-in-splunk",
            "detecting-living-off-the-land-attacks",
            "configuring-suricata-for-network-monitoring",
            "11-csoc-automation"
        ]
    },
    "devsecops": {
        "role": "DevSecOps & Cloud Security",
        "description": "CI/CD pipeline security, container hardening, Kubernetes, IaC, and supply chain",
        "keywords": [r"devsecops", r"ci/cd", r"github actions", r"docker", r"container", r"kubernetes", r"k8s", r"supply chain", r"sbom", r"terraform", r"gitleaks", r"cloud security"],
        "recommended_skills": [
            "supply-chain-risk-auditor",
            "container-hardening",
            "pod-access-control",
            "agentic-actions-auditor",
            "implementing-secrets-scanning-in-ci-cd",
            "cloud-security-automation"
        ]
    },
    "dfir": {
        "role": "DFIR Specialist",
        "description": "Digital forensics, breach triage, volatile memory analysis, and evidence timelines",
        "keywords": [r"dfir", r"forensic", r"incident response", r"breach", r"compromise", r"volatility", r"kape", r"memory dump", r"pcap", r"ransomware", r"hayabusa"],
        "recommended_skills": [
            "triaging-security-incident-with-ir-playbook",
            "triaging-windows-with-kape",
            "conducting-memory-forensics-with-volatility",
            "generating-forensic-timelines-with-hayabusa",
            "forensics-triage"
        ]
    },
    "threat_intel": {
        "role": "Threat Intelligence Analyst",
        "description": "Threat actor profiling, IOC pivot analysis, STIX/TAXII enrichment, and threat hunting",
        "keywords": [r"threat intel", r"cti", r"ioc", r"mitre", r"att&ck", r"virustotal", r"actor", r"apt", r"hunting", r"misp"],
        "recommended_skills": [
            "threat-intelligence",
            "mapping-mitre-attack-techniques",
            "tracking-threat-actor-infrastructure",
            "hunting-for-beaconing-with-frequency-analysis",
            "threat-intel-fusion"
        ]
    },
    "governance": {
        "role": "Purple Team & CISO Governance Lead",
        "description": "Executive cyber-risk reporting, regulatory compliance (NIST/ISO/PCI), and post-pentest Shannon manifests",
        "keywords": [r"ciso", r"governance", r"compliance", r"nist", r"iso 27001", r"pci dss", r"executive report", r"board", r"purple team", r"post-pentest"],
        "recommended_skills": [
            "cybersecurity-pro",
            "performing-purple-team-atomic-testing",
            "22-purple-team",
            "19-grc-compliance"
        ]
    }
}

def triage(text: str):
    matches = {}
    lower_text = text.lower()
    for key, data in ROLE_MAPPINGS.items():
        score = 0
        matched_kw = []
        for kw in data["keywords"]:
            if re.search(r"\b" + kw + r"\b", lower_text):
                score += 1
                matched_kw.append(kw)
        if score > 0:
            matches[key] = {
                "role": data["role"],
                "score": score,
                "matched_keywords": matched_kw,
                "recommended_skills": data["recommended_skills"]
            }

    # If no specific matches, default to Lead Pentest + AppSec
    if not matches:
        return {
            "status": "general_security",
            "primary_role": "Penetration Tester & AppSec Engineer",
            "recommended_skills": ["security-audit", "web-app-pentest", "fp-check"]
        }

    sorted_matches = sorted(matches.values(), key=lambda x: x["score"], reverse=True)
    primary = sorted_matches[0]
    secondary = sorted_matches[1] if len(sorted_matches) > 1 else None

    return {
        "status": "matched",
        "primary_role": primary["role"],
        "primary_skills": primary["recommended_skills"],
        "secondary_role": secondary["role"] if secondary else None,
        "secondary_skills": secondary["recommended_skills"] if secondary else [],
        "all_matches": sorted_matches
    }

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Perform a web application penetration test and code review"
    result = triage(query)
    print(json.dumps(result, indent=2))
