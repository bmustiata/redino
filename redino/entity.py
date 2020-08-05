from typing import List, Any, Optional, TypeVar

import redis
import uuid
import inspect


def class_name(instance: Any) -> str:
    t = instance if inspect.isclass(instance) else type(instance)

    return f"{t.__module__}.{t.__name__}"


class Entity:
    """
    Entities are objects that can be persisted in Redis.

    They are backed by a HSET (HashSet) Redis object, and are
    identified by: `TYPE:id` key names. If they contain a list,
    set or dict, the backing property ID is: `TYPE:id:field_name`,
    and they return one of the `RedinoList`, `RedinoSet` or
    `RedinoDict` respectively.
    """
    def __init__(self,
                 redis: redis.client.Redis,
                 _id: Optional[str] = None) -> None:
        self._rd_redis = redis

        if _id is not None:
            self._rd_id = _id
        else:
            self._rd_id = str(uuid.uuid4())

    @property
    def _rd_self_id(self) -> str:
        return f"{class_name(self)}:{self._rd_id}"

    def persist(self) -> 'Entity':
        self._rd_redis.hset(class_name(self), self._rd_id, "1")
        return self

    def delete(self) -> None:
        # FIXME: iterate over the `attr` and delete them, if the
        # items are being owned
        self._rd_redis.hdel(class_name(self), self._rd_id)

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_rd_"):
            return super(Entity, self).__getattribute__(key)

        if key not in type(self).attr:
            raise Exception(f"No attribute {key} in {self._rd_self_id}. "
                            f"Only {type(self).attr} are known.")

        definition = type(self).attr[key]

        if definition is str:
            return self._rd_redis.hget(self._rd_self_id, key).decode("utf-8")
        elif definition is int:
            return int(self._rd_redis.hget(self._rd_self_id, key))

        raise Exception(f"Unable to fetch {key} from {self._rd_self_id} "
                        f"with definition {definition}")
    
    def __setattr__(self, key, value):
        if key.startswith("_rd_"):
            return super(Entity, self).__setattr__(key, value)

        if key not in type(self).attr:
            raise Exception(f"No attribute {key} in {self._rd_self_id}. "
                            f"Only {type(self).attr} are known.")

        definition = type(self).attr[key]

        if definition is str:
            self._rd_redis.hset(self._rd_self_id, key, str(value))
            return
        elif definition is int:
            self._rd_redis.hset(self._rd_self_id, key, int(value))
            return

        raise Exception(f"Unable to fetch {key} from {self._rd_self_id} "
                        f"with definition {definition}")

    @staticmethod
    def fetch_all(redis: redis.client.Redis,
                  type: 'T') -> List['T']:
        """
        Fetches all the instances of the given type
        """
        # this gives us the IDs
        items = redis.hgetall(class_name(type))
        return [type(redis=redis, _id=id.decode('utf-8')) for id in items]


T = TypeVar('T', bound=Entity)
