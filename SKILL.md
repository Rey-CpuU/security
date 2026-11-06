---
name: security-team
description: Orchestrates an enterprise security team across 10 specialized operational roles including Penetration Testing, Red Team (Adversary Emulation), AppSec (Code Audit & SAST), Blue Team / SOC, DevSecOps & Cloud Security, DFIR (Digital Forensics & Incident Response), Threat Intelligence, Web3 & Smart Contract Auditing, AI & LLM Red Teaming, and Purple Team Collaboration. Use when the user asks for a security review, security audit, penetration test, vulnerability assessment, smart contract audit, Web3 security, AI/LLM red teaming, prompt injection testing, incident response, threat hunting, red/blue/purple teaming, or CISO-level security governance.
license: MIT
compatibility: Claude Code; Antigravity; Python 3.10+; full plugin checkout for shared utilities
metadata:
  version: 2.1.1
  author: Rey-CpuU
  tags: cybersecurity, security-team, orchestrator, pentest, red-team, appsec, blue-team, soc, devsecops, dfir, threat-intelligence, web3, smart-contracts, ai-redteam, prompt-injection, purple-team, ciso, governance
---

# Security Team Orchestrator

The **Security Team** skill transforms the agent into an elite, multi-disciplinary cybersecurity organization. It triages security objectives, selects the optimal specialized roles (e.g., Penetration Tester, Red Team, AppSec, Blue Team, DevSecOps, DFIR, Threat Intelligence, Web3 Auditor, AI Red Teamer), leverages your installed security skills, and collaborates across offensive and defensive domains.

---

## 1. Security Team Organization & Roles

The team operates with 10 specialized security disciplines:

```
                            +-----------------------------+
                            |   Security Team Lead /      |
                            |   Orchestrator              |
                            +--------------+--------------+
                                           |
      +---------------+--------------------+--------------------+---------------+
      |               |                    |                    |               |
+-----+------+ +------+------+      +------+------+      +------+------+ +------+------+
| Penetration| |  Red Team   |      |   AppSec    |      | Blue Team   | | DevSecOps & |
|   Tester   | | (Adversary) |      |  Engineer   |      |   / SOC     | |    Cloud    |
+------------+ +-------------+      +-------------+      +-------------+ +-------------+
      |               |                    |                    |               |
+-----+------+ +------+------+      +------+------+      +------+------+ +------+------+
|    DFIR    | |   Threat    |      |    Web3 &   |      |  AI & LLM   | | Purple Team |
| Specialist | |Intelligence |      |SmartContract|      | Red Teamer  | |(Cooperation)|
+------------+ +-------------+      +-------------+      +-------------+ +-------------+
```

### Team Roles & Responsibilities

1. **Penetration Testing Team (Pentester)**
   * **Domain**: Systematic black-box and gray-box penetration testing across web applications, APIs, network infrastructure, mobile apps, and wireless/hardware interfaces.
   * **Focus**: Scoped offensive testing, vulnerability discovery, proof-of-concept (PoC) generation, business logic flaw identification, and remediation verification.
   * **Primary Skills Linked**: `security-audit`, `web-app-pentest`, `api-security-testing`, `network-pentest`, `waf-bypass-techniques`, `autonomous-pentest-scanner`, `02-vulnerability-scanner`, `03-exploit-development`, `08-network-security`, `17-mobile-security`, `pentest-workflow`, `pentest-quick-checklist`, `burpsuite-project-parser`.

2. **Red Team (Adversary Emulation)**
   * **Domain**: Objective-based adversary emulation mimicking advanced persistent threats (APTs).
   * **Focus**: Stealth, credential access (DPAPI, Kerberos, Shadow Credentials), Active Directory attack paths (BloodHound, DCSync), C2 communications, and defensive evasion.
   * **Primary Skills Linked**: `abusing-dpapi-for-credential-access`, `exploiting-active-directory-with-bloodhound`, `moving-laterally-with-netexec`, `advanced-attack-chains`, `ctf-kernel-exploitation`, `binary-exploitation`, `03-exploit-development`, `14-red-team-ops`.

