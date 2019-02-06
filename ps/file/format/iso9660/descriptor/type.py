from aenum import Enum


class DescriptorType(Enum):
    BOOT_RECORD = 0x00
    PRIMARY = 0x01
    SUPPLEMENTARY = 0x02
    PARTITION = 0x03
    TERMINATOR = 0xFF
