import functools
import unittest
from typing import List, TypeVar, Callable, Dict, Set

import redino
from redino import RedinoSet
from redino.data_converter import DataConverter
from tests.redino.test_shared import prepare_test

T = TypeVar("T")


def expect_fail(f: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> None:
        is_failed = False

        try:
            f(*args, **kw)
        except Exception as e:
            is_failed = True

        if not is_failed:
            raise Exception("Code didn't fail as expected")

    return wrapper


class TestDataConverter(unittest.TestCase):
    """
    Tests if conversion handles correctly
    """

    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

    @redino.connect
    def test_nested_lists(self):
        t = List[List[str]]
        converter = DataConverter(t)

        # create a nested redino list of items
        l = converter.from_data([[]])

        self.assertEqual(1, len(l))
        self.assertEqual(0, len(l[0]))

        @expect_fail
        def assign_wrong_type_str_to_list_fails():
            l.append("abc")

        assign_wrong_type_str_to_list_fails()

        @expect_fail
        def assign_wrong_type_list_to_str_fails():
            l[0].append([])

        assign_wrong_type_list_to_str_fails()

    @redino.connect
    def test_dictionaries(self):
        t = Dict[str, Dict[str, str]]
        converter = DataConverter(t)

        # create a nested redino list of items
        d = converter.from_data(
            {
                "x": {
                    "y": "abc",
                    "z": "123",
                }
            }
        )

        self.assertTrue(1, len(d))
        self.assertTrue(2, len(d["x"]))

        @expect_fail
        def assign_wrong_type_on_keys_should_fail():
            d[3] = {"a": "b"}

        assign_wrong_type_on_keys_should_fail()

        @expect_fail
        def assign_wrong_type_on_values_should_fail():
            d["a"] = {"a", "b"}  # this is a set, not a dict

        assign_wrong_type_on_values_should_fail()

    @redino.connect
    def test_set_assignment(self):
        t = Set[str]
        converter = DataConverter(t)

        # create a nested redino list of items
        s = converter.from_data({"a", "b", "c"})

        self.assertTrue(isinstance(s, RedinoSet))
        self.assertEqual(3, len(s))

        s.add("d")
        self.assertEqual(4, len(s))

        @expect_fail
        def assign_wrong_type_on_set_should_fail():
            s.add(3)

        assign_wrong_type_on_set_should_fail()


if __name__ == "__main__":
    unittest.main()