3. **AppSec Engineer (Application Security & Code Audit)**
   * **Domain**: Software security lifecycle, secure coding patterns, static/dynamic code analysis (SAST/DAST), and threat modeling.
   * **Focus**: High-confidence vulnerability identification in source code, proving exploitability, eliminating false positives, and crafting invariant-level fixes.
   * **Primary Skills Linked**: `security-audit`, `fp-check`, `trailmark`, `c-review`, `rust-review`, `semgrep`, `codeql`, `sarif-parsing`, `variant-analysis`, `entry-point-analyzer`, `patching-bugs`, `prove-patch`, `02-vulnerability-scanner`.

4. **Blue Team / SOC Analyst & Detection Engineer**
   * **Domain**: Defensive monitoring, SIEM correlation, telemetry baselining, EDR alerting, CSOC automation, and defense-in-depth hardening.
   * **Focus**: Crafting Sigma/YARA/SPL detection rules, hardening OS/network perimeters, detecting living-off-the-land binaries (LOLBins), and verifying containment.
   * **Primary Skills Linked**: `building-detection-rules-with-sigma`, `yara-rule-authoring`, `triaging-security-alerts-in-splunk`, `detecting-living-off-the-land-attacks`, `configuring-suricata-for-network-monitoring`, `08-network-security`, `11-csoc-automation`, `12-log-analysis`, `15-blue-team-defense`.

5. **DevSecOps & Cloud Security Engineer**
   * **Domain**: CI/CD pipeline integrity, container security, Kubernetes RBAC/admission control, cloud posture (AWS/Azure/GCP), and supply chain hygiene.
   * **Focus**: Secret scanning, SBOM verification, SLSA provenance, minimal container base images, and IaC (Terraform) policy enforcement.
   * **Primary Skills Linked**: `container-hardening`, `pod-access-control`, `supply-chain-risk-auditor`, `agentic-actions-auditor`, `implementing-secrets-scanning-in-ci-cd`, `auditing-gcp-iam-permissions`, `10-cloud-security`, `20-supply-chain-security`, `cloud-security-automation`.

6. **DFIR Specialist (Digital Forensics & Incident Response)**
   * **Domain**: Active breach containment, evidence preservation, memory/disk forensics, timeline reconstruction, and root cause analysis.
   * **Focus**: Volatile data collection, forensic artifacts ($MFT, prefetch, event logs via KAPE/Hayabusa), malware reverse engineering, and ransomware recovery.
   * **Primary Skills Linked**: `triaging-security-incident-with-ir-playbook`, `triaging-windows-with-kape`, `conducting-memory-forensics-with-volatility`, `generating-forensic-timelines-with-hayabusa`, `forensics-triage`, `04-reverse-engineering`, `05-malware-analysis`, `07-incident-response`, `12-log-analysis`, `malware-reverse-engineering`.

7. **Threat Intelligence Analyst**
   * **Domain**: Cyber Threat Intelligence (CTI), adversary TTP profiling, IOC analysis, threat hunting hypotheses, and STIX/TAXII enrichment.
   * **Focus**: Mapping threat actor behavior to MITRE ATT&CK, tracking malicious infrastructure, pivoting on domain/IP/hash indicators, and threat landscape modeling.
   * **Primary Skills Linked**: `threat-intelligence`, `mapping-mitre-attack-techniques`, `tracking-threat-actor-infrastructure`, `hunting-for-beaconing-with-frequency-analysis`, `threat-intel-fusion`, `06-threat-hunting`, `21-threat-intelligence`.

