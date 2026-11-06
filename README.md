<div align="center">

<pre align="center">
    ____  _____ ____ _   _ ____  ___ _______   __ _____ _____    _    __  __    
   / ___|| ____/ ___| | | |  _ \|_ _|_   _\ \ / /|_   _| ____|  / \  |  \/  |   
   \___ \|  _|| |   | | | | |_) || |  | |  \ V /   | | |  _|   / _ \ | |\/| |   
    ___) | |__| |___| |_| |  _ < | |  | |   | |    | | | |___ / ___ \| |  | |   
   |____/|_____\____|\___/|_| \_\___| |_|   |_|    |_| |_____/_/   \_\_|  |_|   
================================================================================
            AUTONOMOUS CYBER SECURITY SQUAD FOR AI CODING ASSISTANTS            
================================================================================
</pre>

# 🛡️ security-team

### Satu skill orkestrator untuk memimpin 10 divisi cyber security spesialis<br>dan 1.200+ modul keamanan enterprise langsung di AI coding assistant Anda.

<p align="center">
  <a href="https://github.com/Rey-CpuU/security/releases"><img src="https://img.shields.io/badge/Release-v2.2.0-blue.svg" alt="Release: v2.2.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/Rey-CpuU/security"><img src="https://img.shields.io/badge/Platform-Antigravity%20%7C%20Claude%20Code%20%7C%20Codex-brightgreen" alt="Platform"></a>
  <a href="https://github.com/Rey-CpuU/security"><img src="https://img.shields.io/badge/Specialized%20Roles-10%20Divisions-blueviolet" alt="Specialized Roles"></a>
  <a href="https://github.com/Rey-CpuU/security"><img src="https://img.shields.io/badge/Sub--Skills-1%2C214%2B%20Modules-orange" alt="Sub-Skills Ecosystem"></a>
  <a href="https://github.com/Rey-CpuU/security"><img src="https://img.shields.io/badge/Verification-Zero%20False--Positive-success" alt="Verification"></a>
</p>

</div>

---

## 🎬 Demo / Preview Interaktif

Berikut adalah simulasi alur eksekusi saat developer meminta bantuan perbaikan celah keamanan:

```text
┌──[ Antigravity / Claude Code Terminal Session ]────────────────────────────┐
│                                                                            │
│ > /security-team Audit API user dan perbaiki celah IDOR di src/routes/user │
│                                                                            │
│ 🔍 [PHASE 1: SMART TRIAGE & RECONNAISSANCE]                                 │
│    ├─ Stack Detected   : Python 3.11 • FastAPI • SQLAlchemy • JWT Bearer   │
│    ├─ Target Scope     : src/routes/user.py (GET /api/v1/user/{id})        │
│    ├─ Lead Role        : [Role 03] AppSec Engineer & Invariant Patching    │
│    ├─ Support Role     : [Role 01] Web & API Penetration Tester            │
│    └─ Sub-Skills Loaded: fp-check, implement-patch, testing-for-idor       │
│                                                                            │
│ 💥 [PHASE 2: VULNERABILITY DISCOVERY & PoC PROOF]                           │
│    ├─ Finding Name     : CWE-639: Insecure Direct Object Reference (IDOR)  │
│    ├─ Severity Score   : CVSS v4.0: 8.5 (HIGH) [CVSS:4.0/AV:N/AC:L/PR:L]   │
│    ├─ Replay Exploit   : curl -s -X GET http://localhost:8000/api/user/1   │
│    │                     -H "Authorization: Bearer <attacker_jwt_token>"   │
│    └─ Exploit Output   : 200 OK {"id":1,"role":"admin","secret":"sk_live"} │
│                          (Terbukti data admin bocor ke user biasa!)        │
│                                                                            │
│ 🛡️ [PHASE 3: ZERO FALSE-POSITIVE VERIFICATION (fp-check)]                  │
│    ├─ Step 1 (Dataflow): Source 'user_id' mengalir ke SQL sink tanpa filter│
│    ├─ Step 2 (Bounds)  : Attacker non-privileged mampu melewati boundary   │
│    ├─ Step 3 (Harness) : Automated exploit execution berhasil 10/10 run    │
│    └─ Verifikasi Akhir : [VERIFIED EXPLOITABLE] (False-Positive: 0%)       │
│                                                                            │
│ 📦 [PHASE 4: INVARIANT SECURITY PATCH (READY-TO-MERGE)]                     │
│    --- a/src/routes/user.py                                                │
│    +++ b/src/routes/user.py                                                │
│    @@ -42,3 +42,6 @@ def get_user_profile(user_id: int, current_user):     │
│    -    return db.query(User).filter(User.id == user_id).first()           │
│    +    if current_user.id != user_id and not current_user.is_admin:       │
│    +        raise HTTPException(status_code=403, detail="Access Denied")   │
│    +    return db.query(User).filter(User.id == user_id).first()           │
│                                                                            │
│ 📋 [PHASE 5: DELIVERABLES GENERATED]                                        │
│    [✓] Invariant Git Patch         : patches/fix-cwe-639-idor.patch        │
│    [✓] Regression Test Suite       : tests/test_idor.py (100% PASSED)      │
│    [✓] CISO Executive Briefing     : reports/CISO-IDOR-Risk-Report.md      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```
> *Tampilan eksekusi real-time saat `security-team` menerima prompt, membedah konteks, memvalidasi bukti eksploitasi, dan langsung menulis kode perbaikan siap-merge.*

