from .constants import magic


class InvalidSFOException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidSFOException, self).__init__(message)


class EmptySFOException(InvalidSFOException):
    def __init__(self):
        super(EmptySFOException, self).__init__("SFO size shouldn't be 0 bytes.")


class InvalidSFOMagicException(InvalidSFOException):
    def __init__(self):
        super(InvalidSFOMagicException, self).__init__(
            f'Invalid SFO magic. Should be "{magic}".'
        )
