import unittest

import redis

import redino


class Item(redino.Entity):
    def __init__(self,
                 *,
                 redis: redis.client.Redis,
                 **kw) -> None:
        super(Item, self).__init__(redis=redis, **kw)


class TestModel(unittest.TestCase):
    """
    Tests if creating model works
    """
    def test_model(self):
        """
        Tests a model creation
        """
        @redino.connect
        def clear_values(r: redis.client.Redis):
            for it in redino.Entity.fetch_all(redis=r, type=Item):
                it.delete()

        @redino.connect
        @redino.transactional
        def set_values(r: redis.client.Redis):
            item = Item(redis=r)
            item.name = "wut"

        @redino.connect
        def read_values(r: redis.client.Redis):
            items = redino.Entity.fetch_all(redis=r, type=Item)
            self.assertEqual(1, len(items))
            self.assertEqual("wut", items[0].name)

        clear_values()
        set_values()
        read_values()


if __name__ == '__main__':
    unittest.main()