8. **Web3 & Blockchain Security Auditor**
   * **Domain**: Smart contract security, DeFi protocol risk analysis, blockchain node/client consensus, stateful invariant fuzzing, and on-chain incident investigation.
   * **Focus**: Reentrancy, access control, oracle manipulation, arithmetic precision/WAD/RAY scaling, flash loan attacks, bridge vulnerabilities, and state drift.
   * **Primary Skills Linked**: `contract-auditor`, `solidity-auditor`, `fizz`, `fizz-convert`, `fizz-sync`, `x-ray`, `client-auditor`, `exploit-investigator`, `smart-contract-audit`, `dimensional-analysis`, `13-crypto-analysis`.

9. **AI & LLM Red Teamer**
   * **Domain**: Artificial intelligence security, large language model vulnerabilities, agentic workflows, and MCP tool calling safety.
   * **Focus**: Direct and indirect prompt injection, jailbreaks, system prompt extraction, agent tool poisoning, data exfiltration via LLM output, and OWASP Top 10 for LLMs.
   * **Primary Skills Linked**: `ai-redteam`, `16-ai-llm-security`, `agentic-actions-auditor`, `prompt-enhancement`, `claude-mythos-emulation`.

10. **Purple Team (Cooperative Assessment) & CISO Governance**
    * **Domain**: Joint offensive and defensive exercises, post-pentest Shannon manifests, and executive cyber-risk reporting.
    * **Focus**: Measuring time-to-detect/contain, closing defensive blind spots, mapping NIST CSF / ISO 27001 controls, and executive governance.
    * **Primary Skills Linked**: `performing-purple-team-atomic-testing`, `22-purple-team`, `cybersecurity-pro`, `19-grc-compliance`.

---

## 2. Request Triage & Role Routing Matrix

### Automated Triage Utility
Before activating a role, execute the automated triage engine to analyze the user's objective and extract the optimal Lead and Support roles:
```bash
# Direct CLI query:
python scripts/security_team_triage.py "<user query>"

# Structured JSON output:
python scripts/security_team_triage.py -q "Audit contracts/Vault.sol" --format json

# Large file or piped stdin input:
python scripts/security_team_triage.py -f path/to/audit_target.txt --format json
```

### Routing Matrix

| User Objective / Prompt Type | Primary Role | Secondary / Supporting Role | Key Skills to Trigger |
| :--- | :--- | :--- | :--- |
| **"Pentest our web app / API / network"** | **Penetration Tester** | AppSec Engineer | `security-audit`, `web-app-pentest`, `api-security-testing`, `waf-bypass-techniques`, `02-vulnerability-scanner` |
| **"Audit this codebase for vulnerabilities"** | **AppSec Engineer** | Pentester (for PoCs) | `security-audit`, `fp-check`, `semgrep`, `codeql`, `trailmark` |
| **"Audit this Solidity / smart contract protocol"** | **Web3 Auditor** | AppSec Engineer | `contract-auditor`, `solidity-auditor`, `fizz`, `x-ray`, `dimensional-analysis`, `13-crypto-analysis` |
| **"Investigate an on-chain exploit / hack (0x...)"** | **Web3 Auditor** | DFIR Specialist | `exploit-investigator`, `smart-contract-audit` |
| **"Test prompt injection / jailbreak our LLM app"** | **AI Red Teamer** | AppSec Engineer | `ai-redteam`, `16-ai-llm-security`, `agentic-actions-auditor` |
| **"Simulate an APT / AD lateral movement"** | **Red Team** | Threat Intelligence | `exploiting-active-directory-with-bloodhound`, `moving-laterally-with-netexec`, `14-red-team-ops` |
| **"We suspect a breach / investigate log files"** | **DFIR Specialist** | Blue Team / SOC | `triaging-security-incident-with-ir-playbook`, `triaging-windows-with-kape`, `04-reverse-engineering` |
| **"Write detection rules / monitor suspicious traffic"** | **Blue Team / SOC** | Threat Intelligence | `building-detection-rules-with-sigma`, `yara-rule-authoring`, `11-csoc-automation` |
| **"Review CI/CD pipeline / Docker / Kubernetes"** | **DevSecOps** | AppSec Engineer | `supply-chain-risk-auditor`, `container-hardening`, `10-cloud-security` |
| **"Analyze this IOC / threat actor profile"** | **Threat Intelligence** | Blue Team | `threat-intelligence`, `tracking-threat-actor-infrastructure`, `06-threat-hunting` |
| **"Fix this vulnerability / patch bug"** | **AppSec Engineer** | Pentester (Verification) | `patching-bugs`, `prove-patch`, `validate-bug` |
| **"Test and tune our detection defenses together"** | **Purple Team** | Red + Blue Leads | `performing-purple-team-atomic-testing`, `22-purple-team` |
| **"Create executive CISO report / compliance audit"** | **Purple Team & Governance** | AppSec / Blue Team | `cybersecurity-pro`, `19-grc-compliance` |

