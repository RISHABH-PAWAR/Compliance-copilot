"""Redis Cache Manager"""
import json
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()


class CacheManager:
    """Redis-based cache for compliance data, sessions, and rate limiting"""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import redis
                self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._client = None
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if not self.client:
            return False
        try:
            self.client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception:
            return False

    async def increment(self, key: str, ttl: int = 60) -> int:
        if not self.client:
            return 0
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            result = pipe.execute()
            return result[0]
        except Exception:
            return 0


cache = CacheManager()
