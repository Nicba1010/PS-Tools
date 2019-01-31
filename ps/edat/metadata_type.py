from aenum import MultiValueEnum


class MetadataType(MultiValueEnum):
    DEFAULT = 0x00
    COMPRESSED = 0x01, 0x05
    PLAINTEXT = 0x02, 0x06
    COMPRESSED_PLAINTEXT = 0x03, 0x07
    UNKNOWN = 0x0C
    COMPRESSED_DATA = 0x0D
    DATA_MISC = 0x3C
