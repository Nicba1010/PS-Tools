from abc import abstractmethod
from typing import IO

from .errors import InvalidMagicException
from .file_header import FileHeader


class MagicFileHeader(FileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        #: Magic
        self._magic: bytes = f.read(self.__magic_length)
        self.logger.info(f'Magic: {self._magic}')

        if self._magic != self.magic:
            self.logger.error('Error, invalid magic')
            raise InvalidMagicException(self.magic)
        else:
            self.logger.info('Magic Verified')

    @property
    @abstractmethod
    def magic(self) -> bytes:
        pass

    @property
    def __magic_length(self) -> int:
        return len(self.magic)
