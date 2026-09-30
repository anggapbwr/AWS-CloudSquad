# AWS CloudSquad — Canonical Final Architecture

> **Autonomous DevOps & Cloud Engineering Platform**  
> *"From Requirement to Running Infrastructure."*

---

## 1. System Overview & Philosophy

AWS CloudSquad is an autonomous DevOps and cloud engineering control plane that transforms application requirements into architecture, application artifacts, infrastructure, security validation, AWS deployment, observability, performance testing, and SRE analysis through a closed-loop, event-driven engineering workflow.

CloudSquad does **not** treat LLMs as unchecked code generators. Instead, it enforces:

$$\text{AI Reasoning} + \text{Deterministic Engineering Tools} + \text{Validation Gates} + \text{Durable Orchestration} \longrightarrow \text{Production AWS Infrastructure}$$

### Core Closed-Loop Lifecycle:
```text
PLAN ──► BUILD ──► VALIDATE ──► DEPLOY ──► OBSERVE ──► TEST ──► ANALYZE ──► REMEDIATE ──► (Loop)
```

---

## 2. High-Level Architecture Topology

```text
                         ┌────────────────────────────────────────┐
                         │               USER / DEV               │
                         └───────────────────┬────────────────────┘
                                             │
                                             ▼
                         ┌────────────────────────────────────────┐
                         │            NEXT.JS COCKPIT             │
                         │                                        │
                         │  Mission Dashboard   Agent Station     │
                         │  Architecture Canvas (React Flow)      │
                         │  Live Telemetry (Recharts)             │
                         │  Event Timeline      Artifact Inspector│
                         └───────────────────┬────────────────────┘
                                             │ HTTP REST / WebSocket
                                             ▼
                         ┌────────────────────────────────────────┐
                         │              FASTAPI CORE              │
                         │                                        │
                         │  Mission API         Policy Engine     │
                         │  Artifact Manager    Event Gateway     │
                         │  Temporal Client     AWS Integrations  │
                         └───────────────────┬────────────────────┘
                                             │
                   ┌─────────────────────────┴────────────────────────┐
                   │                                                  │
                   ▼                                                  ▼
     ┌───────────────────────────┐                      ┌───────────────────────────┐
     │      POSTGRESQL 16+       │                      │          REDIS 7          │
     │    (System of Record)     │                      │ (Pub/Sub & Real-time Bus) │
     └───────────────────────────┘                      └───────────────────────────┘
                   │                                                  ▲
                   │                                                  │
                   ▼                                                  │
     ┌───────────────────────────┐                      ┌─────────────┴─────────────┐
     │    TEMPORAL ORCHESTRATOR  │                      │         S3 STORAGE        │
     │ (Durable Workflow Engine) │                      │    (Artifact Repository)  │
     └─────────────┬─────────────┘                      └───────────────────────────┘
                   │
                   ▼
     ┌───────────────────────────┐
     │      TEMPORAL WORKER      │
     │  (Modular Monolith Worker)│
     └─────────────┬─────────────┘
                   │
  ┌────────────────┼─────────────────────────────────────────────┐
  │                │                                             │
  ▼                ▼                                             ▼
Architect Agent  Database Agent  Application Agent        Infrastructure Agent
  │                │                    │                        │
  └────────────────┴────────────────────┴────────────────────────┤
                                                                 ▼
                                                        Deterministic Validation Gates
                                                          - terraform fmt / validate / plan
                                                          - Checkov / Trivy config
                                                                 │
                                                                 ▼
                                                          DevSecOps Agent
                                                          (Semgrep, Gitleaks, Trivy, Syft, Cosign)
                                                                 │
                                                                 ▼
                                                        Deterministic Deployment Stage
                                                          - Docker Build & Push ECR
                                                          - Terraform Apply (ECS + ALB + RDS)
                                                          - Health Check Gate
                                                                 │
                                                                 ▼
                                                        Running Workload on AWS
                                                                 │
                                       ┌─────────────────────────┼─────────────────────────┐
                                       ▼                         ▼                         ▼
                                 Observability                Security                Performance
                                 (CloudWatch/OTel)       (WAF/SecurityGroup)         (k6 Benchmark)
                                       │                         │                         │
                                       └─────────────────────────┼─────────────────────────┘
                                                                 ▼
                                                             SRE Agent
                                                       (Analysis & Remediation)
```

---

## 3. Structural Model: Modular Monolith + Isolated Workers

CloudSquad maintains an operationally manageable footprint:
- **Cockpit Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS + React Flow + Recharts.
- **Control Plane API**: FastAPI with SQLAlchemy 2.0 (PostgreSQL) and Redis Pub/Sub event bus.
- **Workflow Engine**: Temporal Cluster with persistent workflow state, retry logic, timeouts, and compensation.
- **Engineering Worker**: Executes Temporal Activities that invoke LLM Gateway reasoning and deterministic CLI tools.
- **Persistence**: PostgreSQL 16 (metadata/runs/events), Redis 7 (real-time streaming/caching), S3/LocalFS (artifacts).

---

## 4. The 6 Engineering Agents & Deterministic Stages

Notice: **Deployment is a deterministic engineering stage, not an AI agent.** **Observability is part of the SRE lifecycle.**

