from .constants import compressed_magic, uncompressed_magic


class InvalidIRDException(Exception):
    def __init__(self, message: str = ""):
        super(InvalidIRDException, self).__init__(message)


class EmptyIRDException(InvalidIRDException):
    def __init__(self):
        super(EmptyIRDException, self).__init__("IRD size shouldn't be 0 bytes.")


class InvalidIRDMagicException(InvalidIRDException):
    def __init__(self):
        super(InvalidIRDMagicException, self).__init__(
            f'Invalid IRD magic. Should be "{compressed_magic}" or "{uncompressed_magic}".'
        )


class InvalidIRDCRCException(InvalidIRDException):
    def __init__(self):
        super(InvalidIRDCRCException, self).__init__(
            f'IRD CRC doesn\'t match declared CRC.'
        )
