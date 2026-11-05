```text
  ____  _____ ____ _   _ ____  ___ _______   __ _____ _____    _    __  __ 
 / ___|| ____/ ___| | | |  _ \|_ _|_   _\ \ / /|_   _| ____|  / \  |  \/  |
 \___ \|  _|| |   | | | | |_) || |  | |  \ V /   | | |  _|   / _ \ | |\/| |
  ___) | |__| |___| |_| |  _ < | |  | |   | |    | | | |___ / ___ \| |  | |
 |____/|_____\____|\___/|_| \_\___| |_|   |_|    |_| |_____/_/   \_\_|  |_|
================================================================================
          AUTONOMOUS CYBER SECURITY SQUAD FOR AI CODING ASSISTANTS
================================================================================
```

# 🛡️ security-team

> Satu skill orkestrator untuk memimpin 10 divisi cyber security spesialis dan 1.200+ modul keamanan enterprise langsung di AI coding assistant Anda.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Antigravity%20%7C%20Claude%20Code%20%7C%20Codex-brightgreen)](https://github.com/Rey-CpuU/security)
[![Specialized Roles](https://img.shields.io/badge/Specialized%20Roles-10%20Divisions-blueviolet)](https://github.com/Rey-CpuU/security)
[![Sub-Skills Ecosystem](https://img.shields.io/badge/Sub--Skills-1%2C214%2B%20Modules-orange)](https://github.com/Rey-CpuU/security)
[![Verification](https://img.shields.io/badge/Verification-Zero%20False--Positive-success)](https://github.com/Rey-CpuU/security)

---

## 🎬 Demo / Preview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ > /security-team Audit repo ini dan buatkan patch aman untuk celah kritis   │
├─────────────────────────────────────────────────────────────────────────────┤
│ [1/4] 🔍 Triaging Context: Python FastAPI + PostgreSQL + JWT Authentication │
│ [2/4] 👥 Mobilizing Roles: [AppSec Engineer] & [Web Penetration Tester]     │
│ [3/4] 🛡️ Verifying Sinks: fp-check 3-Phase Verification (0 False-Positive) │
│ [4/4] 📦 Deliverable Ready: 1 Verified Bug (IDOR) + Invariant Patch (Diff)  │
└─────────────────────────────────────────────────────────────────────────────┘
```
> *Tampilan eksekusi real-time saat `security-team` menerima prompt, membedah konteks, memanggil sub-skill relevan, dan menghasilkan perbaikan kode siap-merge.*

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
| **01** | **Web & API Penetration Testing** | Audit kerentanan OWASP Top 10, REST/GraphQL, dan bypass WAF. | `09-web-security`, `api-testing` |
| **02** | **AppSec & Invariant Patching** | Analisis SAST sumber kode dan penambalan bug berbasis invariant fix. | `fp-check`, `implement-patch` |
| **03** | **DevSecOps & Cloud Hardening** | Audit postur CI/CD, scanning container Docker/K8s, dan kepatuhan SBOM. | `10-cloud-security`, `trivy` |
| **04** | **Blue Team & SOC Engineering** | Pembuatan aturan deteksi SIEM (Sigma), YARA, dan otomatisasi triage alert. | `11-csoc-automation`, `sigma` |
| **05** | **Threat Intel & Threat Hunting** | Pemetaan taktik ancaman MITRE ATT&CK dan ekstraksi indikator IOC. | `06-threat-hunting`, `misp` |
| **06** | **DFIR & Malware Analysis** | Investigasi forensik disk, memory dump (KAPE/Volatility), dan reverse malware. | `04-reverse-eng`, `05-malware` |
| **07** | **Red Team & Adversary Simulation** | Simulasi serangan Active Directory, Kerberoasting, dan pengujian C2. | `14-red-team-ops`, `bloodhound` |
| **08** | **Web3 & Smart Contract Audit** | Audit kontrak Solidity, DeFi attack simulation, dan invariant fuzzing. | `contract-auditor`, `pashov` |
| **09** | **AI & LLM Red Teaming** | Uji ketahanan model terhadap prompt injection, jailbreak, dan data poisoning.| `continuous-llm-red-teaming` |
| **10** | **Purple Team & Governance (CISO)** | Evaluasi risiko komprehensif, maturitas NIST/ISO 27001, dan CISO board deck. | `cybersecurity-pro`, `grc` |

---

## 🚀 Quick Start

Mulai gunakan `security-team` dalam 3 langkah mudah:

```bash
# 1. Clone repositori ke direktori workspace lokal Anda
git clone https://github.com/Rey-CpuU/security.git

# 2. Salin folder skill ke direktori agent Antigravity / Claude Code
cp -r security/skills/security-team ~/.gemini/config/skills/

# 3. Jalankan audit pertama Anda di chat coding assistant
/security-team Audit keamanan repository ini dan cari potensi kebocoran rahasia
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

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        USER PROMPT / SECURITY GOAL                           │
│  In: Kode Sumber, URL Web, Smart Contract, PCAP, Memory Dump, Cloud Config   │
│  Out: Instruksi tugas dan target batasan ruang lingkup (Scope)               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│             security-team (LEAD SECURITY ARCHITECT & ORCHESTRATOR)           │
│  Peran: Mengurai intensi pengguna dan menetapkan rencana strategi audit      │
│  In: Prompt mentah                   │ Out: Context Plan & Role Mandate      │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│              TRIAGE ENGINE (scripts/security_team_triage.py)                 │
│  Peran: Scoring kata kunci (regex) & seleksi otomatis modul sub-skill        │
│  In: Task Context                    │ Out: 1 Lead Role + Support Sub-Skills │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  10 DIVISI SPESIALIS KEAMANAN (ROLE EXECUTION)               │
│  ├─ [01] Pentest Web/API      ├─ [04] Blue Team / SOC  ├─ [07] Threat Intel  │
│  ├─ [02] AppSec & Patching    ├─ [05] DevSecOps        ├─ [08] Web3 / DeFi   │
│  ├─ [03] Cloud & Container    ├─ [06] DFIR Forensics   ├─ [09] AI Red Team   │
│                               └─ [10] Purple Team & CISO Governance          │
│  In: Targeted Scope                  │ Out: Raw Findings & Attack Trees      │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│             PUSTAKA 1.214+ SUB-SKILL TERPADU (GLOBAL ECOSYSTEM HARNESS)      │
│  Peran: Modul taktis (Anthropic, Trail of Bits, Red Hat, DarkNavy, Pashov)   │
│  In: Vulnerability Candidate         │ Out: Deep Static/Dynamic Evidence     │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│            VERIFIKASI KETAT: fp-check (ZERO FALSE-POSITIVE ENGINE)           │
│  Peran: Uji pembuktian 3 fase: Source-to-Sink ─► Exploitability ─► PoC Test  │
│  In: Unverified Finding              │ Out: Proven Exploit ATAU Rejection    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         STANDARDIZED DELIVERABLES                            │
│  • Executive CISO & Risk Matrix      • Reproducible Exploit PoCs             │
│  • Invariant Security Patches (Diff) • SIEM & EDR Detection Rules (Sigma/YARA│
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Legenda Arsitektur:**
> - `┌─┐│└─┘`: Batas komponen terisolasi.
> - `▼`: Aliran data sekuensial (piped context).
> - `├─`: Distribusi tugas ke divisi spesialis.

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
  /security-team Audit konfigurasi Dockerfile dan file .github/workflows/ di repo ini. Pastikan container berjalan sebagai non-root, tidak ada secret yang hardcoded, dan dependency tervalidasi terhadap database CVE terbaru.
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
  /security-team Audit kontrak Solidity di contracts/Vault.sol. Periksa potensi reentrancy, flash loan price manipulation, dan access control flaw. Tuliskan test suite Foundry (test/Vault.t.sol) yang mendemonstrasikan eksploitasinya.
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

| Fitur | Shortcut Prompt Rekomendasi |
| :--- | :--- |
| **01. Pentest Web/API** | `/security-team Pentest endpoint API ini dan buat PoC curl untuk verifikasi celah.` |
| **02. AppSec Patching** | `/security-team Audit kode ini dan berikan invariant patch (git diff) bebas regresi.` |
| **03. DevSecOps** | `/security-team Hardening Dockerfile dan audit pipeline CI/CD GitHub Actions ini.` |
| **04. Blue Team / SOC** | `/security-team Buatkan aturan deteksi Sigma YAML dan YARA untuk indikator ancaman ini.` |
| **05. Threat Hunting** | `/security-team Ekstrak IOC dari log ini dan petakan ke matriks taktik MITRE ATT&CK.` |
| **06. DFIR Forensics** | `/security-team Rekonstruksi timeline insiden dan identifikasi jejak artefak penyerang.` |
| **07. Red Team Ops** | `/security-team Analisis attack path Active Directory dan simulasikan lateral movement.` |
| **08. Web3 Solidity** | `/security-team Audit kontrak Solidity ini dan tuliskan suite test exploitasi Foundry.` |
| **09. AI Red Team** | `/security-team Uji ketahanan model LLM terhadap serangan indirect prompt injection.` |
| **10. CISO Governance** | `/security-team Buatkan CISO Executive Summary lengkap dengan Risk Matrix dan roadmap remediasi.` |

---

## 📂 Struktur Folder

```text
security-team/
├── SKILL.md                          # Panduan orkestrasi 10 divisi & protokol fp-check
├── README.md                         # Dokumentasi arsitektur, panduan, dan quick start
└── scripts/
    └── security_team_triage.py       # Engine triage otomatis: scoring regex & routing role
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
