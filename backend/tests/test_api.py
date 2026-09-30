"""
API End-to-End Tests for AWS CloudSquad
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "AWS CloudSquad"
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_mission_lifecycle_crud(client: AsyncClient):
    # 1. Create Mission
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
    mission = create_resp.json()
    mission_id = mission["id"]
    assert mission["name"] == payload["name"]
    assert mission["status"] == "CREATED"
    assert "architect" in mission["stages"]

    # 2. List Missions
    list_resp = await client.get("/api/missions")
    assert list_resp.status_code == 200
    missions = list_resp.json()
    assert len(missions) >= 1
    assert any(m["id"] == mission_id for m in missions)

    # 3. Get Mission Detail
    get_resp = await client.get(f"/api/missions/{mission_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == mission_id

    # 4. Get Mission Events
    events_resp = await client.get(f"/api/missions/{mission_id}/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) >= 1
    assert events[0]["event_type"] == "MISSION_CREATED"

    # 5. Delete Mission
    del_resp = await client.delete(f"/api/missions/{mission_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"

    # Verify not found after deletion
    get_del_resp = await client.get(f"/api/missions/{mission_id}")
    assert get_del_resp.status_code == 404
