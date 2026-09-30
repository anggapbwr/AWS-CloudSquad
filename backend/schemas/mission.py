"""
Pydantic Schemas & Canonical Enums for Missions, Events, and Artifacts
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class MissionStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    ARCHITECTURE_READY = "ARCHITECTURE_READY"
    DATABASE_READY = "DATABASE_READY"
    APPLICATION_READY = "APPLICATION_READY"
    INFRASTRUCTURE_READY = "INFRASTRUCTURE_READY"
    SECURITY_VALIDATING = "SECURITY_VALIDATING"
    SECURITY_PASSED = "SECURITY_PASSED"
    DEPLOYING = "DEPLOYING"
    DEPLOYED = "DEPLOYED"
    OBSERVING = "OBSERVING"
    BENCHMARKING = "BENCHMARKING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"


class AgentStage(str, Enum):
    ARCHITECT = "architect"
    DATABASE = "database"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    DEVSECOPS = "devsecops"
    DEPLOYMENT = "deployment"
    OBSERVABILITY = "observability"
    BENCHMARK = "benchmark"
    SRE = "sre"
    REPORT = "report"


class StageStatus(str, Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class EventType(str, Enum):
    MISSION_CREATED = "MISSION_CREATED"
    ARCHITECT_STARTED = "ARCHITECT_STARTED"
    ARCHITECT_COMPLETED = "ARCHITECT_COMPLETED"
    DATABASE_STARTED = "DATABASE_STARTED"
    DATABASE_COMPLETED = "DATABASE_COMPLETED"
    APPLICATION_STARTED = "APPLICATION_STARTED"
    APPLICATION_COMPLETED = "APPLICATION_COMPLETED"
    INFRASTRUCTURE_STARTED = "INFRASTRUCTURE_STARTED"
    INFRASTRUCTURE_VALIDATED = "INFRASTRUCTURE_VALIDATED"
    SECURITY_SCAN_STARTED = "SECURITY_SCAN_STARTED"
    SECURITY_SCAN_COMPLETED = "SECURITY_SCAN_COMPLETED"
    SECURITY_GATE_FAILED = "SECURITY_GATE_FAILED"
    DEPLOYMENT_STARTED = "DEPLOYMENT_STARTED"
    DEPLOYMENT_COMPLETED = "DEPLOYMENT_COMPLETED"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    OBSERVABILITY_STARTED = "OBSERVABILITY_STARTED"
    BENCHMARK_STARTED = "BENCHMARK_STARTED"
    BENCHMARK_COMPLETED = "BENCHMARK_COMPLETED"
    SRE_ANALYSIS_STARTED = "SRE_ANALYSIS_STARTED"
    SRE_ANALYSIS_COMPLETED = "SRE_ANALYSIS_COMPLETED"
    REMEDIATION_STARTED = "REMEDIATION_STARTED"
    REMEDIATION_COMPLETED = "REMEDIATION_COMPLETED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_FAILED = "MISSION_FAILED"
    STAGE_FAILED = "STAGE_FAILED"


class ArtifactType(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    DATABASE_SCHEMA = "DATABASE_SCHEMA"
    APPLICATION = "APPLICATION"
    TERRAFORM = "TERRAFORM"
    SECURITY_REPORT = "SECURITY_REPORT"
    SBOM = "SBOM"
    DEPLOYMENT = "DEPLOYMENT"
    BENCHMARK = "BENCHMARK"
    SRE_REPORT = "SRE_REPORT"


# --- Requirements Schemas ---
class MissionRequirementsBase(BaseModel):
    raw_input: str = Field(default="", description="Original user prompt or requirements text")
    target_rps: int = Field(default=1000, description="Target throughput in requests per second")
    availability_target: float = Field(default=0.9995, description="Target availability e.g. 0.9995 (99.95%)")
    monthly_budget_usd: float = Field(default=300.0, description="Monthly cost budget limit in USD")
    region: str = Field(default="ap-southeast-1", description="Target AWS region")
    database: str = Field(default="postgresql", description="Target database engine")
    deployment: str = Field(default="ecs_fargate", description="Target deployment model (ecs_fargate)")
    performance_testing: bool = Field(default=True, description="Whether to run k6 benchmark test suite")
    security_validation: bool = Field(default=True, description="Whether to run DevSecOps blocking security gates")


class MissionRequirementsCreate(MissionRequirementsBase):
    pass


class MissionRequirementsRead(MissionRequirementsBase):
    id: UUID
    mission_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Event Schemas ---
class MissionEventBase(BaseModel):
    event_type: EventType
    stage: Optional[AgentStage] = None
    status: str = "info"  # info, passed, failed, warning
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MissionEventCreate(MissionEventBase):
    mission_id: UUID


class MissionEventRead(BaseModel):
    id: UUID
    mission_id: UUID
    event_type: EventType
    stage: Optional[AgentStage] = None
    status: str = "info"
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Artifact Schemas ---
class ArtifactBase(BaseModel):
    agent: str
    type: ArtifactType
    name: str
    storage_location: str
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")


class ArtifactCreate(ArtifactBase):
    mission_id: UUID


class ArtifactRead(ArtifactBase):
    id: UUID
    mission_id: UUID
    created_at: datetime
    content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Mission Schemas ---
class MissionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=5)
    category: str = Field(default="High Concurrency Web Application")


class MissionCreate(MissionBase):
    requirements: Optional[MissionRequirementsBase] = None


class StageInfo(BaseModel):
    stage: AgentStage
    status: StageStatus = StageStatus.WAITING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    summary: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class MissionRead(MissionBase):
    id: UUID
    status: MissionStatus
    current_stage: Optional[AgentStage] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    requirements: Optional[MissionRequirementsRead] = None
    stages: Dict[str, StageInfo] = Field(default_factory=dict)
    architecture_spec: Optional[Dict[str, Any]] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    telemetry: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    current_stage: Optional[AgentStage] = None
    completed_at: Optional[datetime] = None
    architecture_spec: Optional[Dict[str, Any]] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    telemetry: Optional[Dict[str, Any]] = None