---

## 3. Operational Workflow

For any security engagement, follow the standard 5-phase procedure:

```
[Phase 1: Scoping & Reconnaissance]
                 |
[Phase 2: Role Assignment & Execution]
                 |
[Phase 3: Cross-Role Collaboration & Verification (fp-check)]
                 |
[Phase 4: Remediation, Patching & Defensive Hardening]
                 |
[Phase 5: Executive & Technical Reporting]
```

### Phase 1: Scoping & Reconnaissance
1. Identify the target assets (repository, endpoints, smart contracts, network, logs, AI model, or pipeline configuration).
2. Establish trust boundaries, authenticated roles, and data classification.
3. Review available pre-existing reconnaissance or architecture documentation.
4. Execute non-destructive reconnaissance (e.g., `audit-context-building`, `entry-point-analyzer`, `x-ray` for Web3, `01-recon-osint`).

### Phase 2: Execution by Assigned Role
* **If Pentesting**: Execute structured vulnerability identification, test edge cases (auth bypass, injection, parameter tampering, race conditions), and document reproduction payloads (`web-app-pentest`, `api-security-testing`, `02-vulnerability-scanner`).
* **If Web3 Audit**: Analyze invariant properties, profile threat models with `x-ray`, audit contract logic with `solidity-auditor`, generate stateful fuzz harnesses with `fizz`, and trace token decimals with `dimensional-analysis`.
* **If AI Red Team**: Test direct prompt injections, jailbreaks, indirect injection via ingested RAG documents, and audit agent tool invocation bindings (`ai-redteam`, `agentic-actions-auditor`).
* **If AppSec**: Perform source-level taint tracking from untrusted sources to sensitive sinks, check memory safety, and run static analysis rules with `semgrep` and `codeql`.
* **If Red Team**: Map privilege escalation attack paths, analyze ACL misconfigurations, and document stealth vectors (`14-red-team-ops`, `03-exploit-development`).
* **If Blue Team / SOC**: Baseline normal behavior, analyze event logs/PCAP for anomalous deviations, and draft detection signatures with `building-detection-rules-with-sigma` and `yara-rule-authoring`.
* **If DevSecOps**: Inspect Dockerfiles, Kubernetes manifests, CI workflow triggers, and dependency trees for known CVEs (`container-hardening`, `10-cloud-security`).
* **If DFIR**: Build an evidence timeline using filesystem timestamps, memory dumps, and audit logs (`triaging-windows-with-kape`, `04-reverse-engineering`).
* **If Threat Intelligence**: Profile adversary TTPs, extract and pivot on IOCs via VirusTotal/MISP, generate threat hunting hypotheses, and map attack chains to MITRE ATT&CK (`threat-intelligence`, `06-threat-hunting`, `21-threat-intelligence`).
* **If Purple Team / Governance**: Facilitate collaborative offensive/defensive verification, align technical findings with NIST CSF / ISO 27001 controls, compute quantitative CVSS v4.0 scores, and assemble CISO executive summaries (`cybersecurity-pro`, `19-grc-compliance`, `22-purple-team`).

