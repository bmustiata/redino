from typing import List, Any, Optional, TypeVar, Dict, Type

from redino._redis_instance import redis_instance
from redino.redino_item import RedinoItem, class_name
from redino.data_converter import DataConverter, RedinoNative

T = TypeVar("T", bound="Entity")


class Entity(RedinoItem):
    """
    Entities are objects that can be persisted in Redis.

    They are backed by a HSET (HashSet) Redis object, and are
    identified by: `TYPE:id` key names. If they contain a list,
    set or dict, the backing property ID is: `TYPE:id:field_name`,
    and they return one of the `RedinoList`, `RedinoSet` or
    `RedinoDict` respectively.
    """

    def __init__(self, _id: Optional[str] = None) -> None:
        super(Entity, self).__init__(_id=_id)
        self._rd_cache: Dict[str, RedinoNative] = dict()

    def rd_persist(self: T) -> T:
        redis_instance().hset(class_name(self), self._rd_self_id, "1")
        return self

    def rd_delete(self) -> None:
        # FIXME: iterate over the `attr` and delete them, if the
        # items are being owned
        redis_instance().execute_command("hdel", class_name(self), self._rd_self_id)
        redis_instance().execute_command("del", self._rd_self_id)

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_rd_"):
            return super(Entity, self).__getattribute__(key)

        if key not in type(self).attr:  # type: ignore
            raise Exception(
                f"No attribute {key} in {self._rd_self_id}. "  # type: ignore
                f"Only {type(self).attr} are known."
            )

        if key in self._rd_cache:
            return self._rd_cache[key]

        definition = type(self).attr[key]  # type: ignore
        # FIXME: cache converters
        converter = DataConverter(_type=definition)
        data = converter.from_bytes(redis_instance().hget(self._rd_self_id, key))

        self._rd_cache[key] = data

        return data

    def __setattr__(self, key, value):
        if key.startswith("_rd_"):
            return super(Entity, self).__setattr__(key, value)

        if key not in type(self).attr:
            raise Exception(
                f"No attribute {key} in {self._rd_self_id}. "
                f"Only {type(self).attr} are known."
            )

        definition = type(self).attr[key]

        # FIXME: cache converters
        converter = DataConverter(_type=definition)

        # NOTE: deletion is not handled here since we cannot
        # guarantee usage from other objects.
        native = converter.from_data(value)

        redis_instance().hset(self._rd_self_id, key, converter.native_to_bytes(native))

        self._rd_cache[key] = native

    @staticmethod
    def fetch_all(t: Type[T]) -> List[T]:
        """
        Fetches all the instances of the given type.
        """
        # FIXME: return an iterator
        # this gives us the IDs
        items = redis_instance().hgetall(class_name(t))
        return [t(_id=id.decode("utf-8")) for id in items]

    @staticmethod
    def fetch_first(t: Type[T]) -> Optional[T]:
        """
        Fetches a single item of a given type.
        """
        for item in Entity.fetch_all(t):
            return item

        return None

    @staticmethod
    def attributes(t: Type[T], attr: Dict[str, Any]) -> None:
        t.attr = attr  # type: ignore
