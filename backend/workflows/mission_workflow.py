"""
Temporal Mission Workflow Definition
Durable execution for the closed-loop DevOps and cloud engineering lifecycle
"""
from datetime import timedelta
from typing import Any, Dict
from contextlib import nullcontext

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
    _imports_ctx = workflow.unsafe.imports_passed_through()
except ImportError:
    class DummyWorkflow:
        @staticmethod
        def defn(cls=None):
            return cls if cls else lambda c: c
        @staticmethod
        def run(fn=None):
            return fn if fn else lambda f: f
    class RetryPolicy:
        def __init__(self, **kwargs):
            pass
    workflow = DummyWorkflow()
    _imports_ctx = nullcontext()

with _imports_ctx:
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


@workflow.defn
class MissionWorkflow:
    @workflow.run
    async def run(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the durable mission pipeline:
        Architect -> Database -> Application -> Infrastructure -> Security -> Deployment -> SRE -> Final Report
        """
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3,
            non_retryable_error_types=["RuntimeError"],
        )

        activity_options = {
            "start_to_close_timeout": timedelta(minutes=5),
            "retry_policy": retry_policy,
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
                "mission_id": input_dict["mission_id"],
                "mission_name": input_dict["mission_name"],
                "requirements": input_dict["requirements"],
                "context": context,
            }

            try:
                result = await workflow.execute_activity(
                    activity_fn,
                    activity_input,
                    **activity_options,
                )
                context[stage_name] = result
            except Exception as e:
                workflow.logger.error(f"Workflow stage {stage_name} failed: {str(e)}")
                raise

        return {
            "mission_id": input_dict["mission_id"],
            "status": "COMPLETED",
            "context": context,
        }
