from aenum import Enum


class CompressionType(Enum):
    ZLIB = b'zlib'
    LZMA = b'lzma'
