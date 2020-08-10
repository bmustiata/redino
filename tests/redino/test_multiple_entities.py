import unittest
from typing import Optional, List

import redis

import redino


class Folder(redino.Entity):
    parent: Optional['Folder']
    name: str
    folders: List['Folder']
    files: List['File']


class File(redino.Entity):
    parent: Folder
    name: str
    content: str


Folder.attr = {
    "parent": Folder,
    "name": str,
    "folders": List[Folder],
    "files": List[File],
}

File.attr = {
    "parent": Folder,
    "name": str,
    "content": str,
}


def create_folder(name: str, _id: Optional[str] = None) -> Folder:
    result = Folder(_id=_id).rd_persist()
    result.name = name

    return result


class TestMultipleEntities(unittest.TestCase):
    def test_model(self):
        @redino.connect
        def create_data() -> None:
            tests = create_folder("tests", _id="test")
            tests.folders = [
                create_folder("a"),
                create_folder("b"),
            ]

        @redino.connect
        def validate_data() -> None:
            tests = Folder(_id="test")

            self.assertEqual("tests", tests.name)
            self.assertEqual(2, len(tests.folders))
            self.assertEqual("a", tests.folders[0].name)
            self.assertEqual("b", tests.folders[1].name)

        create_data()
        validate_data()


if __name__ == '__main__':
    unittest.main()
