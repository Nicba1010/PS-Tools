from binascii import hexlify
from typing import IO

from base import LoggingClass
from base.utils import constant_check
from utils.utils import read_u32, Endianess, read_u16


class UnknownDataInfo(LoggingClass):

    def __init__(self, f: IO):
        super().__init__()
        self.f: IO = f

        self.unknown_data_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Unknown Data Offset: {self.unknown_data_offset}")

        self.unknown_data_size: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Unknown Data Size: {self.unknown_data_size}")

        self.unknown: bytes = f.read(0x20)
        self.logger.info(f'Unknown: {hexlify(self.unknown)}')

        self.sha_256_hash: bytes = f.read(0x20)
        self.logger.info(f'SHA-256 Hash: {hexlify(self.sha_256_hash)}')
