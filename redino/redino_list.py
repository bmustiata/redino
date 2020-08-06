from typing import TypeVar, List

from redino._redis_instance import redis_instance

T = TypeVar("T")


class RedinoList:
    def __init__(self, _full_id: str) -> None:
        self._rd_full_id = _full_id

    def append(self, other: T):
        # FIXME: this should be some form of casting
        redis_instance().rpush(self._rd_full_id, other)

    def clear(self):
        redis_instance().lrem(self._rd_full_id, 999999, None)

    def copy(self):
        raise Exception("not implemented")

    def count(self):
        redis_instance().llen(self._rd_full_id)

