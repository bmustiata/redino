from typing import Optional
import unittest

import redino.model

import redino.model
import redino._redis_instance

test = unittest.TestCase()

#
# Since we're enforcing the redino.model.setup() call, we need
# to ensure that in-between tests everything is nuked, and
# the model has a correct version.
#


def empty_redino_model_setup(version: Optional[str]):
    test.assertIsNone(version)


@redino.model._setup_connect
def destroy_all_data():
    redino._redis_instance.redis_instance().flushall()
    redino.model.dbversion = redino.model.VERSION_UKNOWN  # the setup was not yet called


def prepare_test():
    destroy_all_data()
    redino.model.setup(version="1", migrate=empty_redino_model_setup)
