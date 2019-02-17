from binascii import hexlify
from typing import IO

from base import LoggingClass
from base.utils import constant_check
from utils.utils import read_u32, Endianess, read_u16


class EntiretyInfo(LoggingClass):

    def __init__(self, f: IO):
        super().__init__()
        self.f: IO = f

        self.entirety_data_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Entirety Data Offset: {self.entirety_data_offset}")

        self.entirety_data_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Entirety Data Size: {self.entirety_data_size}")

        self.flags: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Flags: {hex(self.flags)}")

        self.unk_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, "Unknown 1", self.unk_1, 0x00)

        self.unk_2: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Unknown 2: {self.unk_2}')

        self.unk_3: bytes = f.read(0x8)
        self.logger.info(f'Unknown 3: {hexlify(self.unk_3)}')

        self.sha_256_hash: bytes = f.read(0x20)
        self.logger.info(f'SHA-256 Hash: {hexlify(self.sha_256_hash)}')
