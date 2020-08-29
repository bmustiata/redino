import unittest
from typing import Set

import redino
from redino import RedinoSet
from tests.redino.test_shared import prepare_test


class TestModel(unittest.TestCase):
    """
    Tests if creating model works
    """

    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    @redino.connect
    def test_set(self):
        s = TestModel.create_test_set()

        try:
            self.assertEqual(3, len(s))
        finally:
            s.rd_delete()

    @redino.connect
    def test_contains(self):
        s = TestModel.create_test_set()

        try:
            self.assertTrue("b" in s)
            self.assertTrue("y" not in s)
        finally:
            s.rd_delete()

    @redino.connect
    def test_delete_and_iterator(self):
        s = TestModel.create_test_set()

        try:
            self.assertEqual(3, len(s))
            s.remove("b")

            self.assertEqual(2, len(s))
            self.assertEqual(
                {"a", "c"},
                set(s),
            )
        finally:
            s.rd_delete()

    @staticmethod
    def create_test_set() -> RedinoSet:
        s = RedinoSet(_type=Set[str], _id="testset").rd_persist()

        s.add("a")
        s.add("b")
        s += "c"

        return s
