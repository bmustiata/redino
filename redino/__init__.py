import functools
import logging
from enum import Enum
from typing import Callable, TypeVar, Optional

import redis.client

from redino.entity import Entity

LOG = logging.getLogger(__name__)

T = TypeVar("T")
_redis_instance: Optional[redis.client.Redis] = None


class Operation(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


def _redis_pool() -> redis.client.Redis:
    global _redis_instance

    if not _redis_instance:
        _redis_instance = redis.client.Redis()

    return _redis_instance


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
        r: redis.client.Redis = args[0]

        r.execute_command("MULTI")
        try:
            result = f(*args, **kw)
            r.execute_command("EXEC")

            return result
        except Exception as e:
            r.execute_command("DISCARD")
            LOG.error("DISCARD redis changes, due to {err}",
                      err=str(e))
            raise e

    return wrapper


def connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        with _redis_pool().client() as redis_client:  # type: ignore
            return f(redis_client, *args, **kw)

    return wrapper