---

## 💡 Kenapa Skill Ini?

| Masalah Konvensional | Solusi `security-team` |
| :--- | :--- |
| **Fragmentasi Ratusan Tool:** Developer punya ratusan skill keamanan tapi bingung memilih modul mana yang harus dipanggil. | **Smart Triage Orchestration:** Script cerdas membedah konteks tugas dan memilih lead role serta modul otomatis. |
| **Banjir Temuan Palsu (False Positives):** AI biasa sering berhalusinasi celah fiktif yang membuang waktu developer. | **Zero False-Positive (`fp-check`):** Wajib lolos verifikasi bukti matematis dan PoC fungsional sebelum dilaporkan. |
| **Laporan Terlalu Teoritis:** Output scanner standar hanya saran umum tanpa kode perbaikan yang nyata. | **Dual Deliverables:** Menghasilkan patch kode git diff siap merge sekaligus ringkasan eksekutif untuk manajemen. |

---

## ⚡ Fitur Utama

| No | Fitur / Divisi Keamanan | Deskripsi Singkat | Modul Inti |
| :---: | :--- | :--- | :--- |
| **01** | **Web & API Penetration Testing** | Audit kerentanan OWASP Top 10, REST/GraphQL, validasi token, dan bypass WAF. | `web-app-pentest`, `api-security-testing`, `02-vulnerability-scanner` |
| **02** | **Red Team & Adversary Simulation** | Simulasi serangan Active Directory, Kerberoasting, privilege escalation, dan C2. | `14-red-team-ops`, `exploiting-active-directory-with-bloodhound` |
| **03** | **AppSec & Invariant Patching** | Analisis SAST sumber kode (Semgrep/CodeQL) dan penambalan bug invariant fix. | `fp-check`, `semgrep`, `codeql`, `implement-patch` |
| **04** | **Blue Team & SOC Engineering** | Pembuatan aturan deteksi SIEM (Sigma), YARA, dan otomatisasi triage alert CSOC. | `11-csoc-automation`, `building-detection-rules-with-sigma`, `yara` |
| **05** | **DevSecOps & Cloud Hardening** | Audit postur CI/CD, scanning container Docker/K8s, dan verifikasi SBOM/SLSA. | `10-cloud-security`, `container-hardening`, `supply-chain-risk-auditor` |
| **06** | **DFIR & Malware Analysis** | Investigasi forensik disk, memory dump (KAPE/Volatility), dan reverse malware. | `04-reverse-engineering`, `05-malware-analysis`, `forensics-triage` |
| **07** | **Threat Intel & Threat Hunting** | Pemetaan taktik ancaman MITRE ATT&CK, korelasi MISP, dan ekstraksi indikator IOC. | `06-threat-hunting`, `threat-intelligence`, `threat-intel-fusion` |
| **08** | **Web3 & Smart Contract Audit** | Audit kontrak Solidity, invariant fuzzing (Foundry/Fizz), dan DeFi exploit triage. | `contract-auditor`, `solidity-auditor`, `fizz`, `dimensional-analysis` |
| **09** | **AI & LLM Red Teaming** | Uji ketahanan model terhadap prompt injection, jailbreak, dan agent tool poisoning.| `ai-redteam`, `16-ai-llm-security`, `agentic-actions-auditor` |
| **10** | **Purple Team & Governance (CISO)** | Evaluasi risiko komprehensif, kepatuhan NIST CSF / ISO 27001, dan CISO board deck. | `cybersecurity-pro`, `19-grc-compliance`, `22-purple-team` |

