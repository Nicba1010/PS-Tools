from aenum import Enum


class DataType(Enum):
    UTF8_SPECIAL = bytes([0x04, 0x00])
    UTF8 = bytes([0x04, 0x02])
    INT32 = bytes([0x04, 0x04])
