from binascii import hexlify
from typing import IO

from base import LoggingClass
from base.utils import constant_check
from utils.utils import read_u32, Endianess


class SELFInfo(LoggingClass):

    def __init__(self, f: IO):
        super().__init__()
        self.f: IO = f

        self.self_info_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"SELF Info Offset: {self.self_info_offset}")

        self.self_info_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"SELF Info Size: {self.self_info_size}")

        self.unknown_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, "Unknown 1", self.unknown_1, 0x00)

        self.unknown_2: bytes = f.read(0x10)
        self.logger.info(f'Unknown 2: {hexlify(self.unknown_2)}')

        self.sha_256_hash: bytes = f.read(0x20)
        self.logger.info(f'SHA-256 Hash: {hexlify(self.sha_256_hash)}')
