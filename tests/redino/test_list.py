import unittest
from typing import List

import redino
from tests.redino.test_shared import prepare_test


class TestList(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    @redino.connect
    def test_list_len(self):
        l = self.create_test_list()

        try:
            self.assertEqual(3, len(l))
        finally:
            l.rd_delete()

    @redino.connect
    def test_list_index(self):
        l = self.create_test_list()
        try:
            self.assertEqual("x", l[0])
            self.assertEqual("y", l[1])
            self.assertEqual("z", l[2])
        finally:
            l.rd_delete()

    @redino.connect
    def test_remove_by_index(self):
        l = self.create_test_list()
        try:
            del l[1]

            self.assertEqual(2, len(l))
            self.assertEqual("x", l[0])
            self.assertEqual("z", l[1])
        finally:
            l.rd_delete()

    @redino.connect
    def test_contains(self):
        l = self.create_test_list()
        try:
            self.assertTrue("y" in l)
            self.assertTrue("b" not in l)
        finally:
            l.rd_delete()

    @redino.connect
    def test_clear(self):
        l = self.create_test_list()
        try:
            self.assertEqual(3, len(l))
            l.clear()
            self.assertEqual(0, len(l))
        finally:
            l.rd_delete()

    @redino.connect
    def test_iteration(self):
        l = self.create_test_list()
        try:
            for f in l:
                print(f)
        finally:
            l.rd_delete()

    @redino.connect
    def test_left_right_push(self):
        l = self.create_test_list()
        try:
            l.clear()
            l.right_push("b")
            l.right_push("c")
            l.left_push("a")

            self.assertEqual(3, len(l))
            self.assertEqual("a", l[0])
            self.assertEqual("b", l[1])
            self.assertEqual("c", l[2])

            self.assertEqual("a", l.left_pop())
            self.assertEqual("c", l.right_pop())

            self.assertEqual(1, len(l))
            self.assertEqual("b", l[0])
        finally:
            l.rd_delete()

    def create_test_list(self):
        l = redino.RedinoList(
            _id="_testlist",
            _type=List[str],
        ).rd_persist()

        l.clear()

        l.append("x")
        l.append("y")
        l += "z"

        return l
