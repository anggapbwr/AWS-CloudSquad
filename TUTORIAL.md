# 📖 AWS CloudSquad — Tutorial: Zero to First Mission

> **Pemula?** Tidak masalah. Tutorial ini memandu kamu dari nol hingga menjalankan pipeline DevOps AI pertama, langkah demi langkah.

---

## Daftar Isi

1. [Apa itu AWS CloudSquad?](#1-apa-itu-aws-cloudsquad)
2. [Cara Kerja — Konsep Dasar](#2-cara-kerja--konsep-dasar)
3. [Persiapan (Prerequisites)](#3-persiapan-prerequisites)
4. [Instalasi & Setup](#4-instalasi--setup)
5. [Membuka Cockpit Dashboard](#5-membuka-cockpit-dashboard)
6. [Membuat Mission Pertama](#6-membuat-mission-pertama)
7. [Menjalankan Pipeline](#7-menjalankan-pipeline)
8. [Memahami Output — Agent per Agent](#8-memahami-output--agent-per-agent)
9. [Melihat Artifacts (Kode yang Dihasilkan)](#9-melihat-artifacts-kode-yang-dihasilkan)
10. [Final Report & Download](#10-final-report--download)
11. [Troubleshooting Umum](#11-troubleshooting-umum)
12. [Langkah Selanjutnya](#12-langkah-selanjutnya)

---

## 1. Apa itu AWS CloudSquad?

AWS CloudSquad adalah platform **autonomous DevOps** yang menggunakan **6 AI agent** untuk menjalankan seluruh siklus rekayasa cloud secara otomatis — mulai dari desain arsitektur hingga deployment ke AWS dan testing performa.

**Analoginya:** Bayangkan kamu punya tim engineers lengkap (Architect, DBA, Backend Dev, DevOps, Security Engineer, SRE) yang bekerja secara otomatis, berurutan, dan saling mewariskan konteks pekerjaan.

```
Kamu input requirement  →  6 Agent bekerja  →  Kode + Infrastruktur + Report
```

**Yang dihasilkan secara otomatis:**
- Diagram arsitektur AWS interaktif (React Flow)
- Schema PostgreSQL + migration scripts
- Aplikasi FastAPI + Dockerfile + unit tests
- Terraform modules (VPC, ALB, ECS, RDS, IAM)
- Security scan report (Semgrep, Trivy, SBOM)
- k6 benchmark results + SRE final report

---

## 2. Cara Kerja — Konsep Dasar

### Pipeline Sequential (Berurutan)

```
Stage 1: ARCHITECT
    ↓ (hasilkan context arsitektur)
Stage 2: DATABASE
    ↓ (hasilkan schema berdasarkan arsitektur)
Stage 3: APPLICATION
    ↓ (hasilkan kode berdasarkan schema)
Stage 4: INFRASTRUCTURE
    ↓ (hasilkan IaC berdasarkan arsitektur)
Stage 5: DEVSECOPS  ← ⚠️ HARD GATE (gagal = pipeline berhenti)
    ↓ (deploy ke AWS atau simulasi dry-run)
Stage 6: DEPLOYMENT
    ↓
Stage 7: SRE (k6 benchmark)
    ↓
Stage 8: FINAL REPORT
```

Setiap stage menghasilkan **artifacts** (file kode) dan mengirim **event** ke dashboard secara real-time via WebSocket.

### Mode Operasi

| Mode | Keterangan |
|---|---|
| `DEMO_MODE=true` + `dry-run` | **Default.** Simulasi penuh tanpa AWS credentials. Cocok untuk evaluasi & development. |
| `DEMO_MODE=false` + `dry-run` | Memanggil API LLM nyata (butuh OpenAI/Anthropic key), tapi tidak deploy ke AWS. |
| `DEMO_MODE=false` + `apply` | Deploy ke AWS sungguhan. Butuh AWS credentials dengan IAM permissions. |

---

## 3. Persiapan (Prerequisites)

### Wajib
| Software | Versi Minimum | Link Download |
|---|---|---|
| **Docker Desktop** | 24.0+ | https://www.docker.com/products/docker-desktop |
| **Git** | 2.40+ | https://git-scm.com/downloads |

### Cek Instalasi

Buka terminal (PowerShell / Command Prompt / Bash) dan jalankan:

```bash
# Cek Docker
docker --version
# Output yang diharapkan: Docker version 24.x.x atau lebih baru

docker compose version
# Output yang diharapkan: Docker Compose version v2.20.x atau lebih baru

# Cek Git
git --version
# Output yang diharapkan: git version 2.40.x atau lebih baru
```

> ⚠️ **Docker Desktop harus dalam keadaan berjalan** (ikon Docker terlihat di system tray/menu bar) sebelum melanjutkan.

---

## 4. Instalasi & Setup

### Step 4.1 — Clone Repository

```bash
git clone https://github.com/anggapbwr/AWS-CloudSquad.git
cd aws-cloudsquad
```

### Step 4.2 — Buat File Konfigurasi

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

### Step 4.3 — (Opsional) Edit Konfigurasi

Buka file `.env` dengan text editor apapun. Untuk **percobaan pertama**, **tidak perlu mengubah apapun** — default-nya sudah dikonfigurasi untuk mode demo lokal.

Jika ingin menggunakan AI nyata (bukan deterministic/simulasi):

```env
# Ganti ini:
LLM_PROVIDER=deterministic

# Menjadi salah satu:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key...

# atau:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...your-key...
```

### Step 4.4 — Jalankan Semua Service

```bash
docker compose up --build
```

Proses build pertama kali membutuhkan **3–8 menit** (mengunduh image dan membangun container). Tunggu hingga muncul output seperti:

```
✅ backend       | Uvicorn running on http://0.0.0.0:8000
✅ frontend      | ▲ Next.js 16.3.6
✅ temporal      | Temporal server started
✅ postgres      | database system is ready to accept connections
✅ redis         | Ready to accept connections
```

---

## 5. Membuka Cockpit Dashboard

Buka browser dan navigasikan ke:

**[http://localhost:3000](http://localhost:3000)**

Kamu akan melihat tampilan **AWS CloudSquad Cockpit** — sebuah dashboard dark-mode premium dengan:

| Area | Keterangan |
|---|---|
| **Header** | Nama mission, status pipeline, region AWS, estimasi biaya, dan tombol aksi |
| **Engineering Squad** | 6 kartu agent dengan status (WAITING / RUNNING / COMPLETED) |
| **Architecture Canvas** | Diagram topologi AWS interaktif (React Flow) |
| **Audit Event Stream** | Log real-time event dari pipeline (WebSocket) |
| **Observability & Benchmark** | Grafik telemetri performa (muncul setelah SRE selesai) |

---

## 6. Membuat Mission Pertama

### Step 6.1 — Klik "New Mission"

Klik tombol **"New Mission"** di pojok kanan atas header.

Sebuah modal akan muncul dengan form konfigurasi.

### Step 6.2 — Gunakan Quick Preset

Di bagian **"Quick Presets"**, klik salah satu preset:
- **E-Commerce Flash Sale** ← Disarankan untuk percobaan pertama
- **SaaS Multi-Tenant API**
- **Microservices Platform**

Preset akan mengisi otomatis semua field.

### Step 6.3 — Konfigurasi Manual (Opsional)

Jika ingin konfigurasi sendiri:

| Field | Nilai Contoh | Keterangan |
|---|---|---|
| **Mission Name** | E-Commerce Flash Sale Platform | Nama identifier mission |
| **Workload Requirements** | High concurrency e-commerce... | Deskripsi kebutuhan teknis |
| **Target Throughput** | 1,000 RPS | Target request per second |
| **Monthly Budget** | $300 USD | Batasan anggaran AWS |
| **Availability SLA** | 99.95% | Target uptime |
| **AWS Region** | ap-southeast-1 (Singapore) | Region deployment target |

### Step 6.4 — Klik "Initialize Mission"

Klik tombol **"Initialize Mission"** (dengan ikon roket 🚀).

Mission baru akan terbuat dan muncul di dashboard. Status akan berubah menjadi **"Ready"** (biru).

---

## 7. Menjalankan Pipeline

### Step 7.1 — Klik "Launch Mission"

Klik tombol **"Launch Mission"** di header (tombol gradien cyan-biru).

Pipeline dimulai! Perhatikan:

1. **Header** — Status berubah menjadi animasi spinning (pipeline running)
2. **Progress bar** — Muncul di atas header, bergerak seiring stage selesai
3. **Engineering Squad** — Kartu agent berubah status satu per satu:
   - ⬜ **WAITING** → 🔵 **RUNNING** (animasi pulse) → ✅ **COMPLETED** (hijau)
4. **Audit Event Stream** — Log event baru muncul real-time dari kanan
5. **Architecture Canvas** — Diagram topologi muncul setelah ArchitectAgent selesai

### Step 7.2 — Pantau Progress

Setiap stage membutuhkan waktu berbeda:

| Stage | Estimasi Waktu | Yang Terjadi |
|---|---|---|
| ARCHITECT | 10–30 detik | Mendesain arsitektur, generate topology diagram |
| DATABASE | 10–20 detik | Mendesain schema PostgreSQL, indexing strategy |
| APPLICATION | 15–30 detik | Generate FastAPI app, Dockerfile, unit tests |
| INFRASTRUCTURE | 20–40 detik | Generate Terraform modules, validasi `fmt/validate` |
| DEVSECOPS | 15–30 detik | Semgrep, Trivy scan, Syft SBOM, Cosign |
| DEPLOYMENT | 10–20 detik | Simulasi push ECR + deploy ECS (dry-run mode) |
| SRE | 20–40 detik | k6 benchmark, generate telemetry data |
| FINAL REPORT | 5–10 detik | Compile semua hasil jadi laporan final |

> 🕐 **Total waktu:** ~2–4 menit dalam DEMO_MODE=true

### Step 7.3 — Selesai! 🎉

Ketika pipeline selesai, kamu akan melihat:
- Confetti animation 🎉 di layar
- Semua kartu agent berubah hijau **COMPLETED**
- Status di header menjadi **"Completed"**
- Grafik telemetri muncul di bagian bawah
- Tombol **"Final Report"** muncul di header

---

## 8. Memahami Output — Agent per Agent

### 🏛️ Agent 1: Solution Architect

**Apa yang dilakukan:** Menerjemahkan requirements kamu menjadi arsitektur AWS Multi-AZ yang optimal.

**Output yang terlihat di dashboard:**
- Diagram topologi interaktif muncul di **Architecture Canvas**
- Node-node AWS (CloudFront, ALB, ECS, RDS, S3, dll) dapat diklik
- Klik sebuah node → inspector muncul dengan detail service, estimasi biaya, redundancy

**Artifacts yang dihasilkan:**
```
architecture.json          ← Definisi nodes & edges untuk React Flow
architecture_description.md ← Penjelasan arsitektur dalam teks
cost_breakdown.json        ← Estimasi biaya per service per bulan
```

---

### 🗄️ Agent 2: Database Specialist

**Apa yang dilakukan:** Merancang schema PostgreSQL 16 yang optimal untuk kebutuhan throughput tinggi.

**Output:**
```
schema.sql                 ← CREATE TABLE dengan constraints
migrations/001_initial.sql ← Alembic migration file
indexes.sql                ← Compound indexes untuk high RPS
```

---

### 💻 Agent 3: Backend Engineer

**Apa yang dilakukan:** Membuat aplikasi FastAPI lengkap dengan health endpoint, autentikasi, dan Docker setup.

**Output:**
```
app.py / main.py           ← FastAPI application
models.py                  ← SQLAlchemy ORM models
Dockerfile                 ← Non-root container (UID 10001)
docker-compose.yml         ← Local development setup
tests/test_api.py          ← Unit tests
requirements.txt           ← Python dependencies
```

---

### 🏗️ Agent 4: DevOps Engineer

**Apa yang dilakukan:** Membuat Terraform IaC modular sesuai arsitektur dari Agent 1.

**Output:**
```
main.tf                    ← Root Terraform config
variables.tf               ← Input variables
outputs.tf                 ← Output values
modules/vpc/               ← VPC + subnets + security groups
modules/alb/               ← Application Load Balancer
modules/ecs/               ← ECS Cluster + Service + Task Definition
modules/rds/               ← RDS PostgreSQL + parameter group
modules/iam/               ← IAM roles & policies
```

---

### 🛡️ Agent 5: DevSecOps Officer

**Apa yang dilakukan:** Menjalankan security scanning pipeline. Jika ada **CRITICAL CVE**, pipeline berhenti.

**Output:**
```
security-report.json       ← Hasil scan semua tools
semgrep-report.json        ← SAST findings
trivy-report.json          ← Container CVE scan
sbom.json                  ← Software Bill of Materials (Syft)
cosign-verification.json   ← Image signature status
```

**Status yang mungkin:**
- ✅ **PASSED** — Tidak ada critical vulnerability
- ❌ **FAILED** — Ditemukan CRITICAL CVE → pipeline berhenti, perlu remediation

---

### 📈 Agent 6: SRE Lead

**Apa yang dilakukan:** Menjalankan k6 load test multi-stage dan menganalisis hasilnya.

**Tahapan benchmark:**
```
Baseline  (30s  @ 10% target RPS)    ← Establish baseline
Load      (60s  @ 100% target RPS)   ← Normal production load
Stress    (60s  @ 150% target RPS)   ← Above capacity test
Spike     (30s  @ 300% target RPS)   ← Sudden traffic spike
Recovery  (30s  @ 50% target RPS)    ← Recovery verification
```

**Output:**
```
sre-report.json            ← Structured SRE analysis
k6-results.json            ← Raw benchmark data
telemetry.json             ← Metrics (RPS, P50/P95/P99, error rate)
```

**Setelah selesai, grafik telemetri muncul di dashboard:**
- Throughput (RPS)
- P95 Latency (ms)
- Error Rate (%)
- CPU & Memory utilization
- Monthly cost estimate

---

## 9. Melihat Artifacts (Kode yang Dihasilkan)

### Membuka Artifact Inspector

Pada kartu agent yang sudah **COMPLETED**, lihat footer kartu — ada link **"X files"** berwarna (contoh: `6 files`). Klik link tersebut.

Atau, klik kartu agent manapun yang completed untuk membuka **Artifact Inspector**.

### Navigasi di Artifact Inspector

```
┌─────────────────────────────────────────────────────────┐
│  📁 Artifact Inspector                    [Copy] [⬇️ Download] [✕] │
├──────────────────┬──────────────────────────────────────┤
│  📂 architect    │                                      │
│    .json arch... │   {                                  │
│    .md  desc...  │     "nodes": [...],                  │
│  📂 database     │     "edges": [...]                   │
│    .sql schema   │   }                                  │
│  📂 application  │                                      │
│    .py  app      │                                      │
│    Dockerfile    │                                      │
│  📂 infrastructure│                                     │
│    .tf  main     │                                      │
│    .tf  modules  │                                      │
└──────────────────┴──────────────────────────────────────┘
```

**Fitur:**
- **Sidebar kiri** — File tree dikelompokkan per agent, dengan color coding ekstensi file
- **Panel kanan** — Code viewer dengan JetBrains Mono font
- **Copy** — Copy isi file ke clipboard
- **Download** — Download file individual

### Download Semua Artifacts

Artifacts tersimpan di server di direktori `generated-output/` (di dalam Docker volume). Untuk mengaksesnya di host:

```bash
# Lihat isi generated output
ls ./generated-output/

# Atau akses via API
curl http://localhost:8000/api/artifacts/{mission_id}
```

---

## 10. Final Report & Download

### Membuka Final Report

Setelah mission **COMPLETED**, tombol **"Final Report"** muncul di header (ungu/indigo). Klik tombol tersebut.

### Isi Final Report

Report berisi dua tab:

**Tab "Mission Report" (Markdown):**
```markdown
# AWS CloudSquad Final Engineering Report
## Mission: E-Commerce Flash Sale Platform

### Executive Summary
...

### Architecture Decisions
...

### Security Gate Results
...

### SRE Analysis
#### Observed Facts (from k6 benchmark):
- Peak RPS Achieved: 1,247 req/s
- P95 Latency: 142ms
- Error Rate: 0.03%

#### Technical Inferences:
...

#### Remediation Proposals:
...

### Cost Analysis
| Service    | Monthly Cost |
|------------|-------------|
| ECS Fargate| $45.00      |
| RDS Multi-AZ| $65.00     |
...
```

**Tab "Executive Summary" (JSON):**
Raw JSON data yang bisa digunakan untuk integrasi programatik.

### Download Report

Klik **"Download .md"** untuk menyimpan report sebagai file Markdown.

Format nama file: `AWS-CloudSquad-Report-{Mission-Name}.md`

---

## 11. Troubleshooting Umum

### ❌ `docker compose up` gagal — port sudah digunakan

```
Error: bind: address already in use (port 3000 / 8000 / 5432)
```

**Solusi:** Stop service yang menggunakan port tersebut, atau edit `docker-compose.yml` untuk mengubah port mapping:
```yaml
ports:
  - "3001:3000"  # Ubah port host dari 3000 ke 3001
```

---

### ❌ Halaman kosong / loading terus di browser

**Cek apakah backend sudah running:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

**Jika belum ready**, tunggu 30-60 detik untuk inisialisasi database.

---

### ❌ Mission stuck di stage tertentu

**Lihat logs:**
```bash
# Logs semua service
docker compose logs -f

# Logs spesifik worker (di sinilah agent berjalan)
docker compose logs -f worker

# Logs backend
docker compose logs -f backend
```

**Reset mission:**
```bash
# Lihat semua missions
curl http://localhost:8000/api/missions

# Buat mission baru dan coba lagi
```

---

### ❌ Frontend tidak connect ke backend

Pastikan environment variable di `.env` sudah benar:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

Jika menggunakan Docker Compose, nilai ini sudah dikonfigurasi otomatis.

---

### ❌ Temporal Worker tidak start

```bash
docker compose logs temporal
docker compose logs worker
```

Temporal butuh PostgreSQL healthy sebelum bisa start. Biasanya resolve sendiri setelah 30-60 detik. Coba:
```bash
docker compose restart worker
```

---

### ❌ Ingin reset semua data

```bash
# Stop semua container + hapus volume
docker compose down -v

# Jalankan ulang fresh
docker compose up --build
```

> ⚠️ **Peringatan:** `docker compose down -v` menghapus semua data termasuk database PostgreSQL!

---

## 12. Langkah Selanjutnya

### Eksplorasi Lebih Lanjut

**Temporal Web UI** — Lihat workflow execution, history, dan retry:
```
http://localhost:8088
```

**FastAPI Swagger UI** — Eksplor semua API endpoint secara interaktif:
```
http://localhost:8000/docs
```

**Run Backend Tests:**
```bash
# Masuk ke container backend
docker compose exec backend python -m pytest tests/ -v
```

### Konfigurasi LLM Nyata

Untuk menggunakan AI engine sungguhan (bukan deterministic/simulasi), edit `.env`:

```env
# Gunakan OpenAI GPT-4
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# atau Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Restart setelah mengubah:
```bash
docker compose restart backend worker
```

### Deploy ke AWS Sungguhan

Untuk menjalankan deployment ke AWS nyata:

1. Setup AWS credentials:
```bash
aws configure
# atau set di .env:
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

2. Ubah mode di `.env`:
```env
DEPLOYMENT_MODE=apply
DEMO_MODE=false
```

3. Pastikan IAM user/role memiliki permissions:
   - `ecs:*`, `ecr:*`, `elbv2:*`
   - `rds:*`, `s3:*`, `cloudwatch:*`
   - `iam:PassRole`, `logs:*`

### Kustomisasi Mission

Buat mission template kustom di direktori `missions/` untuk workload spesifik kamu.

---

## 📚 Referensi

| Dokumen | Link |
|---|---|
| README Lengkap | [README.md](README.md) |
| Arsitektur & Design Philosophy | [docs/architecture.md](docs/architecture.md) |
| Detail 6 Agent | [docs/agents.md](docs/agents.md) |
| Temporal Workflow | [docs/workflow.md](docs/workflow.md) |
| AWS Deployment Guide | [docs/aws-deployment.md](docs/aws-deployment.md) |
| DevSecOps & Security Gates | [docs/security.md](docs/security.md) |
| Performance Testing & SRE | [docs/performance-testing.md](docs/performance-testing.md) |

---

<div align="center">

*AWS CloudSquad v2.0 · Autonomous DevOps & Cloud Engineering Platform*

**Selamat mencoba! 🚀**

</div>
