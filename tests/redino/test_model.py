import unittest

import redis
from redino import transactional, redis_connect


class TestRedisReadWrite(unittest.TestCase):
    """
    Test the model if it can create entries in redis
    """
    def test_regular_writing(self):
        @redis_connect
        @transactional
        def set_values(r: redis.Redis):
            r.hset("a", "key", "3")
            r.hset("b", "key", "3")

        @redis_connect
        def read_values(r: redis.Redis):
            self.assertEqual("3", r.hget("a", "key").decode("utf-8"))
            self.assertEqual("3", r.hget("b", "key").decode("utf-8"))

        set_values()
        read_values()

    def test_exception_rolls_back(self):
        @redis_connect
        @transactional
        def set_values(r: redis.Redis):
            r.hset("ROLL", "key", "3")
            raise Exception("ded")

        @redis_connect
        def read_values(r: redis.Redis):
            self.assertIsNone(r.hget("ROLL", "key"))

        try:
            set_values()
        except Exception:
            pass

        read_values()


if __name__ == "__main__":
    unittest.main()
