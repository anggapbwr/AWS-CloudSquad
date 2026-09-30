"""
Agent 1: ArchitectAgent
Analyzes requirements, selects AWS architecture topology, produces React Flow diagram, cost estimate, and rationale.
"""
import json
from typing import Any, Dict
from agents.base import BaseAgent
from schemas.mission import ArtifactType


class ArchitectAgent(BaseAgent):
    async def run(self) -> Dict[str, Any]:
        reqs = self.requirements
        target_rps = reqs.get("target_rps", 1000)
        budget = reqs.get("monthly_budget_usd", 300.0)
        availability = reqs.get("availability_target", 0.9995)
        region = reqs.get("region", "ap-southeast-1")

        # 1. Deterministic architecture decisions & AWS service selections
        is_high_rps = target_rps >= 5000
        service_selection = {
            "compute": "ECS Fargate (Multi-AZ)",
            "compute_type": "ecs_fargate",
            "load_balancer": "Application Load Balancer (ALB)",
            "database": "Aurora PostgreSQL Serverless v2" if is_high_rps else "RDS PostgreSQL (Multi-AZ)",
            "cache": "ElastiCache Redis Cluster",
            "storage": "Amazon S3 (Encrypted, Intelligent Tiering)",
            "cdn": "Amazon CloudFront + AWS WAF",
            "dns": "Amazon Route 53",
            "queue": "Amazon SQS FIFO",
            "monitoring": "Amazon CloudWatch & Container Insights",
            "secrets": "AWS Secrets Manager",
            "availability_zones": 2,
            "region": region,
        }

        # 2. Detailed AWS monthly cost breakdown
        compute_cost = 45.0 if not is_high_rps else 85.0
        db_cost = 65.0 if not is_high_rps else 110.0
        cache_cost = 32.0
        alb_cost = 22.0
        cdn_cost = 15.0
        storage_cost = 6.0
        monitoring_cost = 12.0
        total_monthly_usd = compute_cost + db_cost + cache_cost + alb_cost + cdn_cost + storage_cost + monitoring_cost

        cost_estimate = {
            "monthly_budget_usd": budget,
            "total_monthly_usd": round(total_monthly_usd, 2),
            "budget_status": "WITHIN_BUDGET" if total_monthly_usd <= budget else "EXCEEDS_BUDGET",
            "currency": "USD",
            "breakdown": {
                "compute_ecs_fargate": compute_cost,
                "database_rds_postgresql": db_cost,
                "cache_elasticache_redis": cache_cost,
                "networking_alb": alb_cost,
                "edge_cloudfront_waf": cdn_cost,
                "storage_s3": storage_cost,
                "monitoring_cloudwatch": monitoring_cost,
            },
        }

        # 3. Canonical Architecture Specification
        architecture_spec = {
            "workload_name": self.mission_name,
            "pattern": "Highly Available Microservice Architecture",
            "target_rps": target_rps,
            "availability_target": f"{availability * 100:.2f}%",
            "components": service_selection,
            "resilience": {
                "multi_az": True,
                "min_replicas": 2,
                "max_replicas": 12 if is_high_rps else 6,
                "target_cpu_utilization": 70,
                "target_memory_utilization": 80,
                "health_check_grace_period_seconds": 60,
            },
            "security": {
                "ingress_protection": "CloudFront + AWS WAF Rate Limiting",
                "network_isolation": "Private subnets for ECS and RDS",
                "encryption_at_rest": "KMS Customer Managed Key",
                "encryption_in_transit": "TLS 1.3 enforced everywhere",
            },
        }

        # 4. Canonical React Flow Diagram Nodes & Edges
        nodes = [
            {
                "id": "node-users",
                "type": "custom",
                "position": {"x": 300, "y": 20},
                "data": {"label": "Internet Users", "service": "Internet", "type": "client", "status": "active"},
            },
            {
                "id": "node-cf",
                "type": "custom",
                "position": {"x": 300, "y": 120},
                "data": {"label": "CloudFront + WAF", "service": "CloudFront", "type": "edge", "status": "active", "cost": f"${cdn_cost}/mo"},
            },
            {
                "id": "node-alb",
                "type": "custom",
                "position": {"x": 300, "y": 220},
                "data": {"label": "Application Load Balancer", "service": "ALB", "type": "lb", "status": "active", "cost": f"${alb_cost}/mo"},
            },
            {
                "id": "node-ecs",
                "type": "custom",
                "position": {"x": 300, "y": 340},
                "data": {"label": "ECS Fargate (FastAPI)", "service": "ECS", "type": "compute", "status": "active", "cost": f"${compute_cost}/mo"},
            },
            {
                "id": "node-redis",
                "type": "custom",
                "position": {"x": 100, "y": 460},
                "data": {"label": "ElastiCache Redis", "service": "ElastiCache", "type": "cache", "status": "active", "cost": f"${cache_cost}/mo"},
            },
            {
                "id": "node-rds",
                "type": "custom",
                "position": {"x": 300, "y": 460},
                "data": {"label": "RDS PostgreSQL", "service": "RDS", "type": "database", "status": "active", "cost": f"${db_cost}/mo"},
            },
            {
                "id": "node-s3",
                "type": "custom",
                "position": {"x": 500, "y": 460},
                "data": {"label": "Amazon S3 Bucket", "service": "S3", "type": "storage", "status": "active", "cost": f"${storage_cost}/mo"},
            },
        ]

        edges = [
            {"id": "e-users-cf", "source": "node-users", "target": "node-cf", "animated": True},
            {"id": "e-cf-alb", "source": "node-cf", "target": "node-alb", "animated": True},
            {"id": "e-alb-ecs", "source": "node-alb", "target": "node-ecs", "animated": True},
            {"id": "e-ecs-redis", "source": "node-ecs", "target": "node-redis"},
            {"id": "e-ecs-rds", "source": "node-ecs", "target": "node-rds"},
            {"id": "e-ecs-s3", "source": "node-ecs", "target": "node-s3"},
        ]

        diagram = {"nodes": nodes, "edges": edges}

        # 5. Architecture Rationale Markdown
        rationale_md = f"""# Architecture Design Document: {self.mission_name}

## 1. Executive Summary
Designed a multi-AZ, highly available cloud architecture targeting **{target_rps:,} RPS** with a monthly budget limit of **${budget:,.2f}**.
Projected monthly infrastructure cost is **${total_monthly_usd:,.2f}**, which is **{cost_estimate['budget_status'].replace('_', ' ')}**.

## 2. Selected AWS Services
- **Compute**: {service_selection['compute']} in private application subnets. Fargate was chosen to eliminate EC2 OS maintenance overhead while supporting instant task scaling.
- **Traffic Routing**: Application Load Balancer with SSL termination, HTTP/2, and health checks pointing to `/health`.
- **Database**: {service_selection['database']} deployed with automated multi-AZ failover and encrypted EBS volumes.
- **Caching**: {service_selection['cache']} for session management, fast read caching, and distributed idempotency locking.
- **Edge Security**: CloudFront CDN with AWS WAF rate-limiting rules (100 req/min per IP) to mitigate DDoS attacks.
- **Object Storage**: Amazon S3 with SSE-S3 AES-256 encryption and Intelligent Tiering.

## 3. SLA & Resiliency
- Availability Target: **{availability * 100:.2f}%**
- Multi-AZ redundancy across 2 Availability Zones (`{region}a`, `{region}b`).
- Autoscaling policy: Step scaling between 2 and {architecture_spec['resilience']['max_replicas']} tasks based on target CPU utilization (70%).
"""

        # 6. Save artifacts
        mission_id_str = str(self.mission_id)
        await self.storage.save_artifact(mission_id_str, "architecture.json", json.dumps(architecture_spec, indent=2), "application/json")
        await self.storage.save_artifact(mission_id_str, "architecture-diagram.json", json.dumps(diagram, indent=2), "application/json")
        await self.storage.save_artifact(mission_id_str, "service-selection.json", json.dumps(service_selection, indent=2), "application/json")
        await self.storage.save_artifact(mission_id_str, "cost-estimate.json", json.dumps(cost_estimate, indent=2), "application/json")
        await self.storage.save_artifact(mission_id_str, "architecture-rationale.md", rationale_md, "text/markdown")

        return {
            "summary": f"Designed Multi-AZ architecture for {target_rps:,} RPS. Total estimated cost: ${total_monthly_usd:,.2f}/mo (Budget: ${budget:,.2f}).",
            "artifacts": [
                "architecture.json",
                "architecture-diagram.json",
                "service-selection.json",
                "cost-estimate.json",
                "architecture-rationale.md",
            ],
            "architecture_spec": architecture_spec,
            "cost_estimate": cost_estimate,
            "diagram": diagram,
        }