| Role | Class | Category | Primary Responsibilities | Deterministic Tools & Outputs |
|---|---|---|---|---|
| **1. Architect** | `ArchitectAgent` | AI Reasoning | Requirements analysis, SLA/budget translation, topology selection, cost estimation | `architecture.json`, `architecture-diagram.json`, `cost-estimate.json`, `architecture-rationale.md` |
| **2. Database** | `DatabaseAgent` | AI + Deterministic | Relational & NoSQL schema design, entity relationships, index optimization, migrations | `schema.sql`, `migration.sql`, `database-config.json`, `database-design.md` |
| **3. Application** | `ApplicationAgent` | AI + Scaffolding | FastAPI application code, Dockerfile, unit tests, `/health` and `/ready` endpoints | Application codebase, `Dockerfile`, `test_api.py`, pytest execution |
| **4. Infrastructure** | `InfrastructureAgent` | AI + IaC Engine | Modular Terraform generation (VPC, ALB, ECS Fargate, RDS, S3, IAM, CloudWatch) | Modular Terraform (`modules/`, `environments/dev/`), `terraform fmt`, `terraform validate`, `terraform plan` |
| **5. DevSecOps** | `DevSecOpsAgent` | Deterministic Security Gate | Static analysis, secret scanning, container scanning, SBOM generation, IaC policy audit | Semgrep, Gitleaks, Trivy, Syft, Cosign, Checkov. Blocking policy gate (`DEPLOYMENT_BLOCKED`) |
| **Stage: Deployment** | `DeploymentService` | Deterministic Workflow Stage | Container build & tag, ECR push, Terraform plan review, Terraform apply, ECS rolling deployment, health probe | Docker CLI / Boto3 / Terraform CLI. Health check verification (`GET /health`) |
| **6. SRE** | `SREAgent` | Observability & Testing | k6 load & stress testing, CloudWatch telemetry aggregation, latency & bottleneck analysis, remediation proposals | k6 runner, `benchmark-report.json`, `sre-analysis.json`, `sre-analysis.md` |

---

## 5. Temporal Mission Workflow Lifecycle

The mission execution is orchestrated as a durable Temporal Workflow:

```text
MissionWorkflow
  ├── Step 1: ArchitectActivity (Requirements -> Architecture & Cost)
  ├── Step 2: DatabaseActivity (Architecture -> Schema & Migrations)
  ├── Step 3: ApplicationActivity (Schema -> App Code, Dockerfile, Tests)
  ├── Step 4: InfrastructureActivity (App & Arch -> Modular Terraform)
  ├── Step 5: ValidationGateActivity (terraform fmt, validate, plan, checkov)
  ├── Step 6: SecurityActivity (Semgrep, Gitleaks, Trivy, Syft SBOM, Cosign)
  ├── Step 7: DeploymentGateActivity (Policy check -> ECR push -> Terraform apply -> Health probe)
  ├── Step 8: ObservabilityActivity (CloudWatch & Metric Alarm setup)
  ├── Step 9: BenchmarkActivity (k6 Baseline -> Load -> Stress -> Spike)
  ├── Step 10: SREAnalysisActivity (Metrics analysis -> Bottleneck detection -> Remediation proposal)
  └── Step 11: FinalReportActivity (Synthesize final mission engineering report)
```

Each activity implements:
- Granular timeouts and exponential backoff retry policies.
- Real-time event publishing through the Redis Pub/Sub event bus.
- Structured artifact persistence to S3/Storage with database record tracking.
- Explicit failure classification (fatal vs retryable).

---

## 6. Canonical Mission State Machine

```text
CREATED 
  ──► PLANNING 
  ──► ARCHITECTURE_READY 
  ──► DATABASE_READY 
  ──► APPLICATION_READY 
  ──► INFRASTRUCTURE_READY 
  ──► SECURITY_VALIDATING 
  ──► SECURITY_PASSED (or SECURITY_BLOCKED ──► FAILED)
  ──► DEPLOYING 
  ──► DEPLOYED (or DEPLOYMENT_FAILED ──► RECOVERING)
  ──► OBSERVING 
  ──► BENCHMARKING 
  ──► ANALYZING 
  ──► COMPLETED (or FAILED)
```

---

## 7. Canonical Event Model

Every event emitted across HTTP/WebSocket/PubSub conforms to:

```json
{
  "id": "c1f7...-uuid",
  "mission_id": "4e2a...-uuid",
  "timestamp": "2026-09-29T16:30:00Z",
  "event_type": "SECURITY_SCAN_COMPLETED",
  "stage": "devsecops",
  "status": "passed",
  "message": "Security scan completed: 0 Critical CVEs, 0 secrets leaked, SBOM generated",
  "metadata": {
    "trivy_critical": 0,
    "gitleaks_findings": 0,
    "semgrep_rules": 142
  }
}
```

---

## 8. Real-Time Streaming Architecture

```text
Temporal Activity Execution
            │
            ▼
    Event Bus Publisher
            │
            ▼
     Redis Pub/Sub Channel ("mission:{mission_id}:events")
            │
            ▼
   FastAPI WebSocket Hub (/ws/{mission_id})
            │
            ▼
Next.js React Client (Zustand store -> UI Canvas / Timeline / Telemetry)
```

---

## 9. Safety & Execution Modes

CloudSquad enforces multi-layer safety controls:
1. `DEPLOYMENT_MODE=dry-run` (Default for local development & PR checks; validates plans, builds test containers, simulates cloud calls with strict realistic schemas).
2. `DEPLOYMENT_MODE=apply` (Active cloud mode requiring AWS credentials, performing real Terraform apply and real ECS deployments).
3. **Hard Security Gates**: Deployment halts immediately if Critical CVEs, leaked API credentials, or root container execution are detected.
4. **Human-in-the-loop Remediation**: SRE proposals are never automatically executed on production clusters without approval.
