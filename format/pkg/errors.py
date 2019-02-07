from binascii import hexlify
from typing import List


class InvalidPKGException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidPKGException, self).__init__(message)


class EmptyPKGException(InvalidPKGException):
    def __init__(self):
        super(EmptyPKGException, self).__init__("PKG size shouldn't be 0 bytes.")


class InvalidPKGHeaderHashException(InvalidPKGException):
    def __init__(self):
        super(InvalidPKGHeaderHashException, self).__init__("PKG header SHA1 hash doesn't match declared SHA1 hash.")


class InvalidPKGHashException(InvalidPKGException):
    def __init__(self):
        super(InvalidPKGHashException, self).__init__("PKG SHA1 hash doesn't match declared SHA1 hash.")


class InvalidPKGMetadataException(InvalidPKGException):
    def __init__(self, data: bytes, valid_sizes: List[bytes]):
        super(InvalidPKGMetadataException, self).__init__("Invalid Metadata Data! Is {} should be {}!".format(
            hexlify(data).decode('UTF-8'),
            '/'.join([hexlify(x).decode('UTF-8') for x in valid_sizes])
        ))


class InvalidPKGMetadataSizeException(InvalidPKGException):
    def __init__(self, data_size: int, valid_sizes: List[int]):
        super(InvalidPKGMetadataSizeException, self).__init__("Invalid Metadata Data Size! Is {} should be {}!".format(
            data_size,
            '/'.join([hex(x) for x in valid_sizes])
        ))
