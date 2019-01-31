from .constants import magic


class InvalidEDATException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidEDATException, self).__init__(message)


class EmptyEDATException(InvalidEDATException):
    def __init__(self):
        super(EmptyEDATException, self).__init__("EDAT size shouldn't be 0 bytes.")


class InvalidEDATMagicException(InvalidEDATException):
    def __init__(self):
        super(InvalidEDATMagicException, self).__init__(
            f'Invalid EDAT magic. Should be "{magic}".'
        )


class InvalidEDATBlockSizeException(InvalidEDATException):
    def __init__(self):
        super(InvalidEDATBlockSizeException, self).__init__(
            f'Invalid EDAT block size. Should be less than or equal to 0x8000.'
        )
