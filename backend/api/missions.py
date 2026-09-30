"""
Mission API Endpoints
Comprehensive REST endpoints for mission creation, execution, status, and reporting
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from schemas.mission import (
    MissionCreate,
    MissionRead,
    MissionStatus,
    MissionEventRead,
    ArtifactRead,
)
from services.mission_service import MissionService
from services.orchestrator import launch_mission_workflow
from services.artifacts.storage import artifact_storage

router = APIRouter()


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
async def create_mission(
    payload: MissionCreate,
    db: AsyncSession = Depends(get_db),
):
    mission = await MissionService.create_mission(db, payload)
    return mission


@router.get("", response_model=List[MissionRead])
async def list_missions(db: AsyncSession = Depends(get_db)):
    missions = await MissionService.list_missions(db)
    return missions


@router.get("/{mission_id}", response_model=MissionRead)
async def get_mission(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    mission = await MissionService.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    return mission


@router.post("/{mission_id}/run")
async def run_mission(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    mission = await MissionService.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

    result = await launch_mission_workflow(mission_id)
    return result


@router.post("/{mission_id}/cancel")
async def cancel_mission(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    mission = await MissionService.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

    await MissionService.update_mission_status(db, mission_id, MissionStatus.FAILED)
    return {"status": "cancelled", "mission_id": str(mission_id)}


@router.get("/{mission_id}/events", response_model=List[MissionEventRead])
async def get_mission_events(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    events = await MissionService.get_events(db, mission_id)
    return events


@router.get("/{mission_id}/artifacts", response_model=List[ArtifactRead])
async def get_mission_artifacts(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    artifacts = await MissionService.get_artifacts(db, mission_id)
    result = []
    for art in artifacts:
        content = await artifact_storage.read_artifact(art.storage_location)
        result.append(
            ArtifactRead(
                id=art.id,
                mission_id=art.mission_id,
                agent=art.agent,
                type=art.type,
                name=art.name,
                storage_location=art.storage_location,
                metadata=art.metadata_json or {},
                created_at=art.created_at,
                content=content,
            )
        )
    return result


@router.get("/{mission_id}/deployment")
async def get_mission_deployment(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    content = await artifact_storage.read_artifact(f"local://generated-output/{mission_id}/deployment-manifest.json")
    if not content:
        raise HTTPException(status_code=404, detail="Deployment record not yet available")
    import json
    return json.loads(content)


@router.get("/{mission_id}/security")
async def get_mission_security(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    content = await artifact_storage.read_artifact(f"local://generated-output/{mission_id}/security-report.json")
    if not content:
        raise HTTPException(status_code=404, detail="Security report not yet available")
    import json
    return json.loads(content)


@router.get("/{mission_id}/benchmark")
async def get_mission_benchmark(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    content = await artifact_storage.read_artifact(f"local://generated-output/{mission_id}/benchmark-report.json")
    if not content:
        raise HTTPException(status_code=404, detail="Benchmark report not yet available")
    import json
    return json.loads(content)


@router.get("/{mission_id}/report")
async def get_mission_report(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    json_content = await artifact_storage.read_artifact(f"local://generated-output/{mission_id}/mission-report.json")
    md_content = await artifact_storage.read_artifact(f"local://generated-output/{mission_id}/mission-report.md")
    if not json_content and not md_content:
        raise HTTPException(status_code=404, detail="Final report not yet generated")
    import json
    return {
        "report_json": json.loads(json_content) if json_content else None,
        "report_markdown": md_content,
    }


@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await MissionService.delete_mission(db, mission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    return {"status": "deleted", "mission_id": str(mission_id)}
