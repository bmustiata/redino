import redis.client

from typing import Callable, TypeVar, Optional
import functools
import logging

LOG = logging.getLogger(__name__)

T = TypeVar("T")
_redis_instance: Optional[redis.client.Redis] = None


def _redis_pool() -> redis.client.Redis:
    global _redis_instance

    if not _redis_instance:
        _redis_instance = redis.client.Redis()

    return _redis_instance


def transactional(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        r: redis.StrictRedis = args[0]

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


def redis_connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        with _redis_pool().client() as redis_client:  # type: ignore
            return f(redis_client, *args, **kw)

    return wrapper
