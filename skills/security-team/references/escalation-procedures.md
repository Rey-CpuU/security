# Security Team: Escalation & Handoff Procedures

This document outlines severity criteria, cross-role communication handoffs, and emergency protocols when critical security risks are uncovered.

---

## 1. Vulnerability Severity Matrix

| Severity Level | CVSS Score Range | Definition & Impact Criteria | Escalation SLA |
| :--- | :--- | :--- | :--- |
| **Critical** | 9.0 - 10.0 | Unauthenticated Remote Code Execution (RCE), complete database compromise, authentication bypass to root/admin, active wormable exploit. | **Immediate** (Halt testing, notify stakeholders within 1 hour) |
| **High** | 7.0 - 8.9 | Stored XSS impacting administrators, blind SQLi, horizontal/vertical IDOR accessing sensitive PII, SSRF to cloud metadata. | **Same Day** (Document within 4 hours) |
| **Medium** | 4.0 - 6.9 | Reflected XSS requiring user interaction, CSRF on non-critical actions, information disclosure of server versions, weak TLS ciphers. | **Standard** (Include in milestone debrief) |
| **Low / Info** | 0.0 - 3.9 | Missing security headers (CSP, HSTS), verbose error messages, software version disclosure without known exploit. | **Periodic** (Include in final report) |

---

## 2. Cross-Role Handoff Workflows

### Scenario A: Pentester Uncovers a 0-Day / Critical Flaw
```
[Pentester discovers RCE]
           |
           v
[AppSec Engineer verifies root cause & drafts fix]
           |
           +-----------------------------+
           |                             |
           v                             v
[DevSecOps deploys emergency fix]  [Blue Team deploys temporary WAF / Sigma rule]
```
1. **Pentester** isolates the finding, produces minimal reproducible curl payload, and freezes intrusive testing on the affected component.
2. **AppSec Engineer** inspects the underlying source code using `fp-check` and drafts an invariant-enforcing patch using `patching-bugs`.
3. **Blue Team** authors an emergency WAF signature or Sigma detection rule to monitor for exploitation attempts while the patch is being deployed.
4. **DevSecOps** coordinates automated pipeline building and rollout of the patched build.

---

### Scenario B: DFIR Incident Escalation
```
[DFIR uncovers active C2 traffic]
           |
           v
[Threat Intel extracts IOCs & profiles threat actor]
           |
           v
[Blue Team applies block rules across firewall/EDR]
           |
           v
[Pentester & Red Team conduct gap analysis post-containment]
```
1. **DFIR** recovers malicious binaries, IP addresses, and domain names from infected memory/disk dumps.
2. **Threat Intelligence** searches VirusTotal, MISP, and threat feeds to identify the threat actor family and known secondary infrastructure.
3. **Blue Team** pushes IOC blocks to DNS firewalls, EDR blocklists, and perimeter proxies.
4. **Red Team** assists by verifying that alternative entry vectors used by the same threat actor are closed.
