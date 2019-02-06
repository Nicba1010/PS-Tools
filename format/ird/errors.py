from base.errors import InvalidFileException


class InvalidIRDCRCException(InvalidFileException):
    def __init__(self):
        super(InvalidIRDCRCException, self).__init__(
            f'IRD CRC doesn\'t match declared CRC.'
        )
