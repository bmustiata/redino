import unittest

import redino
from tests.redino.test_shared import prepare_test


class MigratedItem(redino.Entity):
    data: str


redino.Entity.attributes(MigratedItem, {"data": str})


class TestMigration(unittest.TestCase):
    """
    Tests if creating model works
    """

    def test_migration(self) -> None:
        # we simulate a cold start, but with already some data
        # inside
        prepare_test()

        @redino.connect
        @redino.transactional
        def persist_an_item():
            item = MigratedItem().rd_persist()
            item.data = "test data"

        persist_an_item()

        # now here goes the cold start
        redino.model.dbversion = redino.model.VERSION_UKNOWN

        # we need to call the redino.model.setup before any
        # redino operations
        @redino.connect
        def read_migrated_item():
            items = redino.Entity.fetch_all(MigratedItem)
            self.assertTrue(items)
            self.assertEqual(1, len(items))
            self.assertEqual("test data", items[0].data)

        read_failed = True
        try:
            read_migrated_item()
            read_failed = False
        except Exception:
            pass

        self.assertTrue(read_failed)

        # we should already have some version inside it, so we
        # ensure that the migration is the previous version
        def migration_check(version):
            self.assertEqual("1", version)

        redino.model.setup(version="2.custom", migrate=migration_check)

        read_migrated_item()

        @redino.connect
        def check_version_data():
            model_definitions = redino.Entity.fetch_all(redino.model.RedinoModel)
            self.assertTrue(model_definitions)
            self.assertEqual(1, len(model_definitions))
            self.assertEqual("2.custom", model_definitions[0].version)

        check_version_data()
