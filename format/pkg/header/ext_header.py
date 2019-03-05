from typing import IO

from base.header import MagicFileHeader
from base.utils import constant_check
from format.pkg.key_id import PkgKeyID
from utils.utils import read_u32, read_u64, Endianess


class PkgExtHeader(MagicFileHeader):
    def __init__(self, f: IO):
        super().__init__(f)

        #: TODO: Find what this unknown field is
        self.unknown_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, 'Unknown 1', self.unknown_1, 1)

        #: Header size
        self.header_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Header Size: {self.header_size}')

        #: Data size
        self.data_size: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Data Size: {self.data_size}')

        #: Main and EXT Headers HMAC offset TODO: Check this validity
        self.main_and_ext_headers_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Main and Ext Headers HMAC Offset: {self.main_and_ext_headers_hmac_offset}')

        #: Metadata Header HMAC offset TODO: Check this validity
        self.metadata_header_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Metadata Header HMAC Offset: {self.metadata_header_hmac_offset}')

        #: Tail offset
        self.tail_offset: int = read_u64(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Tail Offset: {self.tail_offset}')

        #: Just padding probably
        self.padding_1: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        constant_check(self.logger, 'Padding 1', self.padding_1, 0)

        #: PKG Key ID
        self.pkg_key_id: PkgKeyID = PkgKeyID(read_u32(f, endianess=Endianess.BIG_ENDIAN))
        self.logger.info(f'PKG Key ID: {self.pkg_key_id}')

        #: Full Header HMAC offset TODO: Check this validity
        self.full_header_hmac_offset: int = read_u32(f, endianess=Endianess.BIG_ENDIAN)
        self.logger.info(f'Full Header HMAC Offset: {self.full_header_hmac_offset}')

        #: Just padding
        self.padding_2: bytes = f.read(0x14)
        constant_check(self.logger, 'Padding 2', self.padding_2, bytes([0x00] * 0x14))

    @property
    def magic(self) -> bytes:
        return b'\x7fext'
