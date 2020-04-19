import redis

from typing import Callable, TypeVar, Optional
import functools
import logging

LOG = logging.getLogger(__name__)

T = TypeVar('T')
_redis_instance: Optional[redis.StrictRedis] = None


def _redis_pool() -> redis.StrictRedis:
    global _redis_instance

    if not _redis_instance:
        _redis_instance = redis.StrictRedis()

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
            LOG.error("DISCARD redis changes, due to {}", str(e))

    return wrapper


def redis_connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        with _redis_pool().client() as redis_client:
            return f(redis_client, *args, **kw)

    return wrapper
