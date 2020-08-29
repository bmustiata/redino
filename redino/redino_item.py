import abc
import inspect
import uuid
from typing import Optional, Any, TypeVar

_S = TypeVar("_S")


def class_name(instance: Any) -> str:
    t = instance if inspect.isclass(instance) else type(instance)

    return f"{t.__name__}"


class RedinoItem(metaclass=abc.ABCMeta):
    """
    Marker class to have easier isinstance checks for the
    DataConverter.
    """

    def __init__(self, _id: Optional[str] = None) -> None:
        if _id is not None:
            self._rd_self_id = _id
        else:
            self._rd_self_id = f"{class_name(self)}:{str(uuid.uuid4())}"

    @abc.abstractmethod
    def rd_persist(self: _S) -> _S:
        pass

    @abc.abstractmethod
    def rd_delete(self: _S) -> None:
        pass
