from binascii import hexlify

from .constants import magic


class InvalidPFDException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidPFDException, self).__init__(message)


class EmptyPFDException(InvalidPFDException):
    def __init__(self):
        super(EmptyPFDException, self).__init__("PFD size shouldn't be 0 bytes.")


class InvalidPFDMagicException(InvalidPFDException):
    def __init__(self):
        super(InvalidPFDMagicException, self).__init__(
            f'Invalid PFD magic. Should be "{magic}".'
        )


class InvalidPFDVersionException(InvalidPFDException):
    def __init__(self):
        super(InvalidPFDVersionException, self).__init__(
            f'Invalid PFD version. Should be either 3 or 4.'
        )


class InvalidFieldException(InvalidPFDException):
    def __init__(self, field_name: str, value: bytes, correct_value: bytes):
        super(InvalidFieldException, self).__init__(
            f'Invalid field: {field_name}. Should be either {hexlify(value)} instead it is {hexlify(correct_value)}.'
        )
