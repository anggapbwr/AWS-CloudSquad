"""
Integration Test for Mission Workflow Execution (End-to-End Pipeline)
"""
import uuid
import pytest
from httpx import AsyncClient
from database.session import async_session_factory
from services.mission_service import MissionService
from services.orchestrator import _run_direct_pipeline


@pytest.mark.asyncio
async def test_full_mission_workflow_pipeline(client: AsyncClient, db_session):
    # 1. Create a mission
    payload = {
        "name": "E-Commerce Flash Sale Platform",
        "description": "High concurrency flash sale platform with PostgreSQL and ECS Fargate",
        "category": "High Concurrency Web Application",
        "requirements": {
            "raw_input": "Build e-commerce flash sale API",
            "target_rps": 1000,
            "availability_target": 0.9995,
            "monthly_budget_usd": 300.0,
            "region": "ap-southeast-1",
            "database": "postgresql",
            "deployment": "ecs_fargate",
            "performance_testing": True,
            "security_validation": True,
        },
    }

    create_resp = await client.post("/api/missions", json=payload)
    assert create_resp.status_code == 201
    mission_data = create_resp.json()
    mid = uuid.UUID(mission_data["id"])

    # 2. Run direct pipeline through all stages
    await _run_direct_pipeline(mid)

    # 3. Check final mission state
    async with async_session_factory() as db:
        final_mission = await MissionService.get_mission(db, mid)
        assert final_mission.status == "COMPLETED"
        assert final_mission.stages["architect"]["status"] == "COMPLETED"
        assert final_mission.stages["database"]["status"] == "COMPLETED"
        assert final_mission.stages["application"]["status"] == "COMPLETED"
        assert final_mission.stages["infrastructure"]["status"] == "COMPLETED"
        assert final_mission.stages["devsecops"]["status"] == "COMPLETED"
        assert final_mission.stages["deployment"]["status"] == "COMPLETED"
        assert final_mission.stages["sre"]["status"] == "COMPLETED"
        assert final_mission.stages["report"]["status"] == "COMPLETED"

        # Check events
        events = await MissionService.get_events(db, mid)
        event_types = [e.event_type for e in events]
        assert "MISSION_CREATED" in event_types
        assert "ARCHITECT_COMPLETED" in event_types
        assert "DATABASE_COMPLETED" in event_types
        assert "SECURITY_SCAN_COMPLETED" in event_types
        assert "DEPLOYMENT_COMPLETED" in event_types
        assert "BENCHMARK_COMPLETED" in event_types
        assert "MISSION_COMPLETED" in event_types

        # Check artifacts
        artifacts = await MissionService.get_artifacts(db, mid)
        artifact_names = [a.name for a in artifacts]
        assert "architecture.json" in artifact_names
        assert "schema.sql" in artifact_names
        assert "main.tf" in artifact_names
        assert "security-report.json" in artifact_names
        assert "benchmark-report.json" in artifact_names
        assert "mission-report.json" in artifact_names
