import functools
from typing import Callable, TypeVar, Optional

import redino
import redino.redino_entity
from redino._redis_instance import _redis_thread_instance

T = TypeVar("T")


# The version means several things:
# "<unknown>"                 - if the setup() function was not yet called
# None                        - if the setup() function is actively running
# Any other non-empty string  - if the setup() was successful, with the active model version

VERSION_UKNOWN = "<unknown>"
dbversion = VERSION_UKNOWN


class RedinoModel(redino.redino_entity.Entity):
    """
    This is the persisted entity that holds the version
    """

    version: str


redino.redino_entity.Entity.attributes(
    RedinoModel,
    {
        "version": str,
    },
)


def _setup_connect(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        with redino._redis_pool().client() as redis_client:  # type: ignore
            try:
                _redis_thread_instance.instance = redis_client
                return f(*args, **kw)
            finally:
                _redis_thread_instance.instance = None

    return wrapper


@_setup_connect
def setup(*, migrate: Callable[[Optional[str]], None], version: str = "") -> None:
    """
    A function to allow migration of data from one
    format to another.
    """
    global dbversion

    if not version:
        raise Exception("version should be a non-empty string.")

    current_model_version = None

    redino_model = redino.redino_entity.Entity.fetch_first(RedinoModel)
    if redino_model:
        current_model_version = redino_model.version

    if current_model_version == version:
        dbversion = version
        return

    migrate(current_model_version)

    # if we don't have a model we'll create the model as well
    if not redino_model:
        redino_model = RedinoModel().rd_persist()

    redino_model.version = version
    dbversion = version
