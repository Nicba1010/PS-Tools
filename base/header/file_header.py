from typing import IO

from ..logging_class import LoggingClass


# noinspection PyUnusedLocal
class FileHeader(LoggingClass):
    def __init__(self, f: IO):
        super().__init__()
