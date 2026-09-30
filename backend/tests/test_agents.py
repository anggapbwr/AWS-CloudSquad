"""
Unit Tests for All 6 Agents and the Deterministic Deployment Service
"""
import uuid
import pytest
from agents.architect import ArchitectAgent
from agents.database import DatabaseAgent
from agents.application import ApplicationAgent
from agents.infrastructure import InfrastructureAgent
from agents.devsecops import DevSecOpsAgent
from agents.sre import SREAgent
from services.deployment.service import DeploymentService


@pytest.fixture
def mission_context():
    mid = uuid.uuid4()
    reqs = {
        "target_rps": 1000,
        "availability_target": 0.9995,
        "monthly_budget_usd": 300.0,
        "region": "ap-southeast-1",
        "database": "postgresql",
        "deployment": "ecs_fargate",
    }
    return mid, reqs


@pytest.mark.asyncio
async def test_architect_agent(mission_context):
    mid, reqs = mission_context
    agent = ArchitectAgent(mid, "E-Commerce Flash Sale", reqs, {})
    result = await agent.run()

    assert "architecture.json" in result["artifacts"]
    assert "cost-estimate.json" in result["artifacts"]
    assert result["architecture_spec"]["components"]["compute"] == "ECS Fargate (Multi-AZ)"
    assert result["cost_estimate"]["total_monthly_usd"] <= 300.0
    assert len(result["diagram"]["nodes"]) > 0


@pytest.mark.asyncio
async def test_database_agent(mission_context):
    mid, reqs = mission_context
    arch_output = {
        "architecture_spec": {
            "components": {"database": "RDS PostgreSQL (Multi-AZ)"}
        }
    }
    agent = DatabaseAgent(mid, "E-Commerce Flash Sale", reqs, arch_output)
    result = await agent.run()

    assert "schema.sql" in result["artifacts"]
    assert "migration.sql" in result["artifacts"]
    assert "CREATE TABLE IF NOT EXISTS orders" in result["schema_sql"]
    assert result["database_config"]["engine"] == "RDS PostgreSQL (Multi-AZ)"


@pytest.mark.asyncio
async def test_application_agent(mission_context):
    mid, reqs = mission_context
    agent = ApplicationAgent(mid, "E-Commerce Flash Sale", reqs, {})
    result = await agent.run()

    assert "app_main.py" in result["artifacts"]
    assert "Dockerfile" in result["artifacts"]
    assert result["tests_passed"] >= 1
    assert "UID 10001" in result["container_user"]


@pytest.mark.asyncio
async def test_infrastructure_agent(mission_context):
    mid, reqs = mission_context
    agent = InfrastructureAgent(mid, "E-Commerce Flash Sale", reqs, {})
    result = await agent.run()

    assert "main.tf" in result["artifacts"]
    assert "modules_vpc.tf" in result["artifacts"]
    assert result["validation"]["terraform_fmt"].startswith("PASSED")
    assert result["validation"]["terraform_validate"].startswith("PASSED")


@pytest.mark.asyncio
async def test_devsecops_agent(mission_context):
    mid, reqs = mission_context
    agent = DevSecOpsAgent(mid, "E-Commerce Flash Sale", reqs, {})
    result = await agent.run()

    assert "security-report.json" in result["artifacts"]
    assert "sbom.json" in result["artifacts"]
    assert result["gate_status"] == "SECURITY_PASSED"
    assert result["report"]["trivy"]["vulnerabilities"]["CRITICAL"] == 0
    assert result["report"]["gitleaks"]["findings_count"] == 0


@pytest.mark.asyncio
async def test_deployment_service(mission_context):
    mid, reqs = mission_context
    result = await DeploymentService.execute_deployment(mid, region="ap-southeast-1")

    assert result["status"] == "DEPLOYED"
    assert "alb" in result["endpoint_url"]
    assert result["health_check_status"].startswith("HEALTHY")


@pytest.mark.asyncio
async def test_sre_agent(mission_context):
    mid, reqs = mission_context
    agent = SREAgent(mid, "E-Commerce Flash Sale", reqs, {})
    result = await agent.run()

    assert "benchmark-report.json" in result["artifacts"]
    assert "sre-analysis.json" in result["artifacts"]
    assert result["benchmark"]["sla_compliance"] == "COMPLIANT"
    assert len(result["analysis"]["observed_facts"]) > 0
    assert len(result["analysis"]["inferences"]) > 0
    assert len(result["analysis"]["remediation_proposals"]) > 0
