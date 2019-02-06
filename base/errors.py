class InvalidFileException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidFileException, self).__init__(message)


class EmptyFileException(InvalidFileException):
    def __init__(self):
        super(EmptyFileException, self).__init__("File size shouldn't be 0 bytes.")
