"""
Artifact Storage Manager — S3 & Local Filesystem Object Storage
"""
import os
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
import structlog
from config import settings

log = structlog.get_logger()


class ArtifactStorageManager:
    def __init__(self):
        self.local_base_dir = Path(settings.ARTIFACTS_LOCAL_DIR)
        self.local_base_dir.mkdir(parents=True, exist_ok=True)
        self.s3_bucket = settings.S3_BUCKET
        self._s3_client = None

    def _get_s3_client(self):
        if self._s3_client is None:
            try:
                import boto3
                self._s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
            except Exception as e:
                log.warning("AWS S3 client init failed, local storage will be primary", error=str(e))
        return self._s3_client

    async def save_artifact(
        self,
        mission_id: str,
        filename: str,
        content: str | bytes,
        content_type: str = "text/plain",
    ) -> str:
        """
        Saves artifact locally and optionally mirrors to S3 if configured.
        Returns the canonical storage location URI.
        """
        mission_dir = self.local_base_dir / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)
        file_path = mission_dir / filename

        # 1. Write to local storage
        if isinstance(content, str):
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)
        else:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

        storage_uri = f"local://{file_path.as_posix()}"

        # 2. Upload to S3 if live AWS mode enabled and not in demo dry-run
        if settings.DEPLOYMENT_MODE == "apply" and not settings.DEMO_MODE:
            try:
                s3 = self._get_s3_client()
                if s3:
                    s3_key = f"missions/{mission_id}/{filename}"
                    body = content.encode("utf-8") if isinstance(content, str) else content
                    s3.put_object(
                        Bucket=self.s3_bucket,
                        Key=s3_key,
                        Body=body,
                        ContentType=content_type,
                    )
                    storage_uri = f"s3://{self.s3_bucket}/{s3_key}"
            except Exception as e:
                log.warning("Failed to upload artifact to S3, using local", error=str(e))

        return storage_uri

    async def read_artifact(self, storage_location: str) -> Optional[str]:
        """Reads artifact content from storage URI"""
        if storage_location.startswith("local://"):
            local_path = storage_location.replace("local://", "")
            if os.path.exists(local_path):
                async with aiofiles.open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    return await f.read()
        elif storage_location.startswith("s3://"):
            try:
                s3 = self._get_s3_client()
                if s3:
                    parts = storage_location.replace("s3://", "").split("/", 1)
                    bucket, key = parts[0], parts[1]
                    resp = s3.get_object(Bucket=bucket, Key=key)
                    return resp["Body"].read().decode("utf-8")
            except Exception as e:
                log.error("Failed to read artifact from S3", error=str(e))
        elif os.path.exists(storage_location):
            async with aiofiles.open(storage_location, "r", encoding="utf-8", errors="ignore") as f:
                return await f.read()

        return None


artifact_storage = ArtifactStorageManager()