---

## 🚀 Quick Start

Mulai gunakan `security-team` dalam 3 langkah mudah:

```bash
# 1. Clone repositori ke workspace lokal Anda
git clone https://github.com/Rey-CpuU/security.git

# 2. Salin folder skill ke direktori agent Antigravity / Claude Code:
# Linux / macOS / Bash:
cp -r security/ ~/.gemini/config/skills/security-team/
# Windows PowerShell:
Copy-Item -Recurse security/ ~/.gemini/config/skills/security-team/

# 3. Jalankan audit pertama Anda di chat coding assistant
/security-team Audit keamanan repository ini dan cari potensi kebocoran rahasia

# 4. (Opsional) Jalankan GUI Kantor Virtual 8-Bit Interaktif:
pip install -r gui/requirements.txt
python gui/run.py
```

---

## 🔄 Cara Kerja (Step by Step)

Alur otomatis dari prompt pengguna hingga penyerahan laporan bebas false-positive:

1. **Input Parsing & Intent Extraction**  
   Prompt pengguna dibaca oleh Lead Security Architect. Karakteristik target (web URL, codebase, Solidity, memory dump, atau log) diidentifikasi.
2. **Context-Aware Triage (`security_team_triage.py`)**  
   Script triage menghitung skor bobot kata kunci secara otomatis untuk menentukan 1 Lead Role dan maksimal 2 Support Roles pendamping.
3. **Pustaka Sub-Skill Terpanggil**  
   Orchestrator mengaktifkan modul spesifik dari 1.214+ keahlian terpasang (Trail of Bits, Anthropic Cyber, Pashov, Red Hat, dsb.).
4. **Eksekusi & Pengumpulan Bukti**  
   Tim spesialis memetakan alur *source-to-sink*, menguji boundary kondisi logika, atau menjalankan harness pengujian.
5. **Verifikasi Ketat Zero False-Positive (`fp-check`)**  
   Setiap temuan harus memiliki PoC yang dapat direproduksi dan bukti invariant matematis. Temuan yang tidak terbukti langsung dianulir.
6. **Penyusunan Deliverables Terstandarisasi**  
   Menghasilkan laporan teknis dengan skor CVSS v4.0, patch kode siap-merge (`git diff`), dan ringkasan eksekutif CISO.

---

## 📐 Topologi Arsitektur (Detail Box ASCII Architecture)

Topologi di bawah menunjukkan bagaimana data dan instruksi mengalir dari input awal pengguna hingga menghasilkan artefak keamanan terverifikasi:

<div align="center">

