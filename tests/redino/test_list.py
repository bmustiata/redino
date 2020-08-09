import unittest
from typing import List

import redino


class TestList(unittest.TestCase):
    @redino.connect
    def test_list_len(self):
        l = self.create_test_list()

        try:
            self.assertEqual(3, len(l))
        finally:
            l.delete()

    @redino.connect
    def test_list_index(self):
        l = self.create_test_list()
        try:
            self.assertEqual("x", l[0])
            self.assertEqual("y", l[1])
            self.assertEqual("z", l[2])
        finally:
            l.delete()

    @redino.connect
    def test_remove_by_index(self):
        l = self.create_test_list()
        try:
            del l[1]

            self.assertEqual(2, len(l))
            self.assertEqual("x", l[0])
            self.assertEqual("z", l[1])
        finally:
            l.delete()

    @redino.connect
    def test_contains(self):
        l = self.create_test_list()
        try:
            self.assertTrue("y" in l)
            self.assertTrue("b" not in l)
        finally:
            l.delete()

    @redino.connect
    def test_clear(self):
        l = self.create_test_list()
        try:
            self.assertEqual(3, len(l))
            l.clear()
            self.assertEqual(0, len(l))
        finally:
            l.delete()

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
