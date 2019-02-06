from .constants import compressed_magic, uncompressed_magic


class InvalidISOException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidISOException, self).__init__(message)


class EmptyISOException(InvalidISOException):
    def __init__(self):
        super(EmptyISOException, self).__init__("ISO size shouldn't be 0 bytes.")


class InvalidISOMagicException(InvalidISOException):
    def __init__(self):
        super(InvalidISOMagicException, self).__init__(
            f'Invalid ISO magic. Should be "{compressed_magic}" or "{uncompressed_magic}".'
        )


class InvalidValueLSBMSBEncodeException(InvalidISOException):
    def __init__(self, lsb: int, msb: int):
        super(InvalidValueLSBMSBEncodeException, self).__init__(
            f'Invalid LSB-MSB encoded pair. LSB: {lsb}, MSB: {msb}'
        )


class InvalidStringEncodeException(InvalidISOException):
    def __init__(self, mode: str, string: str):
        super(InvalidStringEncodeException, self).__init__(
            f'String contains illegal character(s) for {mode} mode: {string}'
        )