<pre align="center">
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: USER INTERACTION & ORCHESTRATION INTERFACE                        │
│ • CLI / Chat Prompt (/security-team)  • 8-Bit Pixel Virtual Office GUI     │
│ • Task Card Dispatcher Desk           • Retro CRT Live Terminal HUD        │
│ In: User Target & Security Intent     │ Out: Dispatched Task Card / Prompt │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: INPUT & CONTEXT INGESTION (SCOPED TARGETS)                        │
│ • Web/API URL   • Git Codebase   • Docker/CI Pipeline  • Smart Contract    │
│ Peran: Menerima target & batasan scope otorisasi dari developer            │
│ In: Prompt Instruksi & Target Scope   │ Out: Target Context Specification  │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: LEAD ARCHITECT & TRIAGE ENGINE (security_team_triage.py v2.2.0)   │
│ • Keyword Regex Scoring Engine      • Technology Stack Auto-Detection      │
│ • Lead Role Mandate Assignment      • Dynamic Sub-Skill Route Selector     │
│ In: Target Context Specification    │ Out: Assigned Lead + Support Squad   │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: 10 SPECIALIZED SECURITY DIVISIONS (ROLES & RESPONSIBILITIES)      │
├─────────────────────────────────────┬──────────────────────────────────────┤
│ [OFFENSIVE SQUAD]                   │ [DEFENSIVE & BUILD SQUAD]            │
│ ├─ [01] Web & API Penetration Tester│ ├─ [03] AppSec & Invariant Patching  │
│ └─ [02] Red Team Adversary Operator │ ├─ [04] Blue Team & SOC Automation   │
│                                     │ └─ [05] DevSecOps & Cloud Hardening  │
├─────────────────────────────────────┼──────────────────────────────────────┤
│ [INVESTIGATION & INTEL SQUAD]       │ [FRONTIER & GOVERNANCE SQUAD]        │
│ ├─ [06] DFIR Forensics & Malware    │ ├─ [08] Web3 & Smart Contract Auditor│
│ └─ [07] Threat Intel & ATT&CK Hunter│ ├─ [09] AI & LLM Red Teamer          │
│                                     │ └─ [10] Purple Team & CISO Governance│
├─────────────────────────────────────┴──────────────────────────────────────┤
│ In: Role Mandate Assignment         │ Out: Raw Findings & Attack Trees     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: GLOBAL SUB-SKILL ECOSYSTEM (1.214+ SPECIALIZED MODULES)           │
│ • Trail of Bits (95): fp-check, Semgrep Rules, Invariant Compiler Prover   │
│ • Anthropic Cyber (818): Active Directory, Kernel, C2, KAPE, Metasploit    │
│ • Red Hat ProdSec (145): K8s, Container Isolation, SBOM, SLSA Provenance  │ 
│ • Pashov & DarkNavy (45): Solidity Invariant Fuzzing, DeFi Attack Replay   │
│ • Security-Agent & Masriyan (111): AI Jailbreak, OSINT, Network Replay     │
│ In: Raw Exploit Hypothesis          │ Out: In-Depth Telemetry & Proof Data │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 5: STRICT VERIFICATION GATEWAY (fp-check ZERO FALSE-POSITIVE)       │ 
│                                                                            │
│  [Fase 1: Dataflow]         [Fase 2: Bounds]        [Fase 3: PoC Replay]   │
│  ┌───────────────────┐      ┌──────────────────┐    ┌──────────────────┐   │
│  │ Source-to-Sink    │ ───► │ Attacker Control │──► │ Standalone PoC   │   │
│  │ Path Tracing      │      │ & Bounds Proof   │    │ Execution Test   │   │
│  └───────────────────┘      └──────────────────┘    └──────────────────┘   │
│           │                          │                       │             │
│           └──────────────────────────┼───────────────────────┘             │
│                                      ▼                                     │
│                     [Apakah Semua Bukti Terpenuhi?]                        │
│                      ├── TIDAK ──► [DISMISSED] Temuan Palsu Dianulir       │
│                      └── YA    ──► [VERIFIED] Terbukti 100% Exploitable    │
│ In: Candidate Findings              │ Out: Verified Vulnerability Package  │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │                                       
                                      ▼                                       
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 6: STANDARDIZED DUAL DELIVERABLES (OUTPUT LAYER)                     │
├─────────────────────────────────────┬──────────────────────────────────────┤
│ 📊 UNTUK EXECUTIVE & CISO (BISNIS)  │ 🛠️ UNTUK DEVELOPER & OPS (TEKNIS)   │  
│ • CISO Executive Summary Report     │ • Invariant Git Diff Security Patch  │
│ • Risk Heatmap (Likelihood/Impact)  │ • Standalone Reproducible PoC Script │
│ • Estimasi Cost of Breach & ROI     │ • Unit & Regression Test Suite       │
│ • Kepatuhan NIST CSF & ISO 27001    │ • Aturan SIEM/EDR (Sigma YAML & YARA)│
└─────────────────────────────────────┴──────────────────────────────────────┘
</pre>

