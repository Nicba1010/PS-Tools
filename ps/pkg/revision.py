from aenum import Enum


class PkgRevision(Enum):
    RETAIL = bytes([0x80, 0x00])
    DEBUG = bytes([0x00, 0x00])