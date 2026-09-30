"""
AWS CloudSquad — Real-Time Event Bus
Redis Pub/Sub backed event distribution with local in-memory fallback
"""
import asyncio
import json
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Set
from uuid import UUID
import structlog
from config import settings

log = structlog.get_logger()

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    aioredis = None
    HAS_REDIS = False


class RedisEventBus:
    def __init__(self):
        self._local_subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self._mission_subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self._redis_client: Optional[aioredis.Redis] = None
        self._pubsub_task: Optional[asyncio.Task] = None
        self._is_connected = False

    async def connect(self):
        """Connect to Redis if available"""
        if not HAS_REDIS:
            self._is_connected = False
            log.info("Redis library not present, using local EventBus")
            return
        try:
            self._redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
            )
            await self._redis_client.ping()
            self._is_connected = True
            log.info("EventBus connected to Redis Pub/Sub", redis_url=settings.REDIS_URL)

            # Start background listener for Redis Pub/Sub
            self._pubsub_task = asyncio.create_task(self._listen_redis())
        except Exception as e:
            self._is_connected = False
            log.warning("Redis Pub/Sub unavailable, using in-memory local EventBus", error=str(e))

    async def disconnect(self):
        if self._pubsub_task:
            self._pubsub_task.cancel()
        if self._redis_client:
            await self._redis_client.close()

    async def _listen_redis(self):
        """Listen to Redis broadcast channels and dispatch to local WebSocket handlers"""
        if not self._redis_client:
            return
        try:
            pubsub = self._redis_client.pubsub()
            await pubsub.psubscribe("mission:*:events")
            async for message in pubsub.listen():
                if message and message.get("type") == "pmessage":
                    try:
                        data = json.loads(message["data"])
                        mission_id = data.get("mission_id")
                        if mission_id:
                            await self._dispatch_local(str(mission_id), data)
                    except Exception as err:
                        log.error("Failed to parse Redis pubsub message", error=str(err))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error("Error in Redis pubsub listener", error=str(e))

    def subscribe_mission(self, mission_id: UUID, callback: Callable):
        self._mission_subscribers[str(mission_id)].add(callback)

    def unsubscribe_mission(self, mission_id: UUID, callback: Callable):
        self._mission_subscribers[str(mission_id)].discard(callback)

    async def _dispatch_local(self, mission_id_str: str, payload: dict):
        callbacks = list(self._mission_subscribers.get(mission_id_str, set()))
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(payload)
                else:
                    cb(payload)
            except Exception as e:
                log.debug("Error in event callback", error=str(e))

    async def publish(
        self,
        event_type: str,
        mission_id: UUID,
        message: str,
        stage: Optional[str] = None,
        status: str = "info",
        metadata: Optional[dict] = None,
    ):
        payload = {
            "event": event_type,
            "event_type": event_type,
            "mission_id": str(mission_id),
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "metadata": metadata or {},
        }

        # 1. Publish to Redis if connected
        if self._is_connected and self._redis_client:
            try:
                channel = f"mission:{mission_id}:events"
                await self._redis_client.publish(channel, json.dumps(payload, default=str))
            except Exception as e:
                log.warning("Failed to publish to Redis, falling back to local dispatch", error=str(e))
                await self._dispatch_local(str(mission_id), payload)
        else:
            # 2. Local fallback
            await self._dispatch_local(str(mission_id), payload)


event_bus = RedisEventBus()
