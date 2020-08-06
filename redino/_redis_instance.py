import redis
import threading

_redis_thread_instance = threading.local()


def redis_instance() -> redis.client.Redis:
    if not _redis_thread_instance.instance:
        raise Exception("This works only inside a @redino.connect function")

    return _redis_thread_instance.instance
