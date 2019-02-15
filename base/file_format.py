import os
from typing import IO, TypeVar, Generic, Type

from .errors import EmptyFileException, InvalidFileHashException
from .header import MagicFileHeader
from .logging_class import LoggingClass


class FileFormat(LoggingClass):

    def __init__(self, path: str, verify: bool = False):
        super().__init__()

        #: File Path
        self.path: str = path
        self.logger.info(f'Parsing file: {self.path}')

        if os.stat(self.path).st_size == 0:
            raise EmptyFileException()

        #: File Handle
        self.file_handle: IO = self.get_file_handle()

        #: File hash verification
        if verify:
            if self.verify_hash():
                self.logger.info('File Hash Verified!')
            else:
                raise InvalidFileHashException()

    def get_file_handle(self) -> IO:
        return open(self.path, 'rb')

    # noinspection PyMethodMayBeStatic
    def verify_hash(self) -> bool:
        return True

    def __del__(self):
        self.logger.debug('Cleaning up...')
        if not self.file_handle.closed:
            self.file_handle.close()


T = TypeVar('T', bound=MagicFileHeader)


class FileFormatWithMagic(FileFormat, Generic[T]):

    def __init__(self, path: str, header_class: Type[T], verify: bool = False):
        super().__init__(path, verify)
        self.__header_class = header_class
        self.__header = self.__header_class(self.file_handle)

    @property
    def header(self) -> T:
        return self.__header
