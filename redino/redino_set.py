from typing import Any, Optional, TypeVar

from redino import redis_instance
from redino._redis_scan import RedisIterable, RedisScan
from redino.data_converter import DataConverter, RedinoNative
from redino.redino_item import RedinoItem

_T = RedinoNative
_S = TypeVar("_S", bound="RedinoSet")


class RedinoSet(RedinoItem):
    def __init__(self, _type: Any, _id: Optional[str] = None) -> None:
        super(RedinoSet, self).__init__(_id=_id)

        # FIXME: use a converter cache for the types
        self._rd_converter = DataConverter(_type=_type.__args__[0])

    def rd_persist(self: _S) -> _S:
        return self

    def rd_delete(self: _S) -> None:
        self.clear()

    def add(self: _S, item: _T):
        redis_instance().execute_command(
            "sadd", self._rd_self_id, self._rd_converter.data_to_bytes(item)
        )

    def clear(self):
        redis_instance().execute_command("del", self._rd_self_id)

    def discard(self, item: _T):
        redis_instance().execute_command(
            "srem",
            self._rd_self_id,
            self._rd_converter.data_to_bytes(item),
        )

    def remove(self, item: _T):
        result = int(
            redis_instance().execute_command(
                "srem",
                self._rd_self_id,
                self._rd_converter.data_to_bytes(item),
            )
        )

        if not result:
            raise ValueError(f"No such item {str(item)} in set.")

    def update(self, other_set):
        for item in other_set:
            self.add(item)

    def __contains__(self, item) -> bool:
        return redis_instance().execute_command(
            "sismember",
            self._rd_self_id,
            self._rd_converter.data_to_bytes(item),
        )

    def __iter__(self, *args, **kwargs):  # real signature unknown
        """ Implement iter(self). """
        return RedisIterable(self, RedisSetIterator).__iter__()

    def __len__(self):  # real signature unknown
        return int(
            redis_instance().execute_command(
                "scard",
                self._rd_self_id,
            )
        )

    def __iadd__(self: _S, other: _T) -> _S:
        self.add(other)
        return self


class RedisSetIterator:
    def __init__(self, s: RedinoSet) -> None:
        self._scan = RedisScan(s, "sscan")
        self._s = s

    def __next__(self) -> _T:
        return self._s._rd_converter.from_bytes(self._scan.__next__())
