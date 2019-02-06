from .constants import magic


class InvalidPSARCException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidPSARCException, self).__init__(message)


class EmptyPSARCException(InvalidPSARCException):
    def __init__(self):
        super(EmptyPSARCException, self).__init__("PSARC size shouldn't be 0 bytes.")


class InvalidPSARCMagicException(InvalidPSARCException):
    def __init__(self):
        super(InvalidPSARCMagicException, self).__init__(
            f'Invalid PSARC magic. Should be "{magic}".'
        )
