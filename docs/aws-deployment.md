# AWS CloudSquad — AWS Deployment & Target Architecture

This document describes the AWS target architecture and the deterministic deployment stage.

---

## 1. Target AWS Architecture (ECS Fargate + ALB + RDS)

```text
                                  Internet
                                     │
                                     ▼
                        [Amazon CloudFront + AWS WAF]
                                     │
                                     ▼
                    [Application Load Balancer (ALB)]
                        (Public Subnets 10.0.101/102.0/24)
                                     │
               ┌─────────────────────┴─────────────────────┐
               │                                           │
               ▼                                           ▼
      [ECS Fargate Task A]                        [ECS Fargate Task B]
  (Private Subnet 10.0.1.0/24)                (Private Subnet 10.0.2.0/24)
               │                                           │
               └─────────────────────┬─────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
         [RDS PostgreSQL 16]   [ElastiCache Redis]   [Amazon S3]
             (Multi-AZ)          (Cluster Mode)     (Encrypted)
```

---

## 2. Deterministic Deployment Pipeline

Deployment is **not** an AI agent. It is an automated pipeline executed during the `deployment_activity`:

```text
1. Application Code Packaging
      ↓
2. Container Image Build (Python 3.12-slim non-root UID 10001)
      ↓
3. Security Gate Verification (0 Critical CVEs, 0 Leaked Secrets)
      ↓
4. Image Push to Amazon ECR
      ↓
5. Terraform Plan Validation
      ↓
6. Terraform Apply (VPC, ALB, ECS, RDS, IAM, S3, CloudWatch)
      ↓
7. ECS Rolling Task Deployment (Zero-Downtime)
      ↓
8. ALB Target Health Check Probe (GET /health -> 200 OK)
      ↓
9. Deployment Marked Complete
```

---

## 3. Modes of Operation

### Dry-Run Mode (`DEPLOYMENT_MODE=dry-run`)
- Default for local development and CI/CD testing.
- Validates Terraform syntax and generates execution plans.
- Emulates container builds and outputs realistic infrastructure manifests without requiring active AWS accounts or incur costs.

### Live AWS Mode (`DEPLOYMENT_MODE=apply`)
- Requires valid AWS credentials (configured via AWS IAM Role, AWS Profile, or environment variables).
- Executes live Terraform provisioning and pushes container images to AWS ECR.
- Targets the configured AWS Region (default: `ap-southeast-1`).
