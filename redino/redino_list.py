from typing import TypeVar, Iterable, Any, Optional, Iterator

from redino._redis_instance import redis_instance
from redino.data_converter import DataConverter, RedinoNative
from redino.redino_item import RedinoItem

_T = RedinoNative


class RedinoList(RedinoItem):
    """
    This behaves a lot like a linked list deque, so using indexed
    access it's a terrible idea. Has blocking support for fetching
    items.
    """

    def __init__(self, _type: Any, _id: Optional[str] = None) -> None:
        super(RedinoList, self).__init__(_id=_id)

        # FIXME: use a converter cache for the types
        self._rd_converter = DataConverter(_type=_type.__args__[0])

    def rd_persist(self: "RedinoList") -> "RedinoList":
        # there's nothing to persist when created
        return self

    def rd_delete(self) -> None:
        self.clear()

    def __contains__(self, item: _T) -> bool:
        return self.index(item) >= 0

    def __len__(self) -> int:
        result = redis_instance().execute_command("llen", self._rd_self_id)
        return int(result)

    def __setitem__(self, index: int, data: _T) -> None:
        redis_instance().execute_command(
            "lset", self._rd_self_id, index, self._rd_converter.data_to_bytes(data)
        )

    def __getitem__(self: "RedinoList", index: int) -> _T:
        data = redis_instance().execute_command("lindex", self._rd_self_id, index)

        return self._rd_converter.from_bytes(data)

    def __delitem__(self, i: int) -> None:
        self[i] = "__remove_me"
        self.remove("__remove_me")

    def __iadd__(self: "RedinoList", other: _T) -> "RedinoList":
        self.append(other)
        return self

    def __iter__(self) -> Iterable[_T]:
        return ListIterator(self)

    def append(self, other: _T):
        redis_instance().execute_command(
            "rpush", self._rd_self_id, self._rd_converter.data_to_bytes(other)
        )

    def pop(self) -> _T:
        data = redis_instance().execute_command("lpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def left_push(self: "RedinoList", item: _T) -> None:
        data = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command("lpush", self._rd_self_id, data)

    def right_push(self: "RedinoList", item: _T) -> None:
        data = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command("rpush", self._rd_self_id, data)

    def left_pop(self: "RedinoList") -> _T:
        data = redis_instance().execute_command("lpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def right_pop(self: "RedinoList") -> _T:
        data = redis_instance().execute_command("rpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def blocking_left_push(self: "RedinoList", item: _T) -> None:
        data = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command("blpush", self._rd_self_id, data)

    def blocking_right_push(self: "RedinoList", item: _T) -> None:
        data = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command("brpush", self._rd_self_id, data)

    def blocking_left_pop(self: "RedinoList") -> _T:
        data = redis_instance().execute_command("blpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def blocking_right_pop(self: "RedinoList") -> _T:
        data = redis_instance().execute_command("brpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def remove(self, item: _T) -> None:
        item_bytes = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command(
            "lrem", self._rd_self_id, 1, item_bytes  # key  # count  # element
        )

    def clear(self) -> None:
        redis_instance().execute_command("del", self._rd_self_id)

    def index(self, item: _T, *args: Any) -> int:
        result = redis_instance().execute_command(
            "lpos",
            self._rd_self_id,
            self._rd_converter.data_to_bytes(item),
        )

        if result is None:
            return -1

        return result

    def extend(self, other: Iterable[_T]) -> None:
        for item in other:
            self.append(item)


class ListIterator(Iterator[_T]):
    def __init__(self, l: RedinoList) -> None:
        self._list = l
        self._len = len(l)
        self._index = 0

    def __next__(self) -> _T:
        if self._index < self._len:
            result = self._list[self._index]
            self._index += 1

            return result

        raise StopIteration
