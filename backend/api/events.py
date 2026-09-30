"""
Events API Router
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from schemas.mission import MissionEventRead
from services.mission_service import MissionService

router = APIRouter()


@router.get("/{mission_id}", response_model=List[MissionEventRead])
async def get_mission_events(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    events = await MissionService.get_events(db, mission_id)
    return events
