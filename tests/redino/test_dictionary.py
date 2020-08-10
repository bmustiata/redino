import unittest
from typing import Dict

import redino
from redino.redino_dict import RedinoDict


class TestList(unittest.TestCase):
    @redino.connect
    def test_dict_items(self):
        d = self.create_dictionary()
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

    def create_dictionary(self) -> RedinoDict:
        d = RedinoDict(
            _id="testdict",
            _type=Dict[str, str]).rd_persist()

        d["x"] = "a"
        d["y"] = "b"
        d["z"] = "c"

        return d

