import time
import json
from typing import Any, Optional

class CacheService:
    """
    Unified caching service that attempts to connect to Redis,
    falling back to an in-memory dictionary-based TTL cache if Redis is offline or unavailable.
    """
    def __init__(self):
        self.redis_client = None
        self.use_fallback = True
        self.memory_cache = {}  # Fallback: {key: (value, expire_timestamp)}

        # Attempt to import and initialize Redis connection
        try:
            import redis
            # We connect to localhost Redis by default, with a 1.0 second socket timeout
            self.redis_client = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1.0, decode_responses=True)
            # Test connectivity
            self.redis_client.ping()
            self.use_fallback = False
            print("[Cache Service] Connected successfully to Redis server.")
        except Exception as e:
            self.redis_client = None
            self.use_fallback = True
            print(f"[Cache Service] Redis unavailable ({e}). Initialized in-memory fallback cache.")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve key from cache. Returns decoded JSON value or string."""
        if not self.use_fallback and self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return val
                return None
            except Exception as e:
                print(f"[Cache Service] Redis get failed: {e}. Falling back to memory.")
                
        # In-memory fallback lookup
        if key in self.memory_cache:
            val, expire_at = self.memory_cache[key]
            if expire_at is None or expire_at > time.time():
                return val
            else:
                del self.memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Write key and value to cache with expiration TTL in seconds."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        
        if not self.use_fallback and self.redis_client:
            try:
                self.redis_client.set(key, serialized, ex=ttl_seconds)
                return True
            except Exception as e:
                print(f"[Cache Service] Redis set failed: {e}. Falling back to memory.")
                
        # In-memory fallback write
        expire_at = time.time() + ttl_seconds if ttl_seconds else None
        self.memory_cache[key] = (value, expire_at)
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.use_fallback and self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                print(f"[Cache Service] Redis delete failed: {e}.")
                
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        return False

# Instantiate service singleton
cache_service = CacheService()
