import logging
from functools import wraps

from .exceptions import ShelterError


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def log_operation(operation):
    def decorate(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                result = method(*args, **kwargs)
            except ShelterError as error:
                logger.warning("%s | ناموفق | %s", operation, type(error).__name__)
                raise

            logger.info("%s | موفق | %s", operation, result.name)
            return result

        return wrapper

    return decorate
