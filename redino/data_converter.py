import inspect
from typing import Any, Union

import redino.redino_entity
import redino.redino_entity
import redino.redino_item

RedisBytes = Union[bytes, int, str, None]
RedinoNative = Union[redino.redino_item.RedinoItem, bytes, int, str, None]


class DataConverter:
    def __init__(self, _type: Any) -> None:
        self._type = _type

    def from_data(self, data: Any) -> RedinoNative:
        if self._type is str and isinstance(data, str):
            return data

        if self._type is int and isinstance(data, int):
            return data

        if isinstance(data, redino.redino_entity.RedinoItem):
            return data

        if self._type.__origin__ is list and isinstance(data, list):
            list_result = redino.redino_list.RedinoList(_type=self._type)
            list_result.extend(data)

            return list_result

        if self._type.__origin__ is set and isinstance(data, set):
            set_result = redino.redino_set.RedinoSet(_type=self._type)
            set_result.update(data)

            return set_result

        if self._type.__origin__ is dict and isinstance(data, dict):
            dict_result = redino.redino_dict.RedinoDict(_type=self._type)
            dict_result.update(data)

            return dict_result

        raise Exception(f"Unsupported type: {self._type} for data {type(data)}")

    def from_bytes(self, data: bytes) -> RedinoNative:
        if data is None:
            return None

        if self._type is str:
            return data.decode("utf-8")

        if self._type is int:
            return int(data)

        if inspect.isclass(self._type) and issubclass(
            self._type, redino.redino_entity.Entity
        ):
            return self._type(_id=data.decode("utf-8"))

        if self._type.__origin__ is list:
            return redino.redino_list.RedinoList(
                _type=self._type, _id=data.decode("utf-8")
            )

        if self._type.__origin__ is set:
            return redino.redino_set.RedinoSet(
                _type=self._type, _id=data.decode("utf-8")
            )

        if self._type.__origin__ is dict:
            return redino.redino_dict.RedinoDict(
                _type=self._type, _id=data.decode("utf-8")
            )

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
