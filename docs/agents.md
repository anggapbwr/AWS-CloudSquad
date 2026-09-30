# AWS CloudSquad — The 6 Engineering Agents

AWS CloudSquad orchestrates six engineering agent roles across a deterministic workflow pipeline.

---

## Agent Roster Overview

```text
1. ArchitectAgent      (Solution Architecture & AWS Cost Topology)
2. DatabaseAgent       (PostgreSQL Schema, Indexes & Migrations)
3. ApplicationAgent    (Containerized FastAPI Microservice & Testing)
4. InfrastructureAgent (Modular Terraform VPC, ALB, ECS, RDS, IAM)
5. DevSecOpsAgent      (Semgrep, Gitleaks, Trivy, Syft, Cosign, Checkov)
6. SREAgent            (k6 Performance Benchmark & Reliability Analysis)
```

> **Note on Deployment**: Deployment is a deterministic engineering stage within the workflow engine, not an AI agent. It executes Docker builds, ECR pushes, Terraform applies, and ALB `/health` probes deterministically without LLM hallucinations.

---

### 1. ArchitectAgent
* **Role**: Principal Cloud Architect
* **Input**: Mission Requirements (Target RPS, Availability SLA, Monthly Budget, AWS Region, Workload Category)
* **Responsibilities**:
  - Translates SLA and throughput targets into AWS service selections.
  - Generates reactive React Flow topology diagram nodes and edges.
  - Calculates granular monthly AWS cost estimates with budget validation (`WITHIN_BUDGET` vs `EXCEEDS_BUDGET`).
  - Authors the executive Architecture Rationale document.
* **Outputs**:
  - `architecture.json`
  - `architecture-diagram.json`
  - `service-selection.json`
  - `cost-estimate.json`
  - `architecture-rationale.md`

---

### 2. DatabaseAgent
* **Role**: Lead DBA Specialist
* **Input**: Consumes `ArchitectAgent` output (target database engine and RPS parameters)
* **Responsibilities**:
  - Designs normalized, high-concurrency relational schemas (PostgreSQL 16).
  - Implements optimistic concurrency controls (`version` column) and unique idempotency constraints.
  - Generates compound B-Tree indexes for sub-millisecond query responses under high RPS.
  - Produces ready-to-execute SQL migrations and connection pooling parameters.
* **Outputs**:
  - `schema.sql`
  - `migration.sql`
  - `database-config.json`
  - `database-design.md`

---

### 3. ApplicationAgent
* **Role**: Senior Backend & Container Engineer
* **Input**: Data models, endpoints, and architecture requirements
* **Responsibilities**:
  - Scaffolds a production-grade asynchronous FastAPI microservice.
  - Implements mandatory health probes: `GET /health` and `GET /ready`.
  - Hardens the Dockerfile with non-root user execution (UID `10001:10001`).
  - Authors unit tests validating endpoints with `pytest` and `TestClient`.
* **Outputs**:
  - `app_main.py`
  - `Dockerfile`
  - `app_requirements.txt`
  - `test_main.py`

---

### 4. InfrastructureAgent
* **Role**: Senior DevOps / IaC Engineer
* **Input**: Application container requirements, networking topologies, and security boundaries
* **Responsibilities**:
  - Generates modular, reusable Terraform code (`modules/vpc`, `modules/alb`, `modules/ecs`, `modules/ecr`, `modules/rds`, `modules/iam`, `modules/monitoring`).
  - Enforces private subnet placement for database and compute tasks.
  - Runs deterministic validation gates: `terraform fmt`, `terraform validate`, and `terraform plan`.
* **Outputs**:
  - `main.tf`
  - `variables.tf`
  - `outputs.tf`
  - `modules_vpc.tf`
  - `terraform-validation.json`

---

### 5. DevSecOpsAgent
* **Role**: Security & Compliance Officer
* **Input**: Application source code, container image definitions, and Terraform manifests
* **Responsibilities**:
  - **SAST**: Runs Semgrep static code analysis against OWASP Top 10 Python rulesets.
  - **Secret Detection**: Runs Gitleaks scans to block any leaked AWS keys or credentials.
  - **Container Vulnerability**: Runs Trivy container image scanning with zero-tolerance threshold for `CRITICAL` CVEs.
  - **Software Supply Chain**: Generates CycloneDX Software Bill of Materials (SBOM) with Syft.
  - **Artifact Signing**: Verifies keyless container image signatures with Cosign.
  - **IaC Compliance**: Executes Checkov checks against CIS AWS Foundations benchmarks.
  - **Blocking Gate**: Halts deployment immediately (`DEPLOYMENT_BLOCKED`) if critical CVEs or secrets are detected.
* **Outputs**:
  - `security-report.json`
  - `sbom.json`
  - `cosign-attestation.json`

---

### 6. SREAgent
* **Role**: Site Reliability Engineering Lead
* **Input**: Running workload endpoints, SLA thresholds, and CloudWatch metrics
* **Responsibilities**:
  - Executes multi-stage k6 performance benchmarking: `baseline` (10% RPS), `load` (50% RPS), `stress` (100% RPS), and `spike` (150% RPS).
  - Aggregates latency percentiles (P50, P95, P99), HTTP error rates, and CPU/memory utilization.
  - Conducts structured Root Cause Analysis distinguishing **Observed Facts**, **Technical Inferences**, and **Safety-Gated Remediation Proposals**.
* **Outputs**:
  - `benchmark-report.json`
  - `sre-analysis.json`
  - `sre-analysis.md`
