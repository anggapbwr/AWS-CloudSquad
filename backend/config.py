"""
AWS CloudSquad — Central Configuration
Pydantic Settings for Environment Configuration
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Server
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database (PostgreSQL)
    POSTGRES_USER: str = Field(default="cloudsquad")
    POSTGRES_PASSWORD: str = Field(default="cloudsquad123")
    POSTGRES_DB: str = Field(default="cloudsquad_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cloudsquad:cloudsquad123@localhost:5432/cloudsquad_db"
    )

    # Cache & Event Bus (Redis)
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Workflow Orchestrator (Temporal)
    TEMPORAL_HOST: str = Field(default="localhost:7233")
    TEMPORAL_NAMESPACE: str = Field(default="default")
    TEMPORAL_TASK_QUEUE: str = Field(default="cloudsquad-mission-queue")

    # AWS
    AWS_REGION: str = Field(default="ap-southeast-1")
    AWS_PROFILE: str = Field(default="default")
    S3_BUCKET: str = Field(default="cloudsquad-mission-artifacts")

    # Execution Modes
    # dry-run (safe simulation/plan) | apply (live AWS provisioning)
    DEPLOYMENT_MODE: str = Field(default="dry-run")
    # DEMO_MODE: provides simulated execution if credentials or cloud services are absent
    DEMO_MODE: bool = Field(default=True)

    # AI Gateway
    # bedrock | openai | anthropic | deterministic
    LLM_PROVIDER: str = Field(default="deterministic")
    MODEL_ID: str = Field(default="claude-3-5-sonnet-20241022")
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")

    # Artifact Storage Directory
    ARTIFACTS_LOCAL_DIR: str = Field(default="./generated-output")


settings = Settings()
