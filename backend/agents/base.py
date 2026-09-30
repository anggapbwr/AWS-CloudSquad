"""
Base Agent Class for AWS CloudSquad
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID
import structlog
from services.artifacts.storage import artifact_storage
from services.llm.gateway import llm_gateway

log = structlog.get_logger()


class BaseAgent(ABC):
    def __init__(self, mission_id: UUID, mission_name: str, requirements: Dict[str, Any], context: Dict[str, Any]):
        self.mission_id = mission_id
        self.mission_name = mission_name
        self.requirements = requirements
        self.context = context
        self.llm = llm_gateway
        self.storage = artifact_storage

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Executes the agent's responsibilities and returns structured outputs"""
        pass
