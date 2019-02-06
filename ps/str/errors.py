from .constants import magic


class InvalidSTRException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidSTRException, self).__init__(message)


class EmptySTRException(InvalidSTRException):
    def __init__(self):
        super(EmptySTRException, self).__init__("STR size shouldn't be 0 bytes.")


class InvalidSTRMagicException(InvalidSTRException):
    def __init__(self):
        super(InvalidSTRMagicException, self).__init__(
            f'Invalid STR magic. Should be "{magic}".'
        )
