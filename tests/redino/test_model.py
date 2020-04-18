import unittest

import redis
from redino import model, transactional, redis_connect


@model("report")
class TestReport:
    def __init__(self) -> None:
        self.name = ""
        self.status = "pass"


class TestModel(unittest.TestCase):
    """
    Test the model if it can create entries in redis
    """
    @redis_connect
    @transactional
    def test_model_creation(redis: redis.Redis, self):
        """
        yay
        """
        print(f"self is {self} and redis is {redis}")
        redis.hset("a", "key", "3")
        redis.hset("b", "key", "3")



if __name__ == '__main__':
    unittest.main()
