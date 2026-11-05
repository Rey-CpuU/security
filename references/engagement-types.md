# Security Team: Engagement Types & Playbooks

This guide specifies the operational configuration for common cybersecurity engagement types and maps them to team roles.

---

## 1. Full Scope Web Application & API Penetration Test
* **Lead Role**: Penetration Tester
* **Supporting Roles**: AppSec Engineer (Source code assistance), Threat Intelligence
* **Objectives**: Identify exploitable vulnerabilities in client-facing applications and API layers.
* **Key Tasks**:
  1. Scope URL endpoints, authentication flows, and user permission matrices.
  2. Perform automated and manual testing for OWASP Top 10 flaws.
  3. Verify access control across different user tiers (Vertical & Horizontal privilege escalation).
  4. Write reproducible PoCs and validate against false positives.
  5. Produce technical vulnerability reports with CVSS scoring.

---

## 2. Web3 Smart Contract & Protocol Security Audit
* **Lead Role**: Web3 & Blockchain Security Auditor
* **Supporting Roles**: AppSec Engineer, Penetration Tester
* **Objectives**: Audit Solidity contracts and DeFi protocols for reentrancy, economic exploits, access control, and arithmetic bugs.
* **Key Tasks**:
  1. Profile protocol architecture and threat models with `x-ray`.
  2. Conduct parallel multi-pass code audits with `solidity-auditor` and `contract-auditor`.
  3. Verify token arithmetic, decimals, and scaling with `dimensional-analysis`.
  4. Scaffold and execute stateful invariant fuzzing campaigns with `fizz` (Echidna / Medusa).
  5. Provide invariant-level patches and test verification.

---

## 3. AI Agent & Large Language Model Red Teaming Assessment
* **Lead Role**: AI & LLM Red Teamer
* **Supporting Roles**: AppSec Engineer, DevSecOps
* **Objectives**: Test LLMs, agentic pipelines, RAG systems, and MCP integrations against prompt injection and autonomous tool abuse.
* **Key Tasks**:
  1. Map input vectors (chat UI, RAG documents, API webhooks, file attachments).
  2. Execute direct and indirect prompt injection attacks (`ai-redteam`, `16-ai-llm-security`).
  3. Test agent tool permissions and sandbox boundaries (`agentic-actions-auditor`).
  4. Attempt system prompt extraction and data exfiltration.
  5. Provide defensive system prompt architecture and output sanitization recommendations.

---

## 4. Source Code Security Audit (White-Box Review)
* **Lead Role**: AppSec Engineer
* **Supporting Roles**: Penetration Tester (Exploitability validation), DevSecOps
* **Objectives**: Inspect application source code, third-party libraries, and configuration files for vulnerabilities.
* **Key Tasks**:
  1. Map architecture and attack surface with `audit-context-building` and `entry-point-analyzer`.
  2. Execute semantic static analysis using `semgrep`, `codeql`, and AST pattern matchers.
  3. Conduct manual taint analysis from untrusted inputs to sensitive sinks.
  4. Verify all candidate findings with `fp-check` to eliminate false positives.
  5. Produce invariant-level patches using `patching-bugs` and `prove-patch`.

---

## 5. Red Team Adversary Simulation (Black-Box APT)
* **Lead Role**: Red Team
* **Supporting Roles**: Threat Intelligence, Penetration Tester
* **Objectives**: Emulate a specific threat actor to test organizational defense readiness and incident response timing.
* **Key Tasks**:
  1. Profile adversary TTPs matching the organization's threat model (MITRE ATT&CK).
  2. Perform initial reconnaissance and credential access.
  3. Map internal network paths using BloodHound.
  4. Test lateral movement and privilege escalation stealthily.
  5. Document attack timelines for purple team debriefing.

---

## 6. Blue Team Defense & SOC Hardening
* **Lead Role**: Blue Team / SOC Analyst
* **Supporting Roles**: Threat Intelligence, DevSecOps
* **Objectives**: Harden perimeter and internal defenses, deploy detection rules, and eliminate blind spots.
* **Key Tasks**:
  1. Review system telemetry and logging policies (Sysmon, Windows Event Logs, CloudTrail).
  2. Write Sigma and YARA rules for high-risk attack techniques.
  3. Baseline normal administrative behavior to suppress noise.
  4. Deploy network filtering and Suricata signatures.

---

## 7. DevSecOps & Supply Chain Security Audit
* **Lead Role**: DevSecOps Engineer
* **Supporting Roles**: AppSec Engineer
* **Objectives**: Secure CI/CD pipelines, container images, Kubernetes clusters, and open-source dependencies.
* **Key Tasks**:
  1. Audit GitHub Actions / GitLab CI workflows for expression injection and runner abuse (`agentic-actions-auditor`).
  2. Scan container images for CVEs and enforce distroless/minimal bases (`container-hardening`).
  3. Audit Kubernetes RBAC policies, service accounts, and Pod Security Standards (`pod-access-control`).
  4. Verify SBOMs, dependency lockfiles, and package integrity (`supply-chain-risk-auditor`).

---

## 8. Digital Forensics & Incident Response (DFIR)
* **Lead Role**: DFIR Specialist
* **Supporting Roles**: Blue Team / SOC, Threat Intelligence
* **Objectives**: Investigate an active or past compromise, determine entry point, scope lateral movement, and eradicate attacker presence.
* **Key Tasks**:
  1. Triage compromised hosts with KAPE and capture volatile memory.
  2. Parse master file tables ($MFT), shimcache, amcache, and event logs.
  3. Reconstruct the end-to-end intrusion timeline using Hayabusa and Plaso.
  4. Extract IOCs and feed them to Threat Intelligence.
  5. Coordinate eradication, credential reset, and recovery procedures.

---

## 9. CISO Strategic Governance & Board Cyber-Risk Review
* **Lead Role**: Purple Team & Governance Lead
* **Supporting Roles**: Blue Team, AppSec Engineer
* **Objectives**: Produce CISO-level risk reports, regulatory compliance gap analyses, and post-pentest remediation roadmaps.
* **Key Tasks**:
  1. Review posture against NIST 800-53, ISO 27001, and CIS Controls using `cybersecurity-pro`.
  2. Synthesize technical vulnerability findings into quantified business risk.
  3. Generate remediation roadmaps and executive presentations.
