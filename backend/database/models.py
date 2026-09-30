"""
SQLAlchemy 2.0 Database Models for AWS CloudSquad
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base, TimestampMixin


class MissionModel(Base, TimestampMixin):
    __tablename__ = "missions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="High Concurrency Web Application")
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False)
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Dynamic JSON state tracking
    stages: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    architecture_spec: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    cost_estimate: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    telemetry: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    requirements: Mapped[Optional["MissionRequirementsModel"]] = relationship(
        "MissionRequirementsModel", back_populates="mission", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )
    events: Mapped[List["MissionEventModel"]] = relationship(
        "MissionEventModel", back_populates="mission", cascade="all, delete-orphan", order_by="MissionEventModel.timestamp"
    )
    artifacts: Mapped[List["ArtifactRecordModel"]] = relationship(
        "ArtifactRecordModel", back_populates="mission", cascade="all, delete-orphan"
    )
    workflow_runs: Mapped[List["WorkflowRunModel"]] = relationship(
        "WorkflowRunModel", back_populates="mission", cascade="all, delete-orphan"
    )
    deployments: Mapped[List["DeploymentRecordModel"]] = relationship(
        "DeploymentRecordModel", back_populates="mission", cascade="all, delete-orphan"
    )
    security_scans: Mapped[List["SecurityScanRecordModel"]] = relationship(
        "SecurityScanRecordModel", back_populates="mission", cascade="all, delete-orphan"
    )
    benchmarks: Mapped[List["BenchmarkRecordModel"]] = relationship(
        "BenchmarkRecordModel", back_populates="mission", cascade="all, delete-orphan"
    )


class MissionRequirementsModel(Base):
    __tablename__ = "mission_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    target_rps: Mapped[int] = mapped_column(Integer, default=1000)
    availability_target: Mapped[float] = mapped_column(Float, default=0.9995)
    monthly_budget_usd: Mapped[float] = mapped_column(Float, default=300.0)
    region: Mapped[str] = mapped_column(String(50), default="ap-southeast-1")
    database: Mapped[str] = mapped_column(String(50), default="postgresql")
    deployment: Mapped[str] = mapped_column(String(50), default="ecs_fargate")
    performance_testing: Mapped[bool] = mapped_column(Boolean, default=True)
    security_validation: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="requirements")


class MissionEventModel(Base):
    __tablename__ = "mission_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="events")


class ArtifactRecordModel(Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    storage_location: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="artifacts")


class WorkflowRunModel(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    temporal_workflow_id: Mapped[str] = mapped_column(String(200), nullable=False)
    temporal_run_id: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="workflow_runs")


class DeploymentRecordModel(Base):
    __tablename__ = "deployments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    target_environment: Mapped[str] = mapped_column(String(50), default="aws-dev")
    cluster_arn: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    service_arn: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="deployments")


class SecurityScanRecordModel(Base):
    __tablename__ = "security_scans"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tool: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="security_scans")


class BenchmarkRecordModel(Base):
    __tablename__ = "benchmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_rps: Mapped[int] = mapped_column(Integer, default=1000)
    actual_rps: Mapped[float] = mapped_column(Float, default=0.0)
    p50_ms: Mapped[float] = mapped_column(Float, default=0.0)
    p95_ms: Mapped[float] = mapped_column(Float, default=0.0)
    p99_ms: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    availability: Mapped[float] = mapped_column(Float, default=100.0)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mission: Mapped["MissionModel"] = relationship("MissionModel", back_populates="benchmarks")
