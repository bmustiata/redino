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
    "folders": (list, Folder),
    "files": (list, File),
}

File.attr = {
    "parent": Folder,
    "name": str,
    "content": str,
}


class TestMultipleEntities(unittest.TestCase):
    def test_model(self):
        @redino.connect
        def create_data() -> None:
            tests = Folder().persist()
            tests.name = "tests"
            tests.folders = []

        create_data()


if __name__ == '__main__':
    unittest.main()
