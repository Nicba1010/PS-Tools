from binascii import hexlify
from typing import IO

from base import LoggingClass
from base.utils import constant_check
from utils.utils import read_u32, Endianess, read_u16


class SFOInfo(LoggingClass):

    def __init__(self, f: IO):
        super().__init__()
        self.f: IO = f

        self.param_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Param Offset: {self.param_offset}")

        self.param_size: int = read_u16(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Param Size: {self.param_size}")

        self.unknown_int: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"Unknown Int: {self.unknown_int}")

        #: May be PSP2_SYSTEM_VER
        self.psp2_disp_version: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.debug(f"PSP 2 Disp Version: {self.unknown_int}")

        self.unknown: bytes = f.read(0x08)
        constant_check(self.logger, "Unknown", self.unknown, bytes([0x00] * 8))

        self.sha_256_hash: bytes = f.read(0x20)
        self.logger.info(f'SHA-256 Hash: {hexlify(self.sha_256_hash)}')
