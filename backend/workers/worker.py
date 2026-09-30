"""
Temporal Worker Process for AWS CloudSquad
Registers MissionWorkflow and all engineering activities
"""
import asyncio
import structlog
from temporalio.client import Client
from temporalio.worker import Worker

from config import settings
from database.session import init_db
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


async def run_worker():
    log.info("Initializing worker database tables...")
    try:
        await init_db()
    except Exception as e:
        log.warning("Database init from worker failed or already initialized", error=str(e))

    log.info("Connecting Temporal worker...", host=settings.TEMPORAL_HOST, queue=settings.TEMPORAL_TASK_QUEUE)
    while True:
        try:
            client = await Client.connect(
                settings.TEMPORAL_HOST,
                namespace=settings.TEMPORAL_NAMESPACE,
            )
            log.info("Connected to Temporal cluster successfully!")
            break
        except Exception as e:
            log.info("Waiting for Temporal server to become available...", error=str(e))
            await asyncio.sleep(3)

    worker = Worker(
        client,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
        workflows=[MissionWorkflow],
        activities=[
            architect_activity,
            database_activity,
            application_activity,
            infrastructure_activity,
            security_activity,
            deployment_activity,
            sre_activity,
            final_report_activity,
        ],
    )

    log.info("Temporal Worker started and polling for mission tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