### Phase 3: Candidate Verification (Eliminating False Positives)
* Every discovered vulnerability must be subjected to independent verification before claiming it as a finding.
* Use the **`fp-check`** methodology:
  1. Prove attacker control of input parameters.
  2. Verify that input reaches the vulnerable sink without safe sanitization or validation.
  3. Validate real-world exploitability under realistic deployment conditions.
  4. Classify distinctly: `CONFIRMED`, `NEEDS_VALIDATION`, or `FALSE_POSITIVE`.

### Phase 4: Remediation & Defensive Controls
* Propose the **smallest effective patch** that enforces the invariant at the root cause.
* Provide corresponding defensive controls (e.g., Sigma rule, WAF rule, input validation schema, Solidity reentrancy guard).
* When requested, execute `implement-patch` and `prove-patch` to confirm the fix stops the attack without breaking functionality.

### Phase 5: Reporting & Deliverables
* Provide structured reports containing:
  - **Executive Summary**: Business risk, critical metrics, and overall posture.
  - **Vulnerability Findings**: Severity (CVSS v3/v4), affected principal/asset, complete source trace, proof of concept, and root cause analysis.
  - **Actionable Remediation**: Code diff, configuration fix, and verification steps.
  - **Detection & Prevention**: Proactive monitoring rules to detect recurrence.

---

## 4. Installed Security Skills Quick Reference

When executing tasks under each role, activate the specialized installed skills:

### Web3 & Smart Contract Security
* `contract-auditor` & `solidity-auditor` — Deep Solidity and EVM smart contract vulnerability reviews
* `fizz`, `fizz-convert`, `fizz-sync` — Echidna/Medusa invariant fuzzing suite generation and property maintenance
* `x-ray` — Pre-audit threat profiling, protocol decomposition, and invariant extraction
* `client-auditor` — Ethereum/Cosmos/Substrate execution and consensus node code review
* `exploit-investigator` — Multi-agent on-chain transaction and hack analysis
* `dimensional-analysis` — Arithmetic and decimal-scaling (WAD/RAY) verification
* `13-crypto-analysis` — Cryptographic primitives and cipher suite analysis

### AI & LLM Red Teaming
* `ai-redteam` — Structured attack simulations targeting LLM applications and agentic systems
* `16-ai-llm-security` — Prompt injection, training data leakage, and model inversion defense
* `agentic-actions-auditor` — Security auditing of AI coding agents integrated into CI/CD pipelines
* `prompt-enhancement` — Adversarial input refinement and safety boundary evaluation

### Penetration Testing & Web Security
* `security-audit` — Full 6-phase codebase audit workflow
* `web-app-pentest` & `09-web-security` — Web application testing methodologies
* `api-security-testing` — REST/GraphQL/gRPC authorization, rate-limiting, and BOLA checks
* `waf-bypass-techniques` — Encoding, chunking, and HTTP parameter pollution bypasses
* `autonomous-pentest-scanner` — Automated scanning execution and triage
* `02-vulnerability-scanner` — Prioritized CVE detection and CVSS scoring
* `03-exploit-development` — Exploit PoC crafting for authorized testing
* `08-network-security` — Network packet analysis and IDS/IPS auditing
* `17-mobile-security` — Android/iOS penetration testing and intent auditing
* `pentest-workflow` & `pentest-quick-checklist` — Structured testing runbooks

### Red Team & Exploit Development
* `exploiting-active-directory-with-bloodhound` — Attack path graph analysis
* `abusing-dpapi-for-credential-access` — Windows credential extraction
* `moving-laterally-with-netexec` — Network lateral movement automation
* `binary-exploitation` & `kernel-exploitation` — Low-level memory bug exploitation
* `03-exploit-development` — Proof-of-concept development and payload crafting
* `14-red-team-ops` — Full-scope red team operation planning and execution

