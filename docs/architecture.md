# AWS CloudSquad — Architecture & Design Philosophy

> **Autonomous DevOps & Cloud Engineering Platform**  
> *"From Requirement to Running Infrastructure."*

---

## 1. Core Engineering Tenets

1. **Closed-Loop Automation Over Open-Loop Code Generation**  
   AWS CloudSquad is not a code-generator chatbot. It is a control plane that orchestrates planning, validation, deployment, observability, testing, and remediation into one unified loop.

2. **Deterministic Validation Over Stochastic Trust**  
   AI agents may propose architectures and code. Deterministic tools (`terraform fmt/validate`, Checkov, Semgrep, Trivy, Syft, k6) must validate those actions. No infrastructure is provisioned without passing deterministic policy gates.

3. **Durable Workflows Over Ephemeral Scripts**  
   Missions are represented as durable Temporal Workflows. Each stage is an isolated activity with explicit timeouts, exponential retries, artifact generation, and audit logging.

4. **Transparent Telemetry Over Fabricated Claims**  
   Target requirements (e.g. 1,000 RPS, 99.95% availability) are goals, not guarantees. Telemetry and SRE reports only present verified facts obtained from live benchmarks and observability metrics.

---

## 2. System Architecture

```text
                           ┌──────────────────┐
                           │   USER / DEV     │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │ NEXT.JS COCKPIT  │
                           └────────┬─────────┘
                                    │ HTTP / WebSocket
                                    ▼
                           ┌──────────────────┐
                           │   FASTAPI CORE   │
                           └────────┬─────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
        PostgreSQL 16            Redis 7         Temporal Orchestrator
      (System of Record)    (Pub/Sub Events)       (Workflow Engine)
                                                          │
                                                          ▼
                                                   Temporal Worker
                                                          │
                    ┌───────────────────┬─────────────────┴───────────────────┐
                    │                   │                                     │
                    ▼                   ▼                                     ▼
             Architect Agent     Database Agent                        DevOps Agents
                    │                   │                                     │
                    └───────────────────┴─────────────────┬───────────────────┘
                                                          │
                                                          ▼
                                                Validation Gates
                                                (terraform / checkov)
                                                          │
                                                          ▼
                                                   DevSecOps Agent
                                                (Semgrep / Trivy / Cosign)
                                                          │
                                                          ▼
                                                Deterministic Deployment
                                                (ECR / ECS Fargate / ALB)
                                                          │
                                                          ▼
                                                  Workload on AWS
                                                          │
                                                          ▼
                                                  Performance & SRE
                                                (k6 Benchmark / Alarms)
```

---

## 3. Technology Stack Reference
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, React Flow (@xyflow/react), Recharts, Zustand.
- **Backend API**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Asyncpg, Aiofiles, Structlog.
- **Workflow Engine**: Temporal Cluster & Python Temporal SDK.
- **Persistence**: PostgreSQL 16 (relational data), Redis 7 (real-time pub/sub), S3/LocalFS (artifacts).
- **IaC & Toolchain**: Terraform, Checkov, Trivy, Semgrep, Syft, Cosign, k6.
