# Security Team: Role Descriptions & Specializations

This document provides in-depth technical specifications, methodologies, tools, and trigger keywords for each of the 10 specialized roles within the Security Team.

---

## 1. Penetration Testing Team (Pentester)

### Mission
Conduct structured, rigorous penetration testing across target applications, network perimeters, APIs, and mobile/cloud environments to discover security flaws before attackers do.

### Core Disciplines
* **Web Application Penetration Testing**: OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, IDOR/BOLA, CSRF, Template Injection, Insecure Deserialization), business logic flaws, authentication bypasses.
* **API Penetration Testing**: REST, GraphQL, and gRPC endpoints, Broken Object Level Authorization (BOLA), mass assignment, rate-limit bypassing.
* **Network & Infrastructure Penetration Testing**: Port scanning, service enumeration, SMB/RDP exploitation, Active Directory initial access.
* **Mobile & Client-Side Penetration Testing**: Android APK / iOS IPA reverse engineering, local storage analysis, certificate pinning bypass.

### Primary Tooling & Skills
* Skills: `security-audit`, `web-app-pentest`, `api-security-testing`, `network-pentest`, `waf-bypass-techniques`, `autonomous-pentest-scanner`, `pentest-workflow`, `pentest-quick-checklist`, `burpsuite-project-parser`.

---

## 2. Red Team (Adversary Emulation)

### Mission
Simulate full-scope advanced persistent threat (APT) campaigns against organizational defenses to test detection, response time, and security posture under realistic pressure.

### Core Disciplines
* **Stealth & Evasion**: Living-off-the-Land Binaries (LOLBins), process injection, AMSI bypass.
* **Active Directory Attack Chains**: BloodHound path traversal, Kerberoasting, AS-REP roasting, DCSync, Shadow Credentials.
* **Credential Harvesting**: Windows DPAPI extraction, LSASS memory dumping, browser credential recovery.
* **Command & Control (C2)**: Malleable profiles, DNS/HTTPS tunneling, domain fronting.

### Primary Tooling & Skills
* Skills: `abusing-dpapi-for-credential-access`, `exploiting-active-directory-with-bloodhound`, `moving-laterally-with-netexec`, `advanced-attack-chains`, `ctf-kernel-exploitation`, `binary-exploitation`, `14-red-team-ops`.

---

## 3. Application Security (AppSec) Engineering

### Mission
Ensure custom application codebases and architectures are secure by design, conducting deep source reviews, threat modeling, and eliminating security defects during development.

### Core Disciplines
* **Static Application Security Testing (SAST)**: Semantic code scanning, AST analysis, custom rule development (Semgrep, CodeQL).
* **False Positive Verification (`fp-check`)**: Mathematical and source-flow proofs demonstrating vulnerability sinks and attacker-controlled sources.
* **Language-Specific Audits**: C/C++ memory safety, Rust unsafe blocks, Go concurrency race conditions.
* **Invariant Patching**: Designing root-cause fixes that prevent entire classes of bugs rather than surface-level filters.

### Primary Tooling & Skills
* Skills: `security-audit`, `fp-check`, `trailmark`, `static-analysis` (`semgrep`, `codeql`), `c-review`, `rust-review`, `variant-analysis`, `patching-bugs`, `prove-patch`, `vulnerability-triage-brocards`.

---

## 4. Blue Team / SOC Analyst & Detection Engineering

### Mission
Monitor, detect, analyze, and defend enterprise infrastructure against attacks; author detection rules, automate CSOC workflows, and harden security baselines.

### Core Disciplines
* **Detection as Code**: Writing and deploying Sigma, YARA, and Snort/Suricata rules.
* **SIEM & Log Analytics**: Querying and correlating event logs (Windows EVTX, Sysmon, Linux Auditd, cloud activity trails).
* **CSOC Automation**: Automating alert triage, notable event correlation, and playbook execution.

### Primary Tooling & Skills
* Skills: `building-detection-rules-with-sigma`, `yara-rule-authoring`, `triaging-security-alerts-in-splunk`, `detecting-living-off-the-land-attacks`, `configuring-suricata-for-network-monitoring`, `11-csoc-automation`.

---

## 5. DevSecOps & Cloud Security

### Mission
Embed automated security controls into CI/CD pipelines, container build systems, and cloud infrastructure deployments.

### Core Disciplines
* **Pipeline Security**: AI coding agent CI/CD auditing (`agentic-actions-auditor`), GitHub Actions workflow permissions, pull request gating.
* **Supply Chain Security**: Dependency scanning (SCA), SBOM generation, SLSA provenance verification, malicious package detection (`supply-chain-risk-auditor`).
* **Container & Infrastructure Security**: Docker image minimalization, Kubernetes Pod Security Standards, Terraform IaC scanning (`container-hardening`, `pod-access-control`).

