from aenum import Enum


class ArchivePathType(Enum):
    RELATIVE = 0x00
    IGNORE_CASE = 0x01
    ABSOLUTE = 0x02
    UNKNOWN = 0x03
