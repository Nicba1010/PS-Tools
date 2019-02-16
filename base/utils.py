from logging import Logger
from typing import Any, List, Union

from .errors import InvalidFileConstantException


def constant_check(logger: Logger, name: str, constant: Any, valid: Union[Any, List[Any]]):
    if (constant in valid) if isinstance(valid, List) else constant == valid:
        logger.info(f'{name}: {constant}')
    else:
        raise InvalidFileConstantException(name, constant, valid)
