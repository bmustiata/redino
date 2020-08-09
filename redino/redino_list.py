from typing import TypeVar, Iterable, Any, Optional

from redino._redis_instance import redis_instance
from redino.data_converter import DataConverter
from redino.redino_item import RedinoItem

_T = TypeVar("_T")
_S = TypeVar("_S")


class RedinoList(RedinoItem):
    def __init__(self,
                 _type: Any,
                 _id: Optional[str] = None) -> None:
        super(RedinoList, self).__init__(_id=_id)

        # FIXME: use a converter cache for the types
        self._rd_converter = DataConverter(_type=_type.__args__[0])

    def persist(self: _S) -> _S:
        pass  # there's nothing to persist when created

    def delete(self) -> None:
        self.clear()

    def __contains__(self, item: object) -> bool:
        return self.index(item) >= 0

    def __len__(self) -> int:
        return redis_instance().execute_command("llen", self._rd_self_id)

    def __setitem__(self, index: int, data: _T) -> None:
        redis_instance().execute_command(
            "lset",
            self._rd_self_id,
            index,
            self._rd_converter.data_to_bytes(data)
        )

    def __getitem__(self, index: int) -> _T:
        data = redis_instance().execute_command(
            "lindex",
            self._rd_self_id,
            index)

        return self._rd_converter.from_bytes(data)

    def __delitem__(self, i: int) -> None:
        self[i] = "__remove_me"
        self.remove("__remove_me")

    def __iadd__(self: '', other: _T) -> _S:
        self.append(other)
        return self

    def append(self, other: _T):
        redis_instance().execute_command(
            "rpush",
            self._rd_self_id,
            self._rd_converter.data_to_bytes(other)
        )

    def pop(self, i: int = ...) -> _T:
        data = redis_instance().execute_command("lpop", self._rd_self_id)
        return self._rd_converter.from_bytes(data)

    def remove(self, item: _T) -> None:
        item_bytes = self._rd_converter.data_to_bytes(item)
        redis_instance().execute_command(
            "lrem",
            self._rd_self_id,  # key
            1,  # count
            item_bytes  # element
        )

    def clear(self) -> None:
        redis_instance().execute_command("del", self._rd_self_id)

    def index(self, item: _T, *args: Any) -> int:
        return redis_instance().execute_command(
            "lpos",
            self._rd_self_id,
            self._rd_converter.data_to_bytes(item),
        )

    def extend(self, other: Iterable[_T]) -> None:
        for item in other:
            self.append(item)
