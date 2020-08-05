from typing import List, Any, Optional

import redis
import uuid


class Entity:
    def __init__(self,
                 redis: redis.client.Redis,
                 _id: Optional[str] = None) -> None:
        self._rd_redis = redis

        if _id:
            self._rd_id = _id
        else:
            self._rd_id = str(uuid.uuid4())
            redis.hset("item", self._rd_id, "1")

    def delete(self):
        self._rd_redis.hdel("item", self._rd_id)
        
    def __getattr__(self, key: str) -> Any:
        if key.startswith("_rd_"):
            return super(Entity, self).__getattribute__(key)

        return self._rd_redis.hget(f"item:{self._rd_id}", key).decode("utf-8")
    
    def __setattr__(self, key, value):
        if key.startswith("_rd_"):
            return super(Entity, self).__setattr__(key, value)

        self._rd_redis.hset(f"item:{self._rd_id}", key, value)

    @staticmethod
    def fetch_all(redis: redis.client.Redis,
                  type: Any) -> List['Entity']:
        """
        Fetches all the instances of the given type
        """
        # this gives us the IDs
        items = redis.hgetall("item")
        return [type(redis=redis, _id=id.decode('utf-8')) for id in items]
