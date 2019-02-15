class InvalidFileException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidFileException, self).__init__(message)


class EmptyFileException(InvalidFileException):
    def __init__(self):
        super(EmptyFileException, self).__init__("File size shouldn't be 0 bytes.")


class InvalidFileHashException(InvalidFileException):
    def __init__(self):
        super(InvalidFileHashException, self).__init__("File hash doesn't match declared hash.")
