from typing import Any

from redino import redis_instance
from redino.redino_item import RedinoItem


class RedisIterable:
    def __init__(self, d: RedinoItem, iterator_class: Any) -> None:
        self._d = d
        self._iterator_class = iterator_class

    def __iter__(self):
        return self._iterator_class(self._d)


class RedisScan:
    def __init__(self, d: RedinoItem, command: str) -> None:
        self._d = d
        self._current_index = -1
        self._command = command

        self._read_redis_cursor()

    def __next__(self) -> Any:
        try:
            return self._cursor.__next__()
        except StopIteration:
            self._read_redis_cursor()
            return self._cursor.__next__()

    def _read_redis_cursor(self):
        # if the next index is 0, the redis scan is complete
        if self._current_index == 0:
            raise StopIteration()

        # this is why we mark the first index as -1 to start the scan
        # so we don't confuse it with completion
        if self._current_index == -1:
            self._current_index = 0

        redis_cursor = redis_instance().execute_command(
            self._command,
            self._d._rd_self_id,
            self._current_index,
        )

        self._current_index = redis_cursor[0]

        if hasattr(redis_cursor[1], "items"):
            self._cursor = redis_cursor[1].items().__iter__()
        else:
            self._cursor = redis_cursor[1].__iter__()
