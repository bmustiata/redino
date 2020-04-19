import redis

from typing import Callable, TypeVar
import functools
import logging

LOG = logging.getLogger(__name__)

T = TypeVar('T')


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
        r = redis.StrictRedis()
        return f(r, *args, **kw)

    return wrapper