</div>

> **Legenda Arsitektur:**
> - `┌ ─ ┐ │ └ ┘`: Batas komponen layer sistem yang terisolasi.
> - `▼` / `──►`: Aliran data sekuensial dari input awal menuju verifikasi akhir.
> - `├─` / `└─`: Pembagian tugas ke divisi spesialis atau cabang pengujian.
> - `In / Out`: Kontrak data masuk dan data keluar pada setiap layer.

---

## 🎯 Panduan Prompt per Fitur

Panduan lengkap penggunaan prompt siap copy-paste, disusun dari level dasar hingga mahir:

### 1. Web & API Penetration Testing (Dasar)
* **Kapan dipakai:** Saat menguji aplikasi web, REST API, endpoint GraphQL, atau konfigurasi WAF.
* **Prompt Siap Pakai:**
  ```text
  /security-team Lakukan pengujian penetrasi pada endpoint API auth di repositori ini. Fokus pada validasi token JWT, potensi IDOR, dan mekanisme rate limiting. Buatkan skrip curl PoC untuk setiap celah yang ditemukan.
  ```
* **Contoh Hasil Singkat:** Laporan kerentanan IDOR pada `/api/v1/user/settings` beserta script curl PoC yang membuktikan manipulasi ID pengguna lain tanpa otorisasi.

---

### 2. AppSec & Invariant Patching (Dasar - Menengah)
* **Kapan dipakai:** Saat meninjau kode sumber (*code review*), memperbaiki bug keamanan, atau membuat patch bebas regresi.
* **Prompt Siap Pakai:**
  ```text
  /security-team Review kode di folder src/auth/ untuk celah SQL Injection dan logic flaw. Jika ditemukan celah, jalankan fp-check untuk validasi, lalu berikan kode perbaikan (git diff) dengan pendekatan invariant patch.
  ```
* **Contoh Hasil Singkat:** Patch `git diff` yang mengganti string concatenation dengan parameterized queries dan menambahkan unit test pencegah regresi.

---

### 3. DevSecOps & Container Hardening (Menengah)
* **Kapan dipakai:** Saat mengaudit Dockerfile, manifest Kubernetes, pipeline CI/CD GitHub Actions, atau audit dependensi (SBOM).
* **Prompt Siap Pakai:**
  ```text
  /security-team Audit konfigurasi Dockerfile, docker-compose, dan pipeline CI/CD (GitHub Actions / Jenkins) di repo ini. Jalankan pemindaian kerentanan image dengan Trivy, pastikan container non-root, dan cegah kebocoran secret.
  ```
* **Contoh Hasil Singkat:** Dockerfile yang telah di-hardening dengan Alpine distroless multi-stage build dan workflow GitHub Actions yang dilengkapi gitleaks scanner.

---

### 4. Blue Team & SOC Detection Engineering (Menengah)
* **Kapan dipakai:** Saat ingin membangun sistem monitoring, aturan SIEM, atau memburu jejak intrusi dalam log.
* **Prompt Siap Pakai:**
  ```text
  /security-team Berdasarkan teknik serangan Pass-the-Hash (MITRE T1550.002), buatkan aturan deteksi Sigma YAML untuk Windows Event Log dan aturan Suricata untuk mendeteksi anomali di level jaringan.
  ```
* **Contoh Hasil Singkat:** File konfigurasi `detection.yml` (Sigma Rule) valid dan rule Suricata siap deploy di sensor IDS organisasi.

---

