from typing import TypeVar, Any, Optional, Dict, Tuple, Iterable

import redino.data_converter
import redino.redino_item
from redino import redis_instance

_S = TypeVar("_S")
_K = TypeVar("_K")
_V = TypeVar("_V")


class RedinoDict(redino.redino_item.RedinoItem):
    def __init__(self: _S,
                 _type: Any,
                 _id: Optional[str] = None) -> None:
        super(RedinoDict, self).__init__(_id=_id)

        # FIXME: use a converter cache for the types
        self._rd_converter_key = redino.data_converter.DataConverter(_type=_type.__args__[0])
        self._rd_converter_value = redino.data_converter.DataConverter(_type=_type.__args__[1])

    def rd_persist(self: _S) -> _S:
        return self

    def rd_delete(self) -> None:
        self.clear()

    def clear(self):
        redis_instance().execute_command("del", self._rd_self_id)

    def get(self, key: _K) -> _V:
        data = redis_instance().execute_command(
            "hget",
            self._rd_self_id,
            self._rd_converter_key.data_to_bytes(key),
        )

        return self._rd_converter_value.from_bytes(data)

    def items(self) -> Iterable[Tuple[_K, _V]]:
        return RedisDictItems(self)

    def keys(self):
        pass

    def pop(self, k, d=None):  # real signature unknown; restored from __doc__
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        pass

    def popitem(self):  # real signature unknown; restored from __doc__
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if D is empty.
        """
        pass

    def setdefault(self, *args, **kwargs):  # real signature unknown
        pass

    def update(self, m: Dict[_K, _V]):
        for k, v in m.items():
            self[k] = v

    def values(self):
        pass

    def __contains__(self, *args, **kwargs):
        pass

    def __delitem__(self, key: _K):
        redis_instance().execute_command(
            "hdel",
            self._rd_self_id,
            self._rd_converter_key.data_to_bytes(key),
        )

    def __getitem__(self, key: _K) -> Optional[_V]:
        data = redis_instance().execute_command(
            "hget",
            self._rd_self_id,
            self._rd_converter_key.data_to_bytes(key),
        )

        return self._rd_converter_value.from_bytes(data)

    def __iter__(self):
        return self.keys()

    def __len__(self) -> int:
        return int(redis_instance().execute_command(
            "hget",
            self._rd_self_id,
        ))

    def __setitem__(self, key: _K, value: _V):
        redis_instance().execute_command(
            "hset",
            self._rd_self_id,
            self._rd_converter_key.data_to_bytes(key),
            self._rd_converter_value.data_to_bytes(value),
        )


def convert_data(d: RedinoDict,
                 data: Tuple[Any, Any]) -> Tuple[_K, _V]:
    return (
        d._rd_converter_key.from_bytes(data[0]),
        d._rd_converter_value.from_bytes(data[1]),
    )


class RedisDictItems:
    def __init__(self,
                 d: RedinoDict) -> None:
        self._d = d

    def __iter__(self):
        return RedisIterator(self._d)


class RedisIterator:
    def __init__(self,
                 d: RedinoDict) -> None:
        self._d = d
        self._current_index = -1

        self._read_redis_cursor()

    def __next__(self) -> Tuple[_K, _V]:
        try:
            return convert_data(self._d, self._cursor.__next__())
        except StopIteration:
            self._read_redis_cursor()
            return convert_data(self._d, self._cursor.__next__())

    def _read_redis_cursor(self):
        # if the next index is 0, the redis scan is complete
        if self._current_index == 0:
            raise StopIteration()

        # this is why we mark the first index as -1 to start the scan
        # so we don't confuse it with completion
        if self._current_index == -1:
            self._current_index = 0

        redis_cursor = redis_instance().hscan(
            self._d._rd_self_id,
            self._current_index,
        )

        self._current_index = redis_cursor[0]
        self._cursor = redis_cursor[1].items().__iter__()
