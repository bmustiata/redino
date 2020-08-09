import inspect
from typing import Any, Union

import redino.redino_entity
import redino.redino_entity
import redino.redino_item

RedisBytes = Union[bytes, int, str]
RedinoNative = Union[redino.redino_item.RedinoItem, bytes, int, str]


class DataConverter:
    def __init__(self,
                 _type: Any) -> None:
        self._type = _type

    def from_data(self, data: Any) -> RedinoNative:
        if self._type is str:
            return data

        if self._type is int:
            return data

        if isinstance(data, redino.redino_entity.RedinoItem):
            return data

        if self._type.__origin__ is list and isinstance(data, list):
            result = redino.redino_list.RedinoList(_type=self._type)
            result.extend(data)

            return result

        raise Exception(f"Unsupported type: {self._type} for data {type(data)}")

    def from_bytes(self, data: bytes) -> RedinoNative:
        if self._type is str:
            return data.decode('utf-8')

        if self._type is int:
            return int(data)

        if inspect.isclass(self._type) and issubclass(self._type, redino.redino_entity.Entity):
            return self._type(_id=data.decode("utf-8"))

        if self._type.__origin__ is list:
            return redino.redino_list.RedinoList(
                _type=self._type,
                _id=data.decode("utf-8"))

        raise Exception("Unsupported type: " % self._type)

    def data_to_bytes(self, data: Any) -> RedisBytes:
        item = self.from_data(data)

        if isinstance(item, redino.redino_item.RedinoItem):
            return item._rd_self_id

        return item

    def native_to_bytes(self, native: RedinoNative) -> RedisBytes:
        if isinstance(native, redino.redino_item.RedinoItem):
            return native._rd_self_id

        return native
