import logging
from abc import ABC


class LoggingClass(ABC):
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(self.logger_name)

    @property
    def logger_name(self) -> str:
        return self.__create_logger_name_from_class_name()

    def __create_logger_name_from_class_name(self) -> str:
        class_name: str = self.__class__.__name__
        logger_name: str = ""
        for i in range(len(class_name)):
            logger_name += class_name[i]
            if i + 2 < len(class_name) and class_name[i + 1].isupper() and class_name[i + 2].islower():
                logger_name += " "
        return logger_name
