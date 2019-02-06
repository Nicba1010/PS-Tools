import struct
from binascii import hexlify
from typing import IO, Generator

from base import LoggingClass
from utils.utils import read_u32, Endianess
from ..compression_type import CompressionType
from ..utils import psarc_zlib_multi_stream_unpack


class TOCEntry(LoggingClass):
    def __init__(self, f: IO):
        super().__init__()

        #: Name (read later after reading the name data)
        self.name: str = None

        #: 128-bit MD5 Name Digest
        self.hash: bytes = f.read(16)
        self.logger.debug(f'Hash: {hexlify(self.hash)}')

        #: Entry Block Index
        self.block_index: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f'Block Index: {self.block_index}')

        #: Entry Decompressed Size
        self.decompressed_size: int = struct.unpack('>Q', bytes([0, 0, 0]) + f.read(5))[0]
        self.logger.debug(f'Decompressed Size: {self.decompressed_size}')

        #: Entry Offset
        self.offset: int = struct.unpack('>Q', bytes([0, 0, 0]) + f.read(5))[0]
        self.logger.debug(f'Offset: {self.offset}')

    # TODO: Implement LZMA Decompression (And find an example file...)
    # noinspection PyUnusedLocal
    def get_decompression_stream(
            self, f: IO, block_size: int, compression_type: CompressionType
    ) -> Generator[bytes, None, None]:
        f.seek(self.offset)
        if f.read(1)[0] == 0x78:
            f.seek(self.offset)
            for data in psarc_zlib_multi_stream_unpack(f, self.decompressed_size, block_size):
                yield data
        else:
            f.seek(self.offset)
            bytes_remaining: int = self.decompressed_size
            while bytes_remaining != 0:
                to_read: int = block_size if bytes_remaining >= block_size else bytes_remaining
                data = f.read(to_read)
                yield data
                bytes_remaining -= len(data)

    def read_entry_data(self, f: IO, block_size: int, compression_type: CompressionType) -> bytearray:
        _data: bytearray = bytearray()
        for data in self.get_decompression_stream(f, block_size, compression_type):
            _data += data
        return _data