### 5. Threat Intelligence & Threat Hunting (Menengah)
* **Kapan dipakai:** Saat menganalisis taktik grup APT tertentu, ekstraksi IOC (IP, domain, hash), atau korelasi feed ancaman MISP.
* **Prompt Siap Pakai:**
  ```text
  /security-team Analisis feed IOC berikut: [masukkan daftar hash/domain]. Petakan ke matriks MITRE ATT&CK, identifikasi pola campaign threat actor terkait, dan rekomendasikan aksi mitigasi proaktif.
  ```
* **Contoh Hasil Singkat:** Tabel mapping TTPs ke MITRE ATT&CK Navigator beserta rekomendasi firewall blocking rule untuk domain C2 yang teridentifikasi.

---

### 6. DFIR Forensics & Malware Analysis (Menengah - Lanjut)
* **Kapan dipakai:** Saat terjadi insiden kebocoran data, analisis memory dump (RAM), file log server, atau bedah sampel malware.
* **Prompt Siap Pakai:**
  ```text
  /security-team Saya mencurigai adanya webshell pada direktori /var/www/html/. Analisis artefak dan log akses web server berikut, susun kronologi insiden (timeline kejadian), dan buatkan rule YARA untuk mendeteksi varian webshell serupa.
  ```
* **Contoh Hasil Singkat:** Rekonstruksi timeline penyerang berhasil mengunggah file PHP backdoor beserta signature YARA berakurasi tinggi.

---

### 7. Red Team & Adversary Simulation (Lanjut)
* **Kapan dipakai:** Saat merancang skenario simulasi serangan tingkat lanjut, lateral movement di Active Directory, atau audit perimeter internal.
* **Prompt Siap Pakai:**
  ```text
  /security-team Rancang skenario pengujian Red Team untuk arsitektur Active Directory hybrid. Simulasikan attack path dari compromised low-priv user menuju Domain Admin melalui Kerberoasting dan ADCS ESC1 misconfiguration.
  ```
* **Contoh Hasil Singkat:** Blueprint simulasi serangan end-to-end lengkap dengan audit command BloodHound, verifikasi celah, dan mitigasi pengerasan GPO.

---

### 8. Web3 & Smart Contract Security Audit (Lanjut)
* **Kapan dipakai:** Saat mengaudit smart contract Solidity, protokol DeFi, tokenomics, atau pengujian invariant fuzzing dengan Foundry.
* **Prompt Siap Pakai:**
  ```text
  /security-team Audit token contract dan smart contract Solidity di contracts/Vault.sol. Periksa logika transfer, token minting/burn, potensi reentrancy, dan manipulasi flash loan. Tuliskan test suite Foundry (test/Vault.t.sol) yang mendemonstrasikan eksploitasinya.
  ```
* **Contoh Hasil Singkat:** Laporan audit berstandar Pashov Audit Group disertai test suite Foundry yang memicu kegagalan invariant penarikan dana.

---

### 9. AI & LLM Security Red Teaming (Lanjut)
* **Kapan dipakai:** Saat mengevaluasi keamanan sistem berbasis LLM, agentic AI, pipeline RAG, dan perlindungan prompt injection.
* **Prompt Siap Pakai:**
  ```text
  /security-team Lakukan stress test pada prompt dan tool definitions agen AI ini. Uji terhadap direct & indirect prompt injection, tool poisoning, dan kemungkinan eksfiltrasi system prompt atau data sensitif dari vector database.
  ```
* **Contoh Hasil Singkat:** Matrix hasil uji prompt injection adversarial lengkap dengan guardrail regex dan rekomendasi sanitasi konteks retriever.

---

### 10. Purple Team & CISO Board Governance (Mahir / Eksekutif)
* **Kapan dipakai:** Saat menyajikan hasil penilaian keamanan menyeluruh kepada jajaran eksekutif, dewan direksi, atau auditor kepatuhan (ISO 27001/NIST).
* **Prompt Siap Pakai:**
  ```text
  /security-team Gabungkan semua temuan teknis dari audit sistem ini menjadi CISO Executive Summary. Sajikan Risk Matrix (Likelihood vs Impact), dampak finansial bisnis, roadmap remediasi prioritas 30-60-90 hari, dan skor kepatuhan NIST CSF.
  ```