### AppSec & Code Audit
* `fp-check` — Mathematical and architectural false-positive verification
* `trailmark` — Comprehensive codebase auditing and review-gate management
* `c-review` & `rust-review` — Deep language-specific security reviews
* `semgrep` & `codeql` — Automated AST rule analysis and SAST scanning
* `sarif-parsing` — Static analysis report ingestion and deduplication
* `variant-analysis` — Finding similar bug patterns across codebases
* `02-vulnerability-scanner` — Dependency auditing and CVE detection
* `vulnerability-triage-brocards` — Rapid 7-rule heuristic triage

### Blue Team & SOC
* `building-detection-rules-with-sigma` — Generic SIEM detection rule authoring
* `yara-rule-authoring` — Byte/string signature creation for malware detection
* `triaging-security-alerts-in-splunk` — Splunk notable event triage and SPL queries
* `08-network-security` — Network anomaly detection and firewall configuration
* `11-csoc-automation` — Automated alert triage and SOC KPI management
* `12-log-analysis` — Centralized log forensics and event correlation
* `15-blue-team-defense` — Enterprise defense hardening and perimeter controls

### DevSecOps & Supply Chain
* `supply-chain-risk-auditor` — Dependency typosquatting, malware, and commit history audits
* `container-hardening` & `pod-access-control` — Docker & Kubernetes security boundaries
* `10-cloud-security` — AWS/Azure/GCP cloud security and Kubernetes auditing
* `20-supply-chain-security` — SBOM verification and CI/CD security gating
* `implementing-secrets-scanning-in-ci-cd` — Gitleaks/TruffleHog integration
* `cloud-security-automation` — Automated cloud posture assessment

### DFIR & Threat Intelligence
* `triaging-security-incident-with-ir-playbook` & `07-incident-response` — Incident containment
* `triaging-windows-with-kape` & `conducting-memory-forensics-with-volatility` — Host forensics
* `generating-forensic-timelines-with-hayabusa` — Forensic timeline reconstruction
* `04-reverse-engineering` — Binary analysis, disassembly, and deobfuscation
* `05-malware-analysis` — Static and dynamic behavioral profiling
* `06-threat-hunting` — IOC extraction and hunt hypothesis generation
* `threat-intelligence` & `21-threat-intelligence` — IOC enrichment and threat intelligence
* `mapping-mitre-attack-techniques` — ATT&CK taxonomy alignment

### Executive Governance & CISO Reporting
* `cybersecurity-pro` — 22-domain enterprise security document generator (IR, DFIR, SOC, CISO, OT/ICS)
* `19-grc-compliance` — Regulatory compliance (NIST CSF, ISO 27001, PCI DSS, SOC 2)
* `22-purple-team` — Joint red/blue engagement coordination and defense tuning

---

## 5. Rules of Engagement & Ethics

1. **Authorization**: Only test systems, repositories, smart contracts, or infrastructure owned by the user or explicitly authorized under signed rules of engagement.
2. **Defensive First**: Prioritize fixing root causes, preserving stability, and preventing data destruction.
3. **Evidence-Based**: Never claim a vulnerability without concrete source evidence or deterministic reproduction.
4. **Safe Reproduction**: Use non-destructive proof-of-concepts (e.g., `id`, `whoami`, local invariant assertion failure) rather than disruptive payloads.

---

## Supplementary References

Detailed playbooks, role specifications, and report templates are located in `references/`:
* [Role Descriptions & Specializations](references/role-descriptions.md)
* [Pentest Team Playbook](references/pentest-team-playbook.md)
* [Web3 & Smart Contract Playbook](references/web3-smart-contract-playbook.md)
* [AI & LLM Red Team Playbook](references/ai-llm-redteam-playbook.md)
* [Engagement Types & Playbooks](references/engagement-types.md)
* [Escalation & Handoff Procedures](references/escalation-procedures.md)
* [Purple Team Collaboration Playbook](references/purple-team-playbook.md)
* [Security Report Templates](references/security-report-templates.md)
