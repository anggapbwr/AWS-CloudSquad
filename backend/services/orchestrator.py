"""
Mission Orchestrator Gateway
Dispatches workflows to Temporal cluster or direct durable activity runner
"""
import asyncio
import uuid
from typing import Dict, Any, Optional
import structlog

try:
    from temporalio.client import Client
    HAS_TEMPORAL = True
except ImportError:
    Client = None
    HAS_TEMPORAL = False

from config import settings
import database.session as db_session_module
from services.mission_service import MissionService
from schemas.mission import MissionStatus
from workflows.mission_workflow import MissionWorkflow
from workflows.activities import (
    architect_activity,
    database_activity,
    application_activity,
    infrastructure_activity,
    security_activity,
    deployment_activity,
    sre_activity,
    final_report_activity,
)

log = structlog.get_logger()


async def _run_direct_pipeline(mission_id: uuid.UUID):
    """
    Fallback activity runner if Temporal service is not currently reachable.
    Executes the exact same activities in order, ensuring 100% testability.
    """
    async with db_session_module.async_session_factory() as db:
        mission = await MissionService.get_mission(db, mission_id)
        if not mission:
            return
        mission_name = mission.name
        reqs = {
            "target_rps": mission.requirements.target_rps if mission.requirements else 1000,
            "availability_target": mission.requirements.availability_target if mission.requirements else 0.9995,
            "monthly_budget_usd": mission.requirements.monthly_budget_usd if mission.requirements else 300.0,
            "region": mission.requirements.region if mission.requirements else "ap-southeast-1",
            "database": mission.requirements.database if mission.requirements else "postgresql",
            "deployment": mission.requirements.deployment if mission.requirements else "ecs_fargate",
        }

    context: Dict[str, Any] = {}
    stages = [
        ("architect", architect_activity),
        ("database", database_activity),
        ("application", application_activity),
        ("infrastructure", infrastructure_activity),
        ("devsecops", security_activity),
        ("deployment", deployment_activity),
        ("sre", sre_activity),
        ("final_report", final_report_activity),
    ]

    for stage_name, activity_fn in stages:
        activity_input = {
            "mission_id": str(mission_id),
            "mission_name": mission_name,
            "requirements": reqs,
            "context": context,
        }
        try:
            result = await activity_fn(activity_input)
            context[stage_name] = result
            # Short realistic breathing interval for cockpit animation
            await asyncio.sleep(1.0)
        except Exception as e:
            log.error(f"Direct pipeline stage {stage_name} failed", error=str(e))
            async with db_session_module.async_session_factory() as db:
                await MissionService.update_mission_status(db, mission_id, MissionStatus.FAILED)
            return

    log.info("Direct pipeline finished successfully", mission_id=str(mission_id))


async def launch_mission_workflow(mission_id: uuid.UUID) -> Dict[str, Any]:
    """
    Launches mission execution via Temporal or fallback runner.
    """
    async with db_session_module.async_session_factory() as db:
        mission = await MissionService.get_mission(db, mission_id)
        if not mission:
            raise ValueError(f"Mission {mission_id} not found")
        await MissionService.update_mission_status(db, mission_id, MissionStatus.PLANNING)

    temporal_client = None
    if HAS_TEMPORAL and Client:
        try:
            temporal_client = await asyncio.wait_for(
                Client.connect(settings.TEMPORAL_HOST, namespace=settings.TEMPORAL_NAMESPACE),
                timeout=2.0,
            )
        except Exception as e:
            log.info("Temporal unavailable, using direct activity pipeline runner", error=str(e))

    if temporal_client:
        workflow_id = f"mission-{mission_id}"
        handle = await temporal_client.start_workflow(
            MissionWorkflow.run,
            {
                "mission_id": str(mission_id),
                "mission_name": mission.name,
                "requirements": {
                    "target_rps": mission.requirements.target_rps if mission.requirements else 1000,
                    "availability_target": mission.requirements.availability_target if mission.requirements else 0.9995,
                    "monthly_budget_usd": mission.requirements.monthly_budget_usd if mission.requirements else 300.0,
                    "region": mission.requirements.region if mission.requirements else "ap-southeast-1",
                },
            },
            id=workflow_id,
            task_queue=settings.TEMPORAL_TASK_QUEUE,
        )
        log.info("Temporal workflow started", workflow_id=workflow_id, run_id=handle.run_id)
        return {"status": "started", "workflow_id": workflow_id, "run_id": handle.run_id}
    else:
        # Run background direct pipeline
        asyncio.create_task(_run_direct_pipeline(mission_id))
        return {"status": "started", "mode": "direct_activity_runner"}
