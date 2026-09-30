"""
Artifacts API Router
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from schemas.mission import ArtifactRead
from services.mission_service import MissionService
from services.artifacts.storage import artifact_storage

router = APIRouter()


@router.get("/{mission_id}", response_model=List[ArtifactRead])
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
