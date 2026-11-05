# Purple Team Collaboration Playbook

Purple Teaming bridges offensive capabilities (Pentesting & Red Team) with defensive engineering (Blue Team, AppSec, DevSecOps) in an iterative, transparent feedback loop.

---

## 1. The Purple Team Feedback Loop

```
[1. Red/Pentest executes atomic technique]
                    |
                    v
[2. Blue Team verifies detection in SIEM/EDR]
                    |
                    +------------------------+
                    |                        |
         [Detected / Logged]        [Blind Spot / Missed]
                    |                        |
                    v                        v
         [Measure Time to Detect]   [Tune Telemetry & Rules]
                    |                        |
                    +----------+-------------+
                               |
                               v
[3. Re-execute test & validate improved defense]
```

---

## 2. Common Purple Team Exercise Scenarios

### Exercise 1: Credential Access (DPAPI / Kerberoasting)
* **Offensive Action**: Pentester runs non-domain joined Kerberoasting or offline DPAPI blob extraction.
* **Defensive Verification**:
  * Check Windows Event ID 4769 (A Kerberos service ticket was requested with encryption type 0x17 RC4).
  * Check Sysmon Event 10 (Process access to LSASS by unauthorized binaries).
* **Defensive Tuning**: Author Sigma rule `win_kerberoasting_unusual_encryption.yml` and enable alert forwarding to Slack/PagerDuty.

### Exercise 2: Living-off-the-Land (LOLBins) Execution
* **Offensive Action**: Execute commands via `certutil.exe -urlcache`, `mshta.exe`, or `rundll32.exe`.
* **Defensive Verification**:
  * Check Sysmon Event 1 (Process creation) for anomalous command-line flags.
  * Check EDR command-line logging.
* **Defensive Tuning**: Deploy AppLocker / WDAC policies restricting script interpreters and add Sigma rules for LOLBins.

### Exercise 3: Web Application WAF Bypass
* **Offensive Action**: Pentester sends SQLi or SSRF payloads using URL double encoding, chunked transfer encoding, or unicode normalization.
* **Defensive Verification**:
  * Check WAF inspection logs to see if requests passed transparently.
  * Check backend database logs for raw unescaped queries.
* **Defensive Tuning**: Update WAF regex decoding rules and ensure backend uses parameterized queries.
