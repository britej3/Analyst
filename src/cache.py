import os
import redis
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

class Cache:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def get_json(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set_json(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

