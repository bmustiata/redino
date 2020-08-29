import unittest
from typing import Optional, List

import redino
from redino import Entity
from tests.redino.test_shared import prepare_test


class Folder(redino.Entity):
    parent: Optional["Folder"]
    name: str
    folders: List["Folder"]
    files: List["File"]

    def rd_delete(self) -> None:
        if self.folders:
            for folder in self.folders:
                folder.rd_delete()

            self.folders.clear()

        # we call the remove of the parent after all the other removes
        super(Folder, self).rd_delete()


class File(redino.Entity):
    parent: Folder
    name: str
    content: str


Entity.attributes(
    Folder,
    {
        "parent": Folder,
        "name": str,
        "folders": List[Folder],
        "files": List[File],
    },
)


Entity.attributes(
    File,
    {
        "parent": Folder,
        "name": str,
        "content": str,
    },
)


def create_folder(name: str, _id: Optional[str] = None) -> Folder:
    result = Folder(_id=_id).rd_persist()
    result.name = name

    return result


class TestMultipleEntities(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        prepare_test()

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

        @redino.connect
        def cleanup_data() -> None:
            Folder(_id="test").rd_delete()

        try:
            create_data()
            validate_data()
        finally:
            cleanup_data()


if __name__ == "__main__":
    unittest.main()