* **Contoh Hasil Singkat:** Dokumen Executive Briefing 2 halaman siap presentasi dengan matriks risiko visual dan estimasi cost-of-breach.

---

### 📋 Tabel Ringkasan Prompt Cepat

| Fitur / Divisi | Shortcut Prompt Rekomendasi |
| :--- | :--- |
| **01. Pentest Web/API** | `/security-team Pentest endpoint API ini dan buat PoC curl untuk verifikasi celah.` |
| **02. Red Team Ops** | `/security-team Analisis attack path Active Directory dan simulasikan lateral movement.` |
| **03. AppSec Patching** | `/security-team Audit kode ini dan berikan invariant patch (git diff) bebas regresi.` |
| **04. Blue Team / SOC** | `/security-team Buatkan aturan deteksi Sigma YAML dan YARA untuk indikator ancaman ini.` |
| **05. DevSecOps** | `/security-team Hardening Dockerfile dan audit pipeline CI/CD GitHub Actions ini.` |
| **06. DFIR Forensics** | `/security-team Rekonstruksi timeline insiden dan identifikasi jejak artefak penyerang.` |
| **07. Threat Hunting** | `/security-team Ekstrak IOC dari log ini dan petakan ke matriks taktik MITRE ATT&CK.` |
| **08. Web3 Solidity** | `/security-team Audit kontrak Solidity ini dan tuliskan suite test exploitasi Foundry.` |
| **09. AI Red Team** | `/security-team Uji ketahanan model LLM terhadap serangan indirect prompt injection.` |
| **10. CISO Governance** | `/security-team Buatkan CISO Executive Summary lengkap dengan Risk Matrix dan roadmap remediasi.` |

---

## 📂 Struktur Folder

```text
security-team/
├── SKILL.md                          # Spesifikasi orkestrasi 10 divisi & protokol fp-check
├── README.md                         # Dokumentasi arsitektur, panduan prompt, dan quick start
├── LICENSE                           # Lisensi open-source MIT
├── .gitignore                        # Konfigurasi proteksi file sensitif & cache
├── scripts/
│   └── security_team_triage.py       # Engine triage CLI/API otomatis: regex scoring & routing
├── references/                       # 8 Playbook & Panduan Operasional Lengkap:
│   ├── role-descriptions.md          # Spesifikasi detail 10 persona divisi keamanan
│   ├── pentest-team-playbook.md      # Metodologi 6 fase web/API/network pentest
│   ├── web3-smart-contract-playbook.md# Invariant fuzzing, DeFi exploits, scaling WAD/RAY
│   ├── ai-llm-redteam-playbook.md    # Jailbreak, prompt injection, tool poisoning
│   ├── purple-team-playbook.md       # Kolaborasi red/blue team & tuning deteksi
│   ├── engagement-types.md           # Model keterlibatan audit & matriks scope
│   ├── escalation-procedures.md      # Prosedur eskalasi insiden & handoff kritis
│   └── security-report-templates.md  # Template laporan CISO Board & temuan teknis
└── tests/
    └── test_triage.py                # Test suite otomatis (schema, edge cases, 10 divisi)
```

<details>
<summary><b>🔍 Rincian Pustaka Sub-Skill yang Didukung (Klik untuk membuka)</b></summary>

- **Anthropic Cybersecurity (818 Sub-Skills):** Eksploitasi, forensik, pentest jaringan, cloud auditing, SOC response.
- **Trail of Bits (95 Sub-Skills):** Verifikasi `fp-check`, Semgrep custom rules, invariant testing, reproduksi bug compiler.
- **Red Hat ProdSec (145 Sub-Skills):** Audit keamanan container, Kubernetes hardening, SLSA provenance, SBOM tooling.
- **Pashov & DarkNavy Web3 (45 Sub-Skills):** Solidity auditing, Foundry fuzzing, DeFi protocol vulnerability scanning.
- **Security Agent Skills (78 Sub-Skills):** Scanner otonom, network recon, OSINT automation, RF hardware analysis.
- **Masriyan Security & Cloudflare:** AI security red teaming, LLM jailbreak analysis, 6-Phase Web Assessment.
</details>

