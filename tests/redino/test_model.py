import unittest
from typing import Dict, Set, List

import redino
from tests.redino.test_shared import prepare_test


class Item(redino.Entity):
    name: str
    count: int
    d: Dict[int, int]
    s: Set[str]
    l: List[int]

    attr = {
        "name": str,
        "count": int,
        "d": Dict[int, int],
        "s": Set[str],
        "l": List[int],
    }


class TestModel(unittest.TestCase):
    """
    Tests if creating model works
    """

    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    def test_model(self):
        """
        Tests a model creation
        """

        @redino.connect
        def clear_values():
            for it in redino.Entity.fetch_all(Item):
                if it.d:
                    it.d.rd_delete()

                if it.s:
                    it.s.rd_delete()

                if it.l:
                    it.l.rd_delete()

                it.rd_delete()

        @redino.connect
        @redino.transactional
        def set_values():
            item = Item().rd_persist()
            item.name = "wut"
            item.count = 5

        @redino.connect
        def read_values():
            items: List[Item] = redino.Entity.fetch_all(Item)
            self.assertEqual(1, len(items))

            self.assertEqual("wut", items[0].name)
            self.assertTrue(isinstance(items[0].name, str))
            self.assertEqual(5, items[0].count)
            self.assertTrue(isinstance(items[0].count, int))

        try:
            clear_values()
            set_values()
            read_values()
        finally:
            clear_values()


if __name__ == "__main__":
    unittest.main()