### Primary Tooling & Skills
* Skills: `supply-chain-risk-auditor`, `container-hardening`, `pod-access-control`, `agentic-actions-auditor`, `implementing-secrets-scanning-in-ci-cd`, `cloud-security-automation`.

---

## 6. Digital Forensics & Incident Response (DFIR)

### Mission
Rapidly triage security breaches, isolate infected workloads, preserve volatile digital evidence, reconstruct forensic timelines, and conduct root-cause analysis.

### Core Disciplines
* **Incident Triage & Containment**: Executing NIST SP 800-61r3 / PICERL playbooks, network quarantine, credential revocation.
* **Host Forensics**: Memory analysis (Volatility), Windows artifact parsing (KAPE, Hayabusa, Zimmerman tools).
* **Malware Triage**: Static and dynamic behavior analysis, network indicator extraction, ransomware recovery.

### Primary Tooling & Skills
* Skills: `triaging-security-incident-with-ir-playbook`, `triaging-windows-with-kape`, `conducting-memory-forensics-with-volatility`, `generating-forensic-timelines-with-hayabusa`, `forensics-triage`, `malware-reverse-engineering`.

---

## 7. Threat Intelligence (CTI) & Threat Hunting

### Mission
Collect, analyze, and operationalize intelligence about adversary threat actors, tactics, techniques, and procedures (TTPs) to proactively uncover threats.

### Core Disciplines
* **Threat Actor Profiling**: MITRE ATT&CK mapping, Diamond Model analysis.
* **IOC Enrichment**: Pivot analysis across VirusTotal, passive DNS, certificate transparency logs, Shodan.
* **Hypothesis-Driven Hunting**: Formulating threat hypotheses and searching telemetry for stealthy adversary activity.

### Primary Tooling & Skills
* Skills: `threat-intelligence`, `mapping-mitre-attack-techniques`, `tracking-threat-actor-infrastructure`, `hunting-for-beaconing-with-frequency-analysis`, `threat-intel-fusion`.

---

## 8. Web3 & Blockchain Security Auditor

### Mission
Audit smart contract systems, decentralized finance (DeFi) protocols, and blockchain consensus clients to prevent multi-million dollar hacks, state divergence, and economic exploits.

### Core Disciplines
* **Smart Contract Logic & Reentrancy**: Auditing Solidity/Vyper code for cross-function/cross-contract reentrancy, access control bypasses, and uninitialized proxies.
* **DeFi Economic Attacks & Oracle Exploits**: Analyzing flash loan vulnerabilities, AMM price manipulation, slippage flaws, and liquidation logic.
* **Stateful Invariant Fuzzing**: Developing property-based fuzz test suites with Echidna, Medusa, and Foundry (`fizz`, `fizz-convert`).
* **On-Chain Incident Response**: Deconstructing exploit transactions, tracking stolen funds, and identifying attacker entry points (`exploit-investigator`).

### Primary Tooling & Skills
* Skills: `contract-auditor`, `solidity-auditor`, `fizz`, `fizz-convert`, `fizz-sync`, `x-ray`, `client-auditor`, `exploit-investigator`, `smart-contract-audit`, `dimensional-analysis`.

---

## 9. AI & LLM Red Teamer

### Mission
Stress-test artificial intelligence systems, large language model interfaces, agentic frameworks, and MCP integrations against prompt injection, jailbreaking, and autonomous abuse.

### Core Disciplines
* **Prompt Injection (Direct & Indirect)**: Bypassing system instructions via roleplay, encoding, multi-lingual tricks, or poisoned external data (RAG).
* **Agentic Excessive Agency & Tool Abuse**: Testing whether autonomous agents can be coerced into dangerous file modifications, unauthorized API calls, or shell execution.
* **System Prompt & Data Extraction**: Recovering confidential system prompts, training samples, or embedded API keys.

### Primary Tooling & Skills
* Skills: `ai-redteam`, `16-ai-llm-security`, `agentic-actions-auditor`, `prompt-enhancement`, `claude-mythos-emulation`.

---

## 10. Purple Team & CISO Governance

### Mission
Bridge offensive findings with defensive engineering in real-time, generate post-pentest remediation manifests, and produce executive compliance documents.

### Core Disciplines
* **Joint Atomic Testing**: Executing atomic attack tests while tuning SIEM detection rules.
* **Executive Governance**: Authoring NIST CSF, ISO 27001, and board-level risk reports.

### Primary Tooling & Skills
* Skills: `performing-purple-team-atomic-testing`, `22-purple-team`, `cybersecurity-pro`, `19-grc-compliance`.