---

## 📌 Riwayat Rilis & Changelog

| Versi | Tipe | Tanggal | Ringkasan Perubahan |
| :--- | :---: | :---: | :--- |
| **v2.2.0** | 🟡 MINOR | 2026-11-06 | **Interactive 8-Bit Cyber SOC GUI (Phase 1)**: Rilis antarmuka visual kantor virtual retro 8-bit (python gui/run.py), mini pixel agent sprites, dispatcher kartu tugas (*Task Cards*), Web Audio API chiptune SFX, keamanan anti-CSWSH (127.0.0.1, Origin check, session token handshake, dry-run default), font pixel offline bundled, dan Claude Code CLI bridge (stream-json). |

| **v2.1.1** | 🟢 PATCH | 2026-11-06 | **Hardening Regex & Anti-False-Negative**: Menambahkan dukungan kontekstual *token contract* (`token contract`, `mint/burn`) pada divisi Web3 serta kata majemuk *DevSecOps* (`Dockerfile`, `docker-compose`, `jenkins`, `trivy`, `helm`). Menambahkan 2 unit test baru di `tests/test_triage.py` (total 12 unit tests, 100% PASS). |
| **v2.1.0** | 🟡 MINOR | 2026-11-06 | **Rilis Stabil Perdana**: Integrasi triage engine 10 divisi cyber security, auto-detection stack teknologi, isolasi token auth (JWT/OAuth) vs crypto token, proteksi encoding terminal UTF-8, dukungan input file `-f` dan stream `sys.stdin`, diverifikasi lulus 26 skenario benchmark 4-tier. |

---

## ❓ FAQ (Frequently Asked Questions)

<details>
<summary><b>1. Mengapa harus menggunakan security-team dibanding scanner statis biasa?</b></summary>
Scanner statis konvensional hanya menghasilkan ribuan peringatan mentah yang 70% di antaranya seringkali false-positive. <code>security-team</code> menggabungkan 10 perspektif divisi cyber security dan mewajibkan verifikasi ketat (PoC yang tervalidasi) sebelum memberikan patch kode yang siap dimerge.
</details>

<details>
<summary><b>2. Apakah aman dijalankan pada repositori produksi?</b></summary>
Sangat aman. Secara default, <code>security-team</code> beroperasi dalam mode audit dan verifikasi analitik. Tidak ada aksi destruktif yang dijalankan tanpa konfirmasi eksplisit dari pengguna.
</details>

<details>
<summary><b>3. Bagaimana jika saya hanya membutuhkan satu divisi tertentu (misal: hanya Solidity)?</b></summary>
Triage engine kami secara otomatis mengenali ekstensi file <code>.sol</code> atau instruksi spesifik Web3, sehingga orkestrator akan langsung memusatkan sumber daya ke <b>Role 8 (Web3 Auditor)</b> tanpa overhead yang tidak perlu.
</details>

<details>
<summary><b>4. Apakah bisa dipakai di lingkungan offline / air-gapped?</b></summary>
Bisa. Script triage dan modul audit berbasis analisis pola kode lokal dapat berjalan sepenuhnya tanpa ketergantungan koneksi internet eksternal.
</details>

---

## 🤝 Kontribusi, Lisensi & Kontak

- **Kontribusi:** Pull Request dan penambahan varian skenario keamanan baru sangat disambut! Silakan baca panduan kontribusi sebelum membuka PR.
- **Lisensi:** Didistribusikan di bawah lisensi terbuka [MIT License](LICENSE).
- **Author & Maintainer:** **Rey-CpuU** ([GitHub Profile](https://github.com/Rey-CpuU))
- **Email:** `elon0809@gmail.com`
- **Official Repository:** [https://github.com/Rey-CpuU/security](https://github.com/Rey-CpuU/security)
