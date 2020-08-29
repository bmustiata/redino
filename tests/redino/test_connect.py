import unittest

import redino
from redino import redis_instance
from tests.redino.test_shared import prepare_test


class TestRedisReadWrite(unittest.TestCase):
    """
    Test the model if it can create entries in redis
    """

    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    def test_regular_writing(self):
        @redino.connect
        @redino.transactional
        def set_values():
            r = redino.redis_instance()

            r.hset("a", "key", "3")
            r.hset("b", "key", "3")

        @redino.connect
        def read_values():
            r = redino.redis_instance()

            self.assertEqual("3", r.hget("a", "key").decode("utf-8"))
            self.assertEqual("3", r.hget("b", "key").decode("utf-8"))

        @redino.connect
        def clean_values():
            redis_instance().execute_command("del", "a")
            redis_instance().execute_command("del", "b")

        try:
            set_values()
            read_values()
        finally:
            clean_values()

    def test_exception_rolls_back(self):
        @redino.connect
        @redino.transactional
        def set_values():
            r = redino.redis_instance()

            r.hset("ROLL", "key", "3")
            raise Exception("ded")

        @redino.connect
        def read_values():
            r = redino.redis_instance()

            self.assertIsNone(r.hget("ROLL", "key"))

        try:
            set_values()
        except Exception:
            pass

        read_values()


if __name__ == "__main__":
    unittest.main()
