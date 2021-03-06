from aenum import Enum


class DataType(Enum):
    UTF8_SPECIAL = bytes([0x04, 0x00])
    UTF8 = bytes([0x04, 0x02])
    INT32 = bytes([0x04, 0x04])
    PARAM = bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF])
