import functools
import logging
from enum import Enum
from typing import Callable, TypeVar, Optional

import redis.client

import redino.model
from redino._redis_instance import _redis_thread_instance, redis_instance

LOG = logging.getLogger(__name__)

T = TypeVar("T")
_redis_pool_instance: Optional[redis.client.Redis] = None


class Operation(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


def _redis_pool() -> redis.client.Redis:
    global _redis_pool_instance

    if not _redis_pool_instance:
        _redis_pool_instance = redis.client.Redis()

    return _redis_pool_instance


def watch(entity_class) -> Callable[..., Callable[..., T]]:
    def wrapper_builder(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args, **kw) -> T:
            return f(*args, **kw)

        return wrapper

    return wrapper_builder


def transactional(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        r = redis_instance()

        r.execute_command("MULTI")
        try:
            result = f(*args, **kw)
            r.execute_command("EXEC")

            return result
        except Exception as e:
            r.execute_command("DISCARD")
            LOG.error("DISCARD redis changes, due to {err}", err=str(e))
            raise e

    return wrapper


def connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        if (
            not redino.model.dbversion
            or redino.model.dbversion == redino.model.VERSION_UKNOWN
        ):
            raise Exception(
                "redino.model.setup(version, migrate) was not called, "
                "or model version is invalid. The version is the number that "
                "this application model defines, and the migrate() will receive "
                "the version stored in the datastore. If the code of migrate is "
                "successful, the datastore version is updated to the model "
                "version."
            )

        with _redis_pool().client() as redis_client:  # type: ignore
            try:
                _redis_thread_instance.instance = redis_client
                return f(*args, **kw)
            finally:
                _redis_thread_instance.instance = None

    return wrapper


from redino.redino_entity import Entity
from redino.redino_list import RedinoList
from redino.redino_dict import RedinoDict
from redino.redino_set import RedinoSet
