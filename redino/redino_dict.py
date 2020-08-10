from typing import TypeVar, Any, Optional, Dict

import redino.redino_item
import redino.data_converter
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
        pass

    def rd_delete(self) -> None:
        self.clear()

    def clear(self):
        redis_instance().execute_command("del", self._rd_self_id)

    @staticmethod  # known case
    def fromkeys(*args, **kwargs):  # real signature unknown
        """ Create a new dictionary with keys from iterable and values set to value. """
        pass

    def get(self, *args, **kwargs):
        pass

    def items(self):
        pass

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

    def update(self, E=None, **F):  # known special case of dict.update
        pass

    def values(self):  # real signature unknown; restored from __doc__
        pass

    def __contains__(self, *args, **kwargs):
        pass

    def __delitem__(self, *args, **kwargs):
        pass

    def __eq__(self, *args, **kwargs):  # real signature unknown
        pass

    def __getattribute__(self, *args, **kwargs):  # real signature unknown
        pass

    def __getitem__(self, y):  # real signature unknown; restored from __doc__
        pass

    def __iter__(self, *args, **kwargs):  # real signature unknown
        pass

    def __len__(self, *args, **kwargs):  # real signature unknown
        pass

    def __setitem__(self, *args, **kwargs):  # real signature unknown
        """ Set self[key] to value. """
        pass
