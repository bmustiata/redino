import unittest
import uuid
from typing import Dict

import redino
from redino.redino_dict import RedinoDict
from tests.redino.test_shared import prepare_test


class TestDictionary(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    @redino.connect
    def test_dict_items(self):
        d = TestDictionary.create_dictionary()
        try:
            index = 0
            for k, v in d.items():
                if index == 0:
                    self.assertEqual("x", k)
                    self.assertEqual("a", v)
                elif index == 1:
                    self.assertEqual("y", k)
                    self.assertEqual("b", v)
                elif index == 2:
                    self.assertEqual("z", k)
                    self.assertEqual("c", v)
                elif index == 3:
                    raise Exception("There should be only 3 items")

                index += 1
        finally:
            d.rd_delete()

    def test_large_items(self):
        created_dict = dict()
        control_dict = dict()

        @redino.connect
        def create_large_dict():
            d = RedinoDict(_id="testdictlarge", _type=Dict[str, str]).rd_persist()

            for i in range(1000):
                key = str(uuid.uuid4())
                value = str(uuid.uuid4())

                created_dict[key] = value
                d[key] = value

        @redino.connect
        def read_dictionary():
            d = RedinoDict(_id="testdictlarge", _type=Dict[str, str])

            for k, v in d.items():
                control_dict[k] = v

        @redino.connect
        def delete_dict():
            RedinoDict(_id="testdictlarge", _type=Dict[str, str]).rd_delete()

        try:
            create_large_dict()
            read_dictionary()

            self.assertEqual(created_dict, control_dict)
        finally:
            delete_dict()

    @redino.connect
    def test_contains(self):
        d = TestDictionary.create_dictionary()

        try:
            self.assertTrue("x" in d)
            self.assertTrue("a" not in d)
        finally:
            d.rd_delete()

    @redino.connect
    def test_values_iterator(self):
        d = TestDictionary.create_dictionary()

        try:
            self.assertEqual({"a", "b", "c"}, set(d.values()))
        finally:
            d.rd_delete()

    @redino.connect
    def test_keys_iterator(self):
        d = TestDictionary.create_dictionary()

        try:
            self.assertEqual({"x", "y", "z"}, set(d.keys()))
        finally:
            d.rd_delete()

    @redino.connect
    def test_delete_item(self):
        d = TestDictionary.create_dictionary()

        try:
            del d["y"]

            self.assertEqual({"x", "z"}, set(d.keys()))
        finally:
            d.rd_delete()

    @redino.connect
    def test_len(self):
        d = TestDictionary.create_dictionary()

        try:
            self.assertEqual(3, len(d))
        finally:
            d.rd_delete()

    @staticmethod
    def create_dictionary() -> RedinoDict:
        d = RedinoDict(_id="testdict", _type=Dict[str, str]).rd_persist()

        d["x"] = "a"
        d["y"] = "b"
        d["z"] = "c"

        return d
