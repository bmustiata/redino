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

        tx = r.pipeline()
        try:
            result = f(*args, **kw)
            tx.execute()
            return result
        except Exception as e:
            tx.reset()
            LOG.error("DISCARD redis changes, due to {}", e)

    return wrapper


def redis_connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        r = redis.StrictRedis()
        return f(r, *args, **kw)

    return wrapper


def model(namespace: str = "") -> Callable[..., Callable[..., T]]:
    def wrapper_builder(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args, **kw) -> T:
            return f(*args, **kw)

        return wrapper

    return wrapper_builder

