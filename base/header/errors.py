from binascii import hexlify

from ..errors import InvalidFileException


class InvalidMagicException(InvalidFileException):
    def __init__(self, magic: bytes):
        super(InvalidMagicException, self).__init__(
            f'Invalid file magic. Should be "{hexlify(magic)}".'
        )
