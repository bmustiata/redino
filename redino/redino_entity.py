import inspect
import uuid
from typing import List, Any, Optional, TypeVar

from redino._redis_instance import redis_instance


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
                 _id: Optional[str] = None) -> None:
        if _id is not None:
            self._rd_id = _id
        else:
            self._rd_id = str(uuid.uuid4())

        self._rd_cache = dict()

    @property
    def _rd_self_id(self) -> str:
        return f"{class_name(self)}:{self._rd_id}"

    def persist(self) -> 'Entity':
        redis_instance().hset(class_name(self), self._rd_id, "1")
        return self

    def delete(self) -> None:
        # FIXME: iterate over the `attr` and delete them, if the
        # items are being owned
        redis_instance().hdel(class_name(self), self._rd_id)

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_rd_"):
            return super(Entity, self).__getattribute__(key)

        if key not in type(self).attr:
            raise Exception(f"No attribute {key} in {self._rd_self_id}. "
                            f"Only {type(self).attr} are known.")

        if key in self._rd_cache:
            return self._rd_cache[key]

        definition = type(self).attr[key]

        if definition is str:
            result = redis_instance().hget(self._rd_self_id, key).decode("utf-8")
            self._rd_cache[key] = result
            return result
        elif definition is int:
            result = int(redis_instance().hget(self._rd_self_id, key))
            self._rd_cache[key] = result
            return result

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
            result = str(value)
            redis_instance().hset(self._rd_self_id, key, result)
            self._rd_cache[key] = result

            return
        elif definition is int:
            result = int(value)
            redis_instance().hset(self._rd_self_id, key, result)
            self._rd_cache[key] = result

            return

        raise Exception(f"Unable to set {key} from {self._rd_self_id} "
                        f"with definition {definition}.")

    @staticmethod
    def fetch_all(type: 'T') -> List['T']:
        """
        Fetches all the instances of the given type
        """
        # this gives us the IDs
        items = redis_instance().hgetall(class_name(type))
        return [type(_id=id.decode('utf-8')) for id in items]


T = TypeVar('T', bound=Entity)
