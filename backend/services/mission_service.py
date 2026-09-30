"""
Mission Service — Database Operations & Mission Lifecycle Management
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from database.models import (
    MissionModel,
    MissionRequirementsModel,
    MissionEventModel,
    ArtifactRecordModel,
)
from schemas.mission import (
    MissionCreate,
    MissionRequirementsBase,
    MissionStatus,
    AgentStage,
    StageStatus,
    EventType,
    ArtifactType,
)


class MissionService:
    @staticmethod
    async def create_mission(db: AsyncSession, payload: MissionCreate) -> MissionModel:
        initial_stages = {
            stage.value: {
                "stage": stage.value,
                "status": StageStatus.WAITING.value,
                "started_at": None,
                "completed_at": None,
                "duration_seconds": None,
                "summary": None,
                "artifacts": [],
                "error": None,
            }
            for stage in [
                AgentStage.ARCHITECT,
                AgentStage.DATABASE,
                AgentStage.APPLICATION,
                AgentStage.INFRASTRUCTURE,
                AgentStage.DEVSECOPS,
                AgentStage.DEPLOYMENT,
                AgentStage.OBSERVABILITY,
                AgentStage.BENCHMARK,
                AgentStage.SRE,
                AgentStage.REPORT,
            ]
        }

        mission = MissionModel(
            name=payload.name,
            description=payload.description,
            category=payload.category,
            status=MissionStatus.CREATED.value,
            stages=initial_stages,
        )
        db.add(mission)
        await db.flush()

        reqs_data = payload.requirements or MissionRequirementsBase(raw_input=payload.description)
        requirements = MissionRequirementsModel(
            mission_id=mission.id,
            raw_input=reqs_data.raw_input,
            target_rps=reqs_data.target_rps,
            availability_target=reqs_data.availability_target,
            monthly_budget_usd=reqs_data.monthly_budget_usd,
            region=reqs_data.region,
            database=reqs_data.database,
            deployment=reqs_data.deployment,
            performance_testing=reqs_data.performance_testing,
            security_validation=reqs_data.security_validation,
        )
        db.add(requirements)

        # Initial event
        event = MissionEventModel(
            mission_id=mission.id,
            event_type=EventType.MISSION_CREATED.value,
            status="info",
            message=f"Mission '{mission.name}' initialized in system.",
            metadata_json={"target_rps": reqs_data.target_rps, "budget": reqs_data.monthly_budget_usd},
        )
        db.add(event)
        await db.commit()
        await db.refresh(mission)
        return mission

    @staticmethod
    async def get_mission(db: AsyncSession, mission_id: uuid.UUID) -> Optional[MissionModel]:
        stmt = (
            select(MissionModel)
            .where(MissionModel.id == mission_id)
            .options(selectinload(MissionModel.requirements))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_missions(db: AsyncSession) -> List[MissionModel]:
        stmt = select(MissionModel).order_by(MissionModel.created_at.desc()).options(selectinload(MissionModel.requirements))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_mission_stage_status(
        db: AsyncSession,
        mission_id: uuid.UUID,
        stage: AgentStage,
        status: StageStatus,
        summary: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        error: Optional[str] = None,
    ) -> Optional[MissionModel]:
        mission = await MissionService.get_mission(db, mission_id)
        if not mission:
            return None

        stages = dict(mission.stages or {})
        stage_key = stage.value
        stage_info = stages.get(stage_key, {"stage": stage_key})

        stage_info["status"] = status.value
        if status == StageStatus.RUNNING and not stage_info.get("started_at"):
            stage_info["started_at"] = datetime.utcnow().isoformat()
            mission.current_stage = stage_key
        elif status in (StageStatus.COMPLETED, StageStatus.FAILED):
            stage_info["completed_at"] = datetime.utcnow().isoformat()
            if stage_info.get("started_at"):
                try:
                    start_dt = datetime.fromisoformat(stage_info["started_at"])
                    stage_info["duration_seconds"] = round((datetime.utcnow() - start_dt).total_seconds(), 2)
                except Exception:
                    pass

        if summary:
            stage_info["summary"] = summary
        if artifacts:
            existing_artifacts = stage_info.get("artifacts", [])
            stage_info["artifacts"] = list(set(existing_artifacts + artifacts))
        if error:
            stage_info["error"] = error

        stages[stage_key] = stage_info
        mission.stages = dict(stages)
        flag_modified(mission, "stages")
        await db.commit()
        await db.refresh(mission)
        return mission

    @staticmethod
    async def update_mission_status(
        db: AsyncSession,
        mission_id: uuid.UUID,
        status: MissionStatus,
        current_stage: Optional[AgentStage] = None,
    ) -> Optional[MissionModel]:
        mission = await MissionService.get_mission(db, mission_id)
        if not mission:
            return None

        mission.status = status.value
        if current_stage:
            mission.current_stage = current_stage.value
        if status in (MissionStatus.COMPLETED, MissionStatus.FAILED):
            mission.completed_at = datetime.utcnow()
            mission.current_stage = None

        await db.commit()
        await db.refresh(mission)
        return mission

    @staticmethod
    async def record_event(
        db: AsyncSession,
        mission_id: uuid.UUID,
        event_type: EventType,
        message: str,
        stage: Optional[AgentStage] = None,
        status: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MissionEventModel:
        event = MissionEventModel(
            mission_id=mission_id,
            event_type=event_type.value,
            stage=stage.value if stage else None,
            status=status,
            message=message,
            metadata_json=metadata or {},
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_events(db: AsyncSession, mission_id: uuid.UUID) -> List[MissionEventModel]:
        stmt = (
            select(MissionEventModel)
            .where(MissionEventModel.mission_id == mission_id)
            .order_by(MissionEventModel.timestamp.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def record_artifact(
        db: AsyncSession,
        mission_id: uuid.UUID,
        agent: str,
        artifact_type: ArtifactType,
        name: str,
        storage_location: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArtifactRecordModel:
        artifact = ArtifactRecordModel(
            mission_id=mission_id,
            agent=agent,
            type=artifact_type.value,
            name=name,
            storage_location=storage_location,
            metadata_json=metadata or {},
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        return artifact

    @staticmethod
    async def get_artifacts(db: AsyncSession, mission_id: uuid.UUID) -> List[ArtifactRecordModel]:
        stmt = (
            select(ArtifactRecordModel)
            .where(ArtifactRecordModel.mission_id == mission_id)
            .order_by(ArtifactRecordModel.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_mission(db: AsyncSession, mission_id: uuid.UUID) -> bool:
        stmt = delete(MissionModel).where(MissionModel.id == mission_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
