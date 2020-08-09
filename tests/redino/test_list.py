import unittest
from typing import List

import redino


class TestList(unittest.TestCase):
    @redino.connect
    def test_list_append(self):
        l = self.create_test_list()

        self.assertEqual(3, len(l))

    @redino.connect
    def test_list_index(self):
        l = self.create_test_list()

        self.assertEqual("x", l[0])
        self.assertEqual("y", l[1])
        self.assertEqual("z", l[2])

    @redino.connect
    def test_remove_by_index(self):
        l = self.create_test_list()

        del l[1]

        self.assertEqual(2, len(l))
        self.assertEqual("x", l[0])
        self.assertEqual("z", l[1])

    def create_test_list(self):
        l = redino.RedinoList(
            _id="_testlist",
            _type=List[str],
        )
        l.clear()
        l.append("x")
        l.append("y")
        l += "z"

        return l
