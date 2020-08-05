import unittest
from typing import Dict, Set, List

import redis

import redino


class Item(redino.Entity):
    name: str
    count: int
    d: Dict[int, int]
    s: Set[str]
    l: List[int]

    attr = {
        "name": str,
        "count": int,
        "d": (dict, int, int),
        "s": (set, str),
        "l": (list, int),
    }


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
            item = Item(redis=r).persist()
            item.name = "wut"
            item.count = 5

        @redino.connect
        def read_values(r: redis.client.Redis):
            items: List[Item] = redino.Entity.fetch_all(redis=r, type=Item)
            self.assertEqual(1, len(items))

            self.assertEqual("wut", items[0].name)
            self.assertTrue(isinstance(items[0].name, str))
            self.assertEqual(5, items[0].count)
            self.assertTrue(isinstance(items[0].count, int))

        clear_values()
        set_values()
        read_values()


if __name__ == '__main__':
    unittest.main()
